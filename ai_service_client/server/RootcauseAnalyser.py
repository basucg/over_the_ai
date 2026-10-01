#!/usr/bin/env python3
import io
import json
import logging
import os
import re
import tarfile
import zipfile
from functools import lru_cache
from pathlib import Path
from string import Template
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from ModelConnector import AIModelClient

if TYPE_CHECKING:
    from UpdateAgent import ServerConfig

logger = logging.getLogger("AIRootCauseAnalyser")

# Constants from ai_server.py
PROCESS_LOG_HEADER = "\nPROCESS LOG EXCERPTS:\n"
NO_PROCESS_LOGS_TEXT = "\nPROCESS LOGS: (No log archive received yet)\n"
DEFAULT_PROMPT_TEMPLATE_PATH = Path(__file__).resolve().parent / "prompts" / "slm_prompt.txt"
OTA_PROMPT_TEMPLATE_PATH = Path(__file__).resolve().parent / "prompts" / "ota_prompt.txt"
OTA_RELEVANT_LINE = re.compile(r"ERROR|FAIL|[Ff]ailed|shouldRetry|WILL_RETRY|otaState|DNLD|ERC_|timed out|[Ii]nterrupt|\sE/")
# Lines the OTA instruction files point to; kept first when a log exceeds the cap.
OTA_PRIORITY_LINE = re.compile(r"DMA_VAR_ERROR|STSTRK_VAR_VDM_ERROR|ERC_ERROR_RESULT_CODE|\[Core_DL\]\[ERROR\]|shouldRetry|WILL_RETRY|DNLD_FAILURE: error|otaState")
OTA_MAX_LINES_PER_LOG = 30
OTA_FALLBACK_TAIL_LINES = 40
ERROR_CONFIG_PATH = Path(__file__).resolve().parent / "errorconfig.aidl"

class RootCauseAnalyser:
    def __init__(self, config: "ServerConfig", aimodel_client: AIModelClient):
        self._config = config
        self._aimodel_client = aimodel_client
        self._template = self._load_template(DEFAULT_PROMPT_TEMPLATE_PATH)
        self._ota_template = self._load_ota_template()

    async def analyse_ota(
        self,
        instructions: Optional[str],
        error_event: Dict[str, Any],
        recent_history: List[Dict[str, Any]],
        process_logs: Optional[Dict[str, str]],
    ) -> str:
        prompt = self._build_prompt(
            instructions, error_event, recent_history, self._filter_ota_logs(process_logs), self._ota_template
        )
        return await self._aimodel_client.request_analysis(prompt, len(recent_history), log_process_logs=False)

    @staticmethod
    def _filter_ota_logs(process_logs: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
        if not process_logs:
            return process_logs

        filtered: Dict[str, str] = {}
        for log_name, log_text in process_logs.items():
            lines = str(log_text).splitlines()
            seen = set()
            kept: List[str] = []
            for line in lines:
                if not OTA_RELEVANT_LINE.search(line):
                    continue
                # Drop the leading date/time so repeated messages collapse.
                key = re.sub(r"^\S+\s+\S+\s+", "", line)
                if key in seen:
                    continue
                seen.add(key)
                kept.append(line)
            selected = (
                RootCauseAnalyser._cap_ota_lines(kept) if kept else lines[-OTA_FALLBACK_TAIL_LINES:]
            )
            filtered[log_name] = "\n".join(selected) or "(Empty log file)"
        return filtered

    @staticmethod
    def _cap_ota_lines(kept: List[str]) -> List[str]:
        if len(kept) <= OTA_MAX_LINES_PER_LOG:
            return kept

        chosen = {i for i, line in enumerate(kept) if OTA_PRIORITY_LINE.search(line)}
        chosen = set(sorted(chosen)[-OTA_MAX_LINES_PER_LOG:])
        for i in range(len(kept) - 1, -1, -1):
            if len(chosen) >= OTA_MAX_LINES_PER_LOG:
                break
            chosen.add(i)
        return [kept[i] for i in sorted(chosen)]

    async def analyse(
        self,
        instructions: Optional[str],
        error_event: Dict[str, Any],
        recent_history: List[Dict[str, Any]],
        process_logs: Optional[Dict[str, str]],
    ) -> str:
        prompt = self._build_prompt(
            instructions,
            error_event,
            recent_history,
            process_logs,
        )
        #print("*********")
        ##print(prompt)
        #print("*********")
        report_text = await self._aimodel_client.request_analysis(prompt, len(recent_history))
        return self._enforce_report_error_code(report_text, process_logs)

    def _build_prompt(
        self,
        instructions: Optional[str],
        error_event: Dict[str, Any],
        recent_history: List[Dict[str, Any]],
        process_logs: Optional[Dict[str, str]],
        template: Optional[str] = None,
    ) -> str:
        values = {
            "client_instructions": self._format_client_instructions(instructions),
            "failure_event": json.dumps(self.summarize_event(error_event), indent=2),
            "recent_history": json.dumps(
                [self.summarize_event(event) for event in recent_history[-self._config.aimodel_history_events :]],
                indent=2,
            ),
            "process_logs": self._format_process_logs(process_logs),
        }
        return Template(template or self._template).safe_substitute(values)

    @staticmethod
    def _load_ota_template() -> str:
        if OTA_PROMPT_TEMPLATE_PATH.exists():
            return OTA_PROMPT_TEMPLATE_PATH.read_text(encoding="utf-8")

        logger.warning("OTA prompt template not found at %s; using built-in fallback", OTA_PROMPT_TEMPLATE_PATH)
        return (
            "Diagnose this OTA update failure from the evidence only.\n\n"
            "Analysis instructions:\n$client_instructions\n\n"
            "## Failure Event\n$failure_event\n\n"
            "## Recent History\n$recent_history\n\n"
            "## Process Logs\n$process_logs\n\n"
            "Reply in plain text: 1. Failure Reason, 2. Evidence (verbatim log lines), 3. Next Steps.\n"
        )

    def _load_template(self, template_path: str) -> str:
        path = Path(template_path)
        print("Template path:")
        print(path)
        if path.exists():
            return path.read_text(encoding="utf-8")

        logger.warning(
            "Prompt template file not found at %s; using built-in fallback template",
            path,
        )
        return (
            "You diagnose automotive software update failures on IVI and Android platforms.\n\n"
            "CLIENT INSTRUCTIONS:\n$client_instructions\n\n"
            "FAILURE EVENT:\n$failure_event\n\n"
            "RECENT HISTORY:\n$recent_history\n\n"
            "PROCESS LOGS:\n$process_logs\n\n"
            "If the logs are empty, say that the logs are empty and continue with the report."
            " Do not ask the user for more evidence.\n\n"
            "Return 5 short sections:\n"
            "1. Root Cause\n"
            "2. Evidence\n"
            "3. Failure Category\n"
            "4. Recovery Actions\n"
            "5. Preventive Fix\n"
        )

    @staticmethod
    def _format_client_instructions(instructions: Optional[str]) -> str:
        if not instructions:
            return "(No client instructions provided)"

        formatted_instructions = instructions.strip()
        return formatted_instructions if formatted_instructions else "(No client instructions provided)"

    @staticmethod
    def _format_process_logs(process_logs: Optional[Dict[str, str]]) -> str:
        if not process_logs:
            return "Evidence: No process logs provided; logs are empty.\nPROCESS LOGS: (Empty logs provided)"

        return RootCauseAnalyser.build_log_section(process_logs)

    def extract_logs_from_archive(self, archive_bytes: bytes, keep_full: bool = False) -> Dict[str, str]:
        extracted_logs: Dict[str, str] = {}
        try:
            archive_buffer = io.BytesIO(archive_bytes)

            if zipfile.is_zipfile(archive_buffer):
                archive_buffer.seek(0)
                with zipfile.ZipFile(archive_buffer) as archive:
                    for member in archive.infolist():
                        if member.is_dir():
                            continue

                        with archive.open(member) as extracted_file:
                            log_lines = extracted_file.read().decode(
                                "utf-8", errors="replace"
                            ).splitlines()

                        tail_lines = log_lines if keep_full else log_lines[-self._config.aimodel_log_lines :]
                        log_name = os.path.basename(member.filename)
                        log_text = "\n".join(tail_lines) if tail_lines else "(Empty log file)"
                        extracted_logs[log_name] = self.trim_text(
                            log_text, self._config.aimodel_log_chars
                        )
            elif tarfile.is_tarfile(archive_buffer):
                archive_buffer.seek(0)
                with tarfile.open(fileobj=archive_buffer, mode="r:*") as tar:
                    for member in tar.getmembers():
                        if not member.isfile():
                            continue

                        extracted_file = tar.extractfile(member)
                        if extracted_file is None:
                            continue

                        log_lines = extracted_file.read().decode(
                            "utf-8", errors="replace"
                        ).splitlines()
                        #tail_lines = log_lines[-self._config.aimodel_log_lines :]
                        log_name = os.path.basename(member.name)
                        #log_text = "\n".join(tail_lines) if tail_lines else "(Empty log file)"
                        if keep_full:
                            extracted_logs[log_name] = "\n".join(log_lines) or "(Empty log file)"
                            continue
                        extracted_logs[log_name] = self.trim_text(
                            log_lines, self._config.aimodel_log_chars
                        )
            else:
                logger.warning("Unsupported archive format received; expected zip or tar archive")
        except Exception as error:
            logger.error("Failed to extract log archive: %s", error)
        if not keep_full:
            print(extracted_logs)
        return extracted_logs
        
    def extract_logs_from_archives(
        self,
        archive_bytes: bytes,
    ) -> Dict[str, str]:
        extracted_logs: Dict[str, str] = {}

        try:
            archive_buffer = io.BytesIO(
                archive_bytes
            )

            if zipfile.is_zipfile(archive_buffer):
                archive_buffer.seek(0)

                with zipfile.ZipFile(
                    archive_buffer
                ) as archive:
                    for member in archive.infolist():
                        if (
                            member.is_dir()
                            or not member.filename.endswith(
                                ".log"
                            )
                        ):
                            continue

                        with archive.open(
                            member
                        ) as extracted_file:
                            log_lines = (
                                extracted_file
                                .read()
                                .decode(
                                    "utf-8",
                                    errors="replace",
                                )
                                .splitlines()
                            )

                        self._store_log(
                            extracted_logs,
                            os.path.basename(
                                member.filename
                            ),
                            log_lines,
                        )

            elif tarfile.is_tarfile(
                archive_buffer
            ):
                archive_buffer.seek(0)

                with tarfile.open(
                    fileobj=archive_buffer,
                    mode="r:*",
                ) as archive:
                    for member in archive.getmembers():
                        if (
                            not member.isfile()
                            or not member.name.endswith(
                                ".log"
                            )
                        ):
                            continue

                        extracted_file = (
                            archive.extractfile(member)
                        )

                        if extracted_file is None:
                            continue

                        log_lines = (
                            extracted_file
                            .read()
                            .decode(
                                "utf-8",
                                errors="replace",
                            )
                            .splitlines()
                        )

                        self._store_log(
                            extracted_logs,
                            os.path.basename(
                                member.name
                            ),
                            log_lines,
                        )
            else:
                logger.warning(
                    "Unsupported archive format received; "
                    "expected zip or tar archive"
                )

        except Exception as error:
            logger.error(
                "Failed to extract log archive1: %s",
                error,
            )

        return extracted_logs
    
    def _store_log(
        self,
        extracted_logs: Dict[str, str],
        log_name: str,
        log_lines: List[str],
    ) -> None:
        tail_lines = log_lines[
            -self._config.slm_log_lines:
        ]

        if tail_lines:
            log_text = "\n".join(tail_lines)
        else:
            log_text = "(Empty log file)"

        extracted_logs[log_name] = self.trim_text(
            log_text,
            self._config.slm_log_chars,
        )

        print("log_text=")
        
    @staticmethod
    def trim_text(text: str, max_chars: int) -> str:
        if max_chars <= 0 or len(text) <= max_chars:
            return text
        return text[:max_chars] + "\n...(truncated)"

    @staticmethod
    def summarize_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
        keys_to_keep = (
            "event",
            "timestamp",
            "errorCode",
            "errorName",
            "state",
            "stateName",
            "moduleName",
            "subModuleName",
            "releasePercentComplete",
            "subModulePercentComplete",
            "estimatedUpdateTimeSec",
            "line1",
            "line2",
        )
        return {key: event_data[key] for key in keys_to_keep if key in event_data}

    @staticmethod
    def build_log_section(process_logs: Optional[Dict[str, str]]) -> str:
        if not process_logs:
            return NO_PROCESS_LOGS_TEXT

        sections = [PROCESS_LOG_HEADER]
        for log_file, log_text in process_logs.items():
            sections.append(f"\n--- [{log_file}] ---\n{log_text}\n")
        return "".join(sections)

    @classmethod
    def _enforce_report_error_code(
        cls,
        report_text: str,
        process_logs: Optional[Dict[str, str]],
    ) -> str:
        report_text = re.sub(r'(?mi)^(3\.\s*Errorcode:\s*)errorCode:', r'\1', report_text)
        report_text = re.sub(r'(?mi)^(3\.\s*Errorcode:)\s+', r'\1', report_text)

        current_error_code = cls._extract_error_code_from_report(report_text)
        extracted_error_code = cls._extract_error_code_from_process_logs(process_logs)
        resolved_error_code = extracted_error_code or current_error_code
        if resolved_error_code is None:
            return report_text

        formatted_error_code_line = cls._format_error_code_line(resolved_error_code)


        # This regex will match "3. Errorcode:N/A" or "3. Errorcode:N"
        # and the rest of the line, making the check more robust.
       #missing_error_code = "3. Errorcode:N/A (Not present in da3_app_fcswupdate)"
        #if missing_error_code in report_text:
        #    return report_text.replace(
        #        missing_error_code,
        #        formatted_error_code_line,
        #        1,
        #    )
        missing_error_pattern = r'^3\.\s*Errorcode:\s*(?:N/A|N)\b.*'
        report_text, num_replacements = re.subn(
            missing_error_pattern,
            formatted_error_code_line,
            report_text,
            count=1,
            flags=re.MULTILINE | re.IGNORECASE
        )
        print("**replacement**")
        print(num_replacements)
        print("***")
        exit
        if num_replacements > 0:
            return report_text

        report_lines = report_text.splitlines()
        for index, line in enumerate(report_lines):
            if line.strip().lower().startswith("3. errorcode"):
                report_lines[index] = formatted_error_code_line
                return "\n".join(report_lines)

        suffix = f"\n{formatted_error_code_line}"
        return report_text.rstrip() + suffix + "\n"

    @staticmethod
    def _extract_error_code_from_report(report_text: str) -> Optional[str]:
        match = re.search(r'(?mi)^3\.\s*Errorcode:\s*([A-Za-z0-9_/]+)', report_text)
        if match is None:
            return None
        return match.group(1)

    @staticmethod
    def _extract_error_code_from_process_logs(process_logs: Optional[Dict[str, str]]) -> Optional[str]:
        if not process_logs:
            return None

        candidate_logs = [
            str(log_text)
            for log_name, log_text in process_logs.items()
            if "da3_app_fcswupdate" in str(log_name).lower()
        ]
        if not candidate_logs:
            return None

        patterns = (
            r'"?errorCode"?\s*:\s*(ERROR_[A-Za-z0-9_]+|\d+)',
            r'"?error_code"?\s*:\s*(ERROR_[A-Za-z0-9_]+|\d+)',
            r'"?errorCode"?\s*:=\s*(ERROR_[A-Za-z0-9_]+|\d+)',
            r'"?errorCode"?\s*=\s*(ERROR_[A-Za-z0-9_]+|\d+)',
            r'"?error_code"?\s*=\s*(ERROR_[A-Za-z0-9_]+|\d+)',
            r'\b(ERROR_[A-Za-z0-9_]+)\b',
        )

        for log_text in candidate_logs:
            for pattern in patterns:
                match = re.search(pattern, log_text)
                if match is not None:
                    return match.group(1)
        return None

    @staticmethod
    @lru_cache(maxsize=1)
    def _load_error_enum_map() -> Dict[str, str]:
        try:
            aidl_text = ERROR_CONFIG_PATH.read_text(encoding="utf-8")
        except OSError as error:
            logger.warning("Failed to read error config AIDL %s: %s", ERROR_CONFIG_PATH, error)
            return {}

        enum_map: Dict[str, str] = {}
        for enum_name, enum_value in re.findall(r'\b(ERROR_[A-Za-z0-9_]+)\s*=\s*(\d+)\s*,', aidl_text):
            enum_map[enum_value] = enum_name
        return enum_map

    @classmethod
    def _resolve_error_enum_name(cls, error_code: Optional[str]) -> Optional[str]:
        if not error_code:
            return None
        if error_code.startswith("ERROR_"):
            return error_code
        return cls._load_error_enum_map().get(error_code)

    @classmethod
    def _format_error_code_line(cls, error_code: str) -> str:
        error_enum_name = cls._resolve_error_enum_name(error_code)
        if error_enum_name:
            return f"3. Errorcode:{error_code} ({error_enum_name})"
        return f"3. Errorcode:{error_code}"