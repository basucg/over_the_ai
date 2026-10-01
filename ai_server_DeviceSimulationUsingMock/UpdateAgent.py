#!/usr/bin/env python3
import asyncio
import base64
from dataclasses import dataclass, field
import json
import logging
import os
from pathlib import Path
import sys
import time
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set

from ModelConnector import AIModelClient
from RootcauseAnalyser import RootCauseAnalyser
from DetailedAnalyser import DetailedAnalyser
from RecoveryPlanner import RecoveryPlanner

# Constants
REPORT_SEPARATOR = "=" * 70
ARCHIVE_EVENT_NAME = "swUpdateDiagnosticArchive"
DIAGNOSTIC_EVENT_NAMES = {"onUpdateError", "onUpdateState"}
ERROR_STATE_CODE = 6
TCP_STREAM_LIMIT_BYTES = 12 * 1024 * 1024
DEFAULT_PROMPT_TEMPLATE_PATH = Path(__file__).resolve().parent / "prompts" / "aimodel_prompt.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("AIUpdateAgent")

@dataclass
class SystemDetails:
    product_class: str
    primary_os: str
    secondary_os: Set[str] = field(default_factory=set)

    def __post_init__(self):
        # Normalize casing for robust comparisons
        self.product_class = self.product_class.strip().upper()
        self.primary_os = self.primary_os.strip().capitalize()
        self.secondary_os = {os.strip().capitalize() for os in self.secondary_os}


def request_system_details(product_class: str, primary_os: str, secondary_os: Optional[Set[str]] = None) -> List[str]:
    """
    Handles system detail inputs and determines required log requests.
    """
    if secondary_os is None:
        secondary_os = set()
        
    system = SystemDetails(
        product_class=product_class,
        primary_os=primary_os,
        secondary_os=secondary_os
    )
    
    requested_artifacts: List[str] = []

    # Check condition: product_class == 'IVI' and primary_os == 'Android'
    if system.product_class == "IVI" and system.primary_os == "Android":
        requested_artifacts.extend([
            "update_engine",
            "da3_app_fcswupdate",
            "downloadpipe"
        ])
    
    # Process / print request output
    print(f"--- Processing System: {system.product_class} ({system.primary_os}) ---")
    if requested_artifacts:
        print("Requested logs / artifacts:")
        for artifact in requested_artifacts:
            print(f"  - {artifact}")
    else:
        print("No specific diagnostic logs configured for this combination.")
        
    return requested_artifacts

@dataclass(frozen=True)
class ServerConfig:
    tcp_host: str
    tcp_port: int
    aimodel_api_url: str
    aimodel_model: str
    aimodel_timeout_sec: float
    aimodel_history_events: int
    aimodel_log_lines: int
    aimodel_log_chars: int
    aimodel_prompt_template_path: str
    diagnostic_dir: str
    reports_dir: str

    @classmethod
    def from_env(cls) -> "ServerConfig":
        return cls(
            tcp_host=os.getenv("AI_SERVER_HOST", "0.0.0.0"),
            tcp_port=int(os.getenv("AI_SERVER_PORT", "9000")),
            aimodel_api_url=os.getenv("AIMODEL_API_URL", "http://localhost:11434/api/generate"),
            aimodel_model=os.getenv("AIMODEL_MODEL", "gemma3:4b"),
            aimodel_timeout_sec=float(os.getenv("AIMODEL_TIMEOUT_SEC", "1800")),
            aimodel_history_events=int(os.getenv("AIMODEL_HISTORY_EVENTS", "3")),
            aimodel_log_lines=int(os.getenv("AIMODEL_LOG_LINES", "25")),
            aimodel_log_chars=int(os.getenv("AIMODEL_LOG_CHARS", "800")),
            aimodel_prompt_template_path=os.getenv(
                "AIMODEL_PROMPT_FILE", str(DEFAULT_PROMPT_TEMPLATE_PATH)
            ),
            diagnostic_dir=os.getenv("DIAGNOSTIC_DIR", "/tmp/ai-swupdate-diagnostics"),
            reports_dir=os.getenv("REPORTS_DIR", "/tmp/ai-swupdate-reports"),
        )

