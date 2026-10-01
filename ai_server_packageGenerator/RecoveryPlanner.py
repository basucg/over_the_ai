#!/usr/bin/env python3
import logging
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional, TYPE_CHECKING, List

from ModelConnector import AIModelClient

if TYPE_CHECKING:
    from UpdateAgent import ServerConfig

logger = logging.getLogger("AIRecoveryPlanner")

ERROR_CONFIG_PATH = Path(__file__).resolve().parent / "errorconfig.aidl"
RECOVERY_PLAN_PATH = Path(__file__).resolve().parent /  "prompts" /"recovery_plan.md"

class RecoveryPlanner:
    def __init__(self, config: "ServerConfig", aimodel_client: AIModelClient):
        self._config = config
        self._aimodel_client = aimodel_client

    async def plan_recovery(
        self,
        report_text: str,
        next_steps_text: Optional[str],
        process_logs: Optional[Dict[str, str]],
        history_event_count: int,
    ) -> Optional[str]:
        error_code = self._extract_error_code_from_report(report_text)
        if error_code is None:
            return None

        error_enum_name = self._resolve_error_enum_name(error_code)
        failure_reason = self._extract_failure_reason(next_steps_text, error_enum_name)
        package_type = self._extract_package_type_from_report(report_text)
        #from_version = self._resolve_version_value(report_text, process_logs, "FROM_VERSION")
        from_version = "qpr1_a12_int_2026.19.0"
        #to_version = self._resolve_version_value(report_text, process_logs, "TO_VERSION")
        to_version = "qpr1_a12_int_2026.18.0"
        evidence_text = self._extract_evidence_text(next_steps_text, process_logs)

        recovery_prompt = self._build_recovery_plan_prompt(
            error_code,
            error_enum_name,
            failure_reason,
            evidence_text,
            package_type,
            from_version,
            to_version,
        )

        recovery_response = await self._aimodel_client.request_analysis(recovery_prompt, history_event_count)
        # print("***************")
        # print(recovery_response)
        # print("******************")
        return self._normalize_recovery_plan_response(recovery_response, error_code, error_enum_name)

    def _build_recovery_plan_prompt(
        self,
        error_code: str,
        error_enum_name: Optional[str],
        failure_reason: str,
        evidence_text: str,
        package_type: str,
        from_version: str,
        to_version: str,
    ) -> str:
        error_label = error_code if error_enum_name is None else f"{error_code} ({error_enum_name})"

        return (
            "Use the following instruction file to identify a recovery plan for the resolved SW update error.\n\n"
            f"Instruction File:\n{self._load_instruction_file(RECOVERY_PLAN_PATH)}\n\n"
            f"Error Number:\n{error_label}\n\n"
            f"Failure Reason:\n{failure_reason}\n\n"
            f"Evidence:\n{evidence_text}\n\n"
            f"Package Type:\n{package_type}\n\n"
            "Version Information:\n"
            f"FROM_VERSION: {from_version}\n"
            f"TO_VERSION: {to_version}"
        )

    @staticmethod
    def _load_instruction_file(instruction_path: Path) -> str:
        try:
            return instruction_path.read_text(encoding="utf-8")
        except OSError as error:
            logger.warning("Instruction file not found at %s: %s", instruction_path, error)
            return "Instruction file unavailable."

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
    def _extract_failure_reason(
        cls,
        next_steps_text: Optional[str],
        error_enum_name: Optional[str],
    ) -> str:
        if next_steps_text:
            failure_reason = cls._extract_response_section(next_steps_text, "1. Failure Reason")
            if failure_reason:
                return failure_reason
        return error_enum_name or "N/A"

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

    @staticmethod
    def _extract_error_code_from_report(report_text: str) -> Optional[str]:
        match = re.search(r'(?mi)^3\.\s*Errorcode:\s*([A-Za-z0-9_]+)', report_text)
        if match is None:
            return None
        return match.group(1)

    @staticmethod
    def _extract_package_type_from_report(report_text: str) -> str:
        match = re.search(r'(?mi)^1\.\s*Package Type:\s*(.+)$', report_text)
        if match is None:
            return "UNKNOWN"
        package_type = match.group(1).strip()
        return package_type or "UNKNOWN"

    @staticmethod
    def _extract_version_value_from_report(report_text: str, label: str) -> str:
        # First, try to parse the report_text as a JSON object.
        #print("Trying version extraction for ")
        #print(label)
        #print(report_text)
        try:
            data = json.loads(report_text)
            if isinstance(data, dict):
                value = data.get(label)
                if value is not None:
                    return str(value).strip()
        except json.JSONDecodeError:
            # Not a valid JSON string, so we'll fall back to regex matching.
            pass
        #print("Not a json")
        pattern = rf'(?mi)^\s*"?{re.escape(label)}"?\s*:\s*"?(?P<value>[^",\r\n]+)'
        match = re.search(pattern, report_text)
        if match:
            print(match.group("value").strip())
            return match.group("value").strip()
        #print("second match")
        # A simpler regex as a final fallback for "KEY: VALUE"
        match = re.search(rf'(?mi)^\s*{re.escape(label)}\s*:\s*(.+)$', report_text)
        if match:
            print(match.group(1).strip())
            return match.group(1).strip()

        return "N/A"

    @staticmethod
    def _extract_version_value_from_process_logs(
        process_logs: Optional[Dict[str, str]],
        label: str,
    ) -> str:
        if not process_logs:
            return "N/A"

        candidate_logs = [
            str(log_text)
            for log_name, log_text in process_logs.items()
            if "da3_app_fcswupdate" in str(log_name).lower()
        ]
        if not candidate_logs:
            return "N/A"

        if label == "FROM_VERSION":
            patterns = (r'(?mi)\bCUSTOMER_VERSION\s*:\s*(.+)$',)
        elif label == "TO_VERSION":
            patterns = (
                r'(?mi)\bupdateBuildLabel\s+from\s+bosch\.xml\s*:\s*\[([^\]\r\n]+)\]',
                r'(?mi)\bupdateBuildLabel\s+from\s+bosch\.xml\s*:\s*(.+)$',
            )
        else:
            return "N/A"

        for log_text in candidate_logs:
            for pattern in patterns:
                match = re.search(pattern, log_text)
                if match is None:
                    continue
                version_value = match.group(1).strip().strip("[]")
                if version_value:
                    return version_value
        return "N/A"

    @classmethod
    def _resolve_version_value(
        cls,
        report_text: str,
        process_logs: Optional[Dict[str, str]],
        label: str,
    ) -> str:
        version_value = cls._extract_version_value_from_report(report_text, label)
        if version_value != "N/A":
            return version_value
        return cls._extract_version_value_from_process_logs(process_logs, label)

    @staticmethod
    def _extract_single_line_response_value(response_text: str, label: str) -> Optional[str]:
        match = re.search(rf'(?im)^\s*(?:\d+\.\s*)?{re.escape(label)}\s*:\s*(.+)$', response_text)
        if match is None:
            return None
        value = match.group(1).strip()
        return value or None

    @classmethod
    def _normalize_recovery_plan_response(
        cls,
        response_text: str,
        error_code: str,
        error_enum_name: Optional[str],
    ) -> str:
        normalized_error_code = cls._extract_single_line_response_value(response_text, "error_code")
        if normalized_error_code is None:
            normalized_error_code = error_code if error_enum_name is None else f"{error_code} ({error_enum_name})"

        recovery_action = cls._extract_single_line_response_value(response_text, "recovery_action")
        if recovery_action is None:
            recovery_action = next((line.strip() for line in response_text.splitlines() if line.strip()), "CLASSIFY_ERROR")

        detailed_recovery_plan = cls._extract_single_line_response_value(response_text, "detailed_recovery_plan")
        if detailed_recovery_plan is None:
            detailed_recovery_plan = recovery_action

        lines = [
            f"error_code: {normalized_error_code}",
            f"recovery_action: REGENERATE_PACKAGE AND RETRY UPDATE",
            f"detailed_recovery_plan: {detailed_recovery_plan}",
        ]

        recovery_info = cls._extract_single_line_response_value(response_text, "recovery_info")
        if recovery_info is None:
            for line in response_text.splitlines():
                stripped = line.strip()
                if stripped.startswith("{") and stripped.endswith("}"):
                    recovery_info = stripped
                    break

        if recovery_info is not None:
            lines.append(f"recovery_info: {recovery_info}")

        return "\n".join(lines)