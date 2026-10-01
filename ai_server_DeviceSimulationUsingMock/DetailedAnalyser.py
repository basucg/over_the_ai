#!/usr/bin/env python3
import logging
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional, TYPE_CHECKING

from ModelConnector import AIModelClient

if TYPE_CHECKING:
    from UpdateAgent import ServerConfig

logger = logging.getLogger("AIDetailedAnalyser")

ERROR_CONFIG_PATH = Path(__file__).resolve().parent / "errorconfig.aidl"
ERROR_NEXT_STEPS_PATH = Path(__file__).resolve().parent  / "prompts" /"error_enum_next_steps.md"

class DetailedAnalyser:
    def __init__(self, config: "ServerConfig", aimodel_client: AIModelClient):
        self._config = config
        self._aimodel_client = aimodel_client

    async def analyse_next_steps(
        self,
        report_text: str,
        process_logs: Optional[Dict[str, str]],
        history_event_count: int,
    ) -> Optional[str]:
        error_code = self._extract_error_code_from_report(report_text)
        error_enum_name = self._resolve_error_enum_name(error_code)
        if error_enum_name is None:
            print("returning here")
            return None

        next_steps_prompt = self._build_next_steps_prompt(
            error_enum_name,
            process_logs,
        )
        print("*****next steps prompt****")
        print(next_steps_prompt)
        print("*********")
        
        next_steps_response = await self._aimodel_client.request_analysis(next_steps_prompt, history_event_count)
        print(next_steps_response)
        print("*********")
        return self._normalize_next_steps_response(
            next_steps_response,
            error_enum_name,
            process_logs,
        )

    def _build_next_steps_prompt(
        self,
        error_enum_name: str,
        process_logs: Optional[Dict[str, str]],
    ) -> str:
        return (
            f"Use the following instruction file to analyze the resolved SW update error enum.\n\n"
            f"Resolved Error Enum:\n{error_enum_name}\n\n"
            f"Instruction File:\n{self._load_instruction_file(ERROR_NEXT_STEPS_PATH)}\n\n"
            f"Process Logs:\n{self.build_log_section(process_logs)}\n\n"
            "Return exactly 3 sections.\n"
            "1. Failure Reason: one concise line.\n"
            "2. Evidence: do not exceed 8 log lines, and every evidence line must contain [ERROR].\n"
            "3. Next Steps: one concise line.\n"
            "Do not dump raw logs outside the Evidence section."
        )

    @staticmethod
    def _load_instruction_file(instruction_path: Path) -> str:
        try:
            return instruction_path.read_text(encoding="utf-8")
        except OSError as error:
            logger.warning("Instruction file not found at %s: %s", instruction_path, error)
            return "Instruction file unavailable."

    @staticmethod
    def build_log_section(process_logs: Optional[Dict[str, str]]) -> str:
        PROCESS_LOG_HEADER = "\nPROCESS LOG EXCERPTS:\n"
        NO_PROCESS_LOGS_TEXT = "\nPROCESS LOGS: (No log archive received yet)\n"
        if not process_logs:
            return NO_PROCESS_LOGS_TEXT

        sections = [PROCESS_LOG_HEADER]
        for log_file, log_text in process_logs.items():
            sections.append(f"\n--- [{log_file}] ---\n{log_text}\n")
        return "".join(sections)

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

    @staticmethod
    def _extract_error_code_from_report(report_text: str) -> Optional[str]:
        match = re.search(r'(?mi)^3\.\s*Errorcode:\s*([A-Za-z0-9_]+)', report_text)
        if match is None:
            return None
        return match.group(1)

    @classmethod
    def _normalize_next_steps_response(
        cls,
        response_text: str,
        error_enum_name: str,
        process_logs: Optional[Dict[str, str]],
    ) -> str:
        failure_reason = cls._extract_response_section(response_text, "1. Failure Reason")
        if failure_reason is None:
            failure_reason = error_enum_name

        next_steps = cls._extract_response_section(response_text, "3. Next Steps")
        if next_steps is None:
            next_steps = response_text.strip().splitlines()[0] if response_text.strip() else error_enum_name

        evidence_block = cls._extract_evidence_text(response_text, process_logs)

        return (
            f"1. Failure Reason: {failure_reason}\n"
            f"2. Evidence:\n{evidence_block}\n"
            f"3. Next Steps: {next_steps}"
        )
        
    @classmethod
    def _extract_evidence_text(
        cls,
        next_steps_text: Optional[str],
        process_logs: Optional[Dict[str, str]],
    ) -> str:
        if next_steps_text:
            evidence_text = cls._extract_response_section(next_steps_text, "2. Evidence")
            if evidence_text:
                return evidence_text

        evidence_lines = cls._collect_error_evidence_lines(process_logs)
        if evidence_lines:
            return "\n".join(evidence_lines)
        return "No [ERROR] lines found in provided logs."

    @staticmethod
    def _extract_response_section(response_text: str, header: str) -> Optional[str]:
        pattern = rf'(?ims)^\s*{re.escape(header)}\s*:\s*(.*?)(?=^\s*[123]\.\s|\Z)'
        match = re.search(pattern, response_text)
        if match is None:
            return None
        section_text = match.group(1).strip()
        return section_text or None

    @staticmethod
    def _collect_error_evidence_lines(
        process_logs: Optional[Dict[str, str]],
        max_lines: int = 8,
    ) -> list[str]:
        if not process_logs:
            return []

        evidence_lines: list[str] = []
        for log_name, log_text in process_logs.items():
            for line in str(log_text).splitlines():
                if "[ERROR]" not in line:
                    continue
                evidence_lines.append(f"[{log_name}] {line}")
                if len(evidence_lines) >= max_lines:
                    return evidence_lines
        return evidence_lines