class DiagnosticSession:
    def __init__(self) -> None:
        self._events: List[Dict[str, Any]] = []

    def record_event(self, event_data: Dict[str, Any]) -> None:
        self._events.append(event_data)

    def recent_events(self) -> List[Dict[str, Any]]:
        return list(self._events)

    def find_latest_diagnostic_event(
        self, fallback_event: Dict[str, Any]
    ) -> Dict[str, Any]:
        for event_data in reversed(self._events):
            if event_data.get("event") in DIAGNOSTIC_EVENT_NAMES:
                return event_data
        return fallback_event

class AiDiagnosticServer:
    def __init__(
        self,
        config: ServerConfig,
        root_cause_analyser: RootCauseAnalyser,
        detailed_analyser: DetailedAnalyser,
        recovery_planner: RecoveryPlanner,
    ) -> None:
        self._config = config
        self._root_cause_analyser = root_cause_analyser
        self._detailed_analyser = detailed_analyser
        self._recovery_planner = recovery_planner
        self._session = DiagnosticSession()
        self._event_handlers: Dict[str, Callable[[Dict[str, Any]], Awaitable[None]]] = {
            "onUpdateState": self._handle_update_state,
            "onUpdateProgress": self._handle_update_progress,
            "onUpdateError": self._handle_update_error,
            "onCancelUpdResult": self._handle_result_event,
            "onCompleteUpdResult": self._handle_result_event,
            #"systemDetailsResponse":self._handle_system_details_response,
            ARCHIVE_EVENT_NAME: self._handle_diagnostic_archive,
            #"getRequiredFilesResponse":self._handle_logs_response,
        }

    async def serve(self) -> None:
        logger.info(
            "Starting AI Diagnostic Server on %s:%s (Model: %s)",
            self._config.tcp_host,
            self._config.tcp_port,
            self._config.aimodel_model,
        )
        logger.info(
            "Connected AI Model Endpoint: %s (Model: %s)",
            self._config.aimodel_api_url,
            self._config.aimodel_model,
        )
        server = await asyncio.start_server(
            self.handle_client,
            self._config.tcp_host,
            self._config.tcp_port,
            limit=TCP_STREAM_LIMIT_BYTES,
        )
        async with server:
            await server.serve_forever()

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        peer = writer.get_extra_info("peername")
        logger.info("Client connected from %s", peer)

        try:
            while True:
                line = await reader.readline()
                if not line:
                    logger.info("Client %s disconnected", peer)
                    return

                event_data = self._decode_event(line)
                if event_data is None:
                    continue

                self._session.record_event(event_data)
                await self._dispatch_event(event_data)
        except asyncio.CancelledError:
            raise
        except Exception as error:
            logger.error("Exception handling client %s: %s", peer, error)
        finally:
            writer.close()
            await writer.wait_closed()

    def _decode_event(self, raw_line: bytes) -> Optional[Dict[str, Any]]:
        raw_payload = raw_line.decode("utf-8", errors="replace").strip()
        if not raw_payload:
            return None

        try:
            return json.loads(raw_payload)
        except json.JSONDecodeError:
            logger.warning("Received non-JSON payload: %s", raw_payload)
            return None

    async def _dispatch_event(self, event_data: Dict[str, Any]) -> None:
        handler = self._event_handlers.get(event_data.get("event", "unknown"))
        if handler is not None:
            await handler(event_data)


    async def _handle_update_state(self, event_data: Dict[str, Any]) -> None:
        logger.info(
            "==> [STATE] %s (Est. remaining: %ss)",
            event_data.get("stateName", "Unknown"),
            event_data.get("estimatedUpdateTimeSec", 0),
        )
        if event_data.get("state") == ERROR_STATE_CODE:
            logger.error("STATE ERROR DETECTED! Triggering initial AI Model analysis...")
            await self._generate_diagnostic_report(
                event_data,
                instructions=self._extract_client_instructions(event_data),
            )

    async def _handle_update_progress(self, event_data: Dict[str, Any]) -> None:
        logger.info(
            "--> [PROGRESS] Mod: %s | Sub: %s (%s%%) | Overall: %s%%",
            event_data.get("moduleName", ""),
            event_data.get("subModuleName", ""),
            event_data.get("subModulePercentComplete", 0),
            event_data.get("releasePercentComplete", 0),
        )

    async def _handle_update_error(self, event_data: Dict[str, Any]) -> None:
        logger.error(
            "!!! [ERROR EVENT] Code %s: %s",
            event_data.get("errorCode", -1),
            event_data.get("errorName", "Unknown"),
        )
        process_logs = self._extract_direct_process_logs(event_data)
        if not process_logs:
            logger.info(
                "No process logs in onUpdateError event; deferring diagnosis until swUpdateDiagnosticArchive arrives."
            )
            return
        await self._generate_diagnostic_report(
            event_data,
            instructions=self._extract_client_instructions(event_data),
            process_logs=process_logs,
        )

    async def _handle_diagnostic_archive(self, event_data: Dict[str, Any]) -> None:
        archive_name = os.path.basename(event_data.get("archiveName", "diagnostics.tar.gz"))
        archive_data_b64 = event_data.get("archiveData", "")
        try:
            archive_bytes = base64.b64decode(archive_data_b64, validate=True)
            archive_path = self._save_diagnostic_archive(archive_name, archive_bytes)
            logger.info("Saved SWUpdate diagnostic archive: %s", archive_path)

            archive_logs = self._root_cause_analyser.extract_logs_from_archive(archive_bytes)
            print(" Archibe logs::::::::::::::::::::")
            #print(archive_logs)
            direct_logs = self._extract_direct_process_logs(event_data)
            process_logs = self._merge_process_logs(archive_logs, direct_logs)
            latest_error_event = self._session.find_latest_diagnostic_event(event_data)
            await self._generate_diagnostic_report(
                latest_error_event,
                instructions=self._extract_client_instructions(event_data),
                process_logs=process_logs,
                title="         AI Model ROOT CAUSE DIAGNOSIS (WITH PROCESS LOGS)",
                path_label="Report File Created on Linux Server",
            )
        except (ValueError, OSError) as error:
            logger.error("Could not save or analyze SWUpdate diagnostic archive: %s", error)

    async def _handle_result_event(self, event_data: Dict[str, Any]) -> None:
        logger.info("<-- [%s] Result: %s", event_data.get("event", "unknown"), event_data.get("errorName", "Unknown"))

    async def _generate_diagnostic_report(
        self,
        trigger_event: Dict[str, Any],
        instructions: Optional[str] = None,
        process_logs: Optional[Dict[str, str]] = None,
        title: str = "                AI Model AUTOMATED ROOT CAUSE DIAGNOSIS",
        path_label: str = "Report File Created",
    ) -> None:
        recent_history = self._session.recent_events()
        logger.info(
            "Entering query_aimodel for event=%s errorCode=%s history_events=%d process_logs=%d",
            trigger_event.get("event", "unknown"),
            trigger_event.get("errorCode", trigger_event.get("state", "n/a")),
            len(recent_history),
            len(process_logs or {}),
        )
        self._log_process_logs(process_logs)
        #print(process_logs)
        report_text = await self._root_cause_analyser.analyse(
            instructions,
            trigger_event,
            recent_history,
            process_logs,
        )
        #report_text = self._enforce_report_error_code(report_text, process_logs)
        print("*****report text**********")
        print(report_text)
        print("***************")
        #print(process_logs)
        
        next_steps_text = await self._detailed_analyser.analyse_next_steps(report_text, process_logs, len(recent_history))
        report_path = self._save_report_file(report_text)
        
        #print("*****next_steps_text**********")
        #print(next_steps_text)
        #print("***************")
        self._print_report(title, report_text, report_path, path_label, next_steps_text)
        recovery_plan_text = await self._recovery_planner.plan_recovery(report_text, next_steps_text, process_logs, len(recent_history))
        #print("*****recovery_plan_text**********")
        #print(recovery_plan_text)
        #print("***************")
        self._print_recovery_plan(recovery_plan_text)
        
        # As requested, calling the package generator with specified parameters.
        await self.call_swu_package_generator(
            verify_version=True,
            verification_type="Upgrade",
            from_version="qpr1_a12_int_2026.19.0",
            to_version="qpr1_a12_int_2026.18.0",
            package_type="delta"
        )

    async def call_swu_package_generator(self, verify_version: bool, verification_type: str, from_version: str, to_version: str, package_type: str):
        """
        Connects to the swu_package_generator service and requests a package generation.
        """
        host = os.getenv("PKG_GEN_HOST", "127.0.0.1")
        port = int(os.getenv("PKG_GEN_PORT", "9001"))

        params = {
            "verify_version": verify_version,
            "verification_type": verification_type,
            "from_version": from_version,
            "to_version": to_version,
            "package_type": package_type,
        }

        request_data = {
            "command": "generate_package",
            "params": params,
            "request_id": f"req-{int(time.time())}"
        }
        
        writer = None
        try:
            logger.info(f"Connecting to Package Generator at {host}:{port} to generate package.")
            reader, writer = await asyncio.open_connection(host, port)
            
            writer.write(json.dumps(request_data).encode('utf-8') + b'\n')
            await writer.drain()
            
            logger.info(f"Sent package generation request with params: {params}")

            response_line = await reader.readline()
            if response_line:
                response = json.loads(response_line.decode('utf-8'))
                logger.info(f"Response from Package Generator: {response}")

        except (ConnectionRefusedError, OSError) as e:
            logger.error(f"Failed to connect to Package Generator at {host}:{port}: {e}")
        except Exception as e:
            logger.error(f"Error communicating with Package Generator: {e}")
        finally:
            if writer:
                writer.close()
                await writer.wait_closed()

    @staticmethod
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

        missing_error_code = "3. Errorcode:N/A (Not present in da3_app_fcswupdate)"
        if missing_error_code in report_text:
            return report_text.replace(
                missing_error_code,
                formatted_error_code_line,
                1,
            )

        report_lines = report_text.splitlines()
        for index, line in enumerate(report_lines):
            if line.strip().lower().startswith("3. errorcode"):
                report_lines[index] = formatted_error_code_line
                return "\n".join(report_lines)

        suffix = f"\n{formatted_error_code_line}"
        return report_text.rstrip() + suffix + "\n" 

    @staticmethod
    def _log_process_logs(process_logs: Optional[Dict[str, str]]) -> None:
        if not process_logs:
            logger.warning("process_logs is empty")
            return

        non_empty_logs = {
            log_name: log_text
            for log_name, log_text in process_logs.items()
            if str(log_text).strip()
        }
        if not non_empty_logs:
            logger.warning("process_logs is empty")
            return

    @staticmethod
    def _extract_client_instructions(event_data: Dict[str, Any]) -> Optional[str]:
        instructions = event_data.get("instructions") or event_data.get("promptInstructions")
        if instructions is None:
            return None
        return str(instructions)

    @staticmethod
    def _extract_direct_process_logs(event_data: Dict[str, Any]) -> Optional[Dict[str, str]]:
        logs_payload = event_data.get("logs") or event_data.get("processLogs")
        if logs_payload is None:
            return None

        if isinstance(logs_payload, dict):
            return {str(log_name): str(log_text) for log_name, log_text in logs_payload.items()}

        if isinstance(logs_payload, list):
            normalized_logs: Dict[str, str] = {}
            for index, log_entry in enumerate(logs_payload, start=1):
                if isinstance(log_entry, dict):
                    log_name = str(
                        log_entry.get("name")
                        or log_entry.get("fileName")
                        or log_entry.get("logName")
                        or f"log-{index}.txt"
                    )
                    log_text = str(log_entry.get("content") or log_entry.get("text") or "")
                else:
                    log_name = f"log-{index}.txt"
                    log_text = str(log_entry)
                normalized_logs[log_name] = log_text
            return normalized_logs

        return {"payload.log": str(logs_payload)}

    @staticmethod
    def _merge_process_logs(
        archive_logs: Optional[Dict[str, str]],
        direct_logs: Optional[Dict[str, str]],
    ) -> Optional[Dict[str, str]]:
        if not archive_logs and not direct_logs:
            return None

        merged_logs: Dict[str, str] = {}
        if archive_logs:
            merged_logs.update(archive_logs)
        if direct_logs:
            merged_logs.update(direct_logs)
        return merged_logs

    def _save_diagnostic_archive(self, archive_name: str, archive_bytes: bytes) -> str:
        os.makedirs(self._config.diagnostic_dir, exist_ok=True)
        archive_path = os.path.join(self._config.diagnostic_dir, archive_name)
        with open(archive_path, "wb") as archive_file:
            archive_file.write(archive_bytes)
        return archive_path

    def _save_report_file(self, report_text: str) -> str:
        try:
            os.makedirs(self._config.reports_dir, exist_ok=True)
            report_path = os.path.join(self._config.reports_dir, f"swupdate-report-{int(time.time())}.md")
            with open(report_path, "w", encoding="utf-8") as report_file:
                report_file.write(report_text)
            logger.info("Diagnostic report successfully saved to Linux server: %s", report_path)
            return report_path
        except OSError as error:
            logger.error("Failed to save report file on Linux server: %s", error)
            return ""

    @staticmethod
    def _print_report(
        title: str,
        report_text: str,
        report_path: str,
        path_label: str,
        next_steps_text: Optional[str] = None,
    ) -> None:
        error_code = RootCauseAnalyser._extract_error_code_from_report(report_text)
        error_enum_name = DetailedAnalyser._resolve_error_enum_name(error_code)

        print("\n" + REPORT_SEPARATOR)
        print(title.replace("SLM", "AI Model"))
        print(REPORT_SEPARATOR)
        print(report_text)
        if error_code is not None:
            print(f"Resolved Errorcode: {error_code}")
        if error_enum_name is not None:
            print(f"Resolved Error Enum: {error_enum_name}")
        if next_steps_text:
            print(REPORT_SEPARATOR)
            print("AI Model ENUM NEXT STEPS")
            print(REPORT_SEPARATOR)
            print(next_steps_text)
        print(REPORT_SEPARATOR)
        if report_path:
            print(f"{path_label}: {report_path}")
        print(REPORT_SEPARATOR + "\n")

    @staticmethod
    def _print_recovery_plan(recovery_plan_text: Optional[str]) -> None:
        if not recovery_plan_text:
            return

        print(REPORT_SEPARATOR)
        print("AI Model RECOVERY PLAN")
        print(REPORT_SEPARATOR)
        print(recovery_plan_text)
        print(REPORT_SEPARATOR + "\n")
        
        
        


async def main() -> None:
    config = ServerConfig.from_env()
    aimodel_client = AIModelClient(config)
    root_cause_analyser = RootCauseAnalyser(config, aimodel_client)
    detailed_analyser = DetailedAnalyser(config, aimodel_client)
    recovery_planner = RecoveryPlanner(config, aimodel_client)
    server = AiDiagnosticServer(config, root_cause_analyser, detailed_analyser, recovery_planner)
    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("AI Server shutting down.")
        sys.exit(0)