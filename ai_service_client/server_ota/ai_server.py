#!/usr/bin/env python3
"""
AI Diagnostic Server (Linux / Docker)
Listens for SWUpdate notifications streamed over TCP from Android ai_service_client,
tracks update session state, and invokes an SLM (via Ollama or OpenAI-compatible API)
to diagnose root cause when update failures occur using logs from da3_app_fcswupdate,
update_engine_client, and update_engine.
"""

import asyncio
import base64
from dataclasses import dataclass
import io
import json
import logging
import os
from functools import lru_cache
from pathlib import Path
import re
import socket
import sys
import tarfile
import time
import zipfile
from string import Template
from typing import Any, Awaitable, Callable, Dict, List, Optional
from urllib.parse import urlparse

try:
    import httpx
except ImportError:
    httpx = None

REPORT_SEPARATOR = "=" * 70
PROCESS_LOG_HEADER = "\nPROCESS LOG EXCERPTS:\n"
NO_PROCESS_LOGS_TEXT = "\nPROCESS LOGS: (No log archive received yet)\n"
ARCHIVE_EVENT_NAME = "swUpdateDiagnosticArchive"
DIAGNOSTIC_EVENT_NAMES = {"onUpdateError", "onUpdateState"}
ERROR_STATE_CODE = 6
TCP_STREAM_LIMIT_BYTES = 12 * 1024 * 1024
DEFAULT_PROMPT_TEMPLATE_PATH = Path(__file__).resolve().parent / "prompts" / "slm_prompt.txt"
ERROR_CONFIG_PATH = Path(__file__).resolve().parent / "errorconfig.aidl"
ERROR_NEXT_STEPS_PATH = Path(__file__).resolve().parent / "error_enum_next_steps.md"
RECOVERY_PLAN_PATH = Path(__file__).resolve().parent / "recovery_plan.md"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("AIServer")


from dataclasses import dataclass, field
from typing import Set, List, Optional

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
            "update_engine_logs",
            "logcat_logs",
            "update_persistent_logs",
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
    slm_api_url: str
    slm_model: str
    slm_timeout_sec: float
    slm_history_events: int
    slm_log_lines: int
    slm_log_chars: int
    prompt_template_path: str
    diagnostic_dir: str
    reports_dir: str

    @classmethod
    def from_env(cls) -> "ServerConfig":
        return cls(
            tcp_host=os.getenv("AI_SERVER_HOST", "0.0.0.0"),
            tcp_port=int(os.getenv("AI_SERVER_PORT", "9000")),
            slm_api_url=os.getenv("SLM_API_URL", "http://localhost:11434/api/generate"),
            slm_model=os.getenv("SLM_MODEL", "gemma3:4b"),
            slm_timeout_sec=float(os.getenv("SLM_TIMEOUT_SEC", "1800")),
            slm_history_events=int(os.getenv("SLM_HISTORY_EVENTS", "3")),
            slm_log_lines=int(os.getenv("SLM_LOG_LINES", "25")),
            slm_log_chars=int(os.getenv("SLM_LOG_CHARS", "800")),
            prompt_template_path=os.getenv(
                "SLM_PROMPT_FILE", str(DEFAULT_PROMPT_TEMPLATE_PATH)
            ),
            diagnostic_dir=os.getenv("DIAGNOSTIC_DIR", "/tmp/ai-swupdate-diagnostics"),
            reports_dir=os.getenv("REPORTS_DIR", "/tmp/ai-swupdate-reports"),
        )


from pathlib import Path
from string import Template
from typing import Any, Awaitable, Callable, Dict, List, Optional

try:
    import httpx
except ImportError:
    httpx = None

REPORT_SEPARATOR = "=" * 70
PROCESS_LOG_HEADER = "\nPROCESS LOG EXCERPTS:\n"
NO_PROCESS_LOGS_TEXT = "\nPROCESS LOGS: (No log archive received yet)\n"
ARCHIVE_EVENT_NAME = "swUpdateDiagnosticArchive"
DIAGNOSTIC_EVENT_NAMES = {"onUpdateError", "onUpdateState"}
ERROR_STATE_CODE = 6
TCP_STREAM_LIMIT_BYTES = 12 * 1024 * 1024
DEFAULT_PROMPT_TEMPLATE_PATH = Path(__file__).resolve().parent / "prompts" / "slm_prompt.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("AIServer")


@dataclass(frozen=True)
class ServerConfig:
    tcp_host: str
    tcp_port: int
    slm_api_url: str
    slm_model: str
    slm_timeout_sec: float
    slm_history_events: int
    slm_log_lines: int
    slm_log_chars: int
    prompt_template_path: str
    diagnostic_dir: str
    reports_dir: str

    @classmethod
    def from_env(cls) -> "ServerConfig":
        return cls(
            tcp_host=os.getenv("AI_SERVER_HOST", "0.0.0.0"),
            tcp_port=int(os.getenv("AI_SERVER_PORT", "9000")),
            slm_api_url=os.getenv("SLM_API_URL", "http://localhost:11434/api/generate"),
            slm_model=os.getenv("SLM_MODEL", "qwen3:4b"),
            slm_timeout_sec=float(os.getenv("SLM_TIMEOUT_SEC", "180")),
            slm_history_events=int(os.getenv("SLM_HISTORY_EVENTS", "3")),
            slm_log_lines=int(os.getenv("SLM_LOG_LINES", "25")),
            slm_log_chars=int(os.getenv("SLM_LOG_CHARS", "800")),
            prompt_template_path=os.getenv(
                "SLM_PROMPT_FILE", str(DEFAULT_PROMPT_TEMPLATE_PATH)
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


class DiagnosticPromptBuilder:
    def __init__(self, config: ServerConfig) -> None:
        self._config = config
        self._template = self._load_template(config.prompt_template_path)

    def build_prompt(
        self,
        instructions: Optional[str],
        error_event: Dict[str, Any],
        recent_history: List[Dict[str, Any]],
        process_logs: Optional[Dict[str, str]],
    ) -> str:
        values = {
            "client_instructions": self._format_client_instructions(instructions),
            "failure_event": json.dumps(self.summarize_event(error_event), indent=2),
            "recent_history": json.dumps(
                [self.summarize_event(event) for event in recent_history[-self._config.slm_history_events :]],
                indent=2,
            ),
            "process_logs": self._format_process_logs(process_logs),
        }
        return Template(self._template).safe_substitute(values)

    def build_next_steps_prompt(
        self,
        error_enum_name: str,
        process_logs: Optional[Dict[str, str]],
    ) -> str:
        return (
            f"Use the following instruction file to analyze the resolved SW update error enum.\n\n"
            f"Resolved Error Enum:\n{error_enum_name}\n\n"
            f"Instruction File:\n{self._load_instruction_file(ERROR_NEXT_STEPS_PATH)}\n\n"
            f"Process Logs:\n{self._format_process_logs(process_logs)}\n\n"
            "Return exactly 3 sections.\n"
            "1. Failure Reason: one concise line.\n"
            "2. Evidence: do not exceed 8 log lines, and every evidence line must contain [ERROR].\n"
            "3. Next Steps: one concise line.\n"
            "Do not dump raw logs outside the Evidence section."
        )

    def build_recovery_plan_prompt(
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

    def _load_template(self, template_path: str) -> str:
        path = Path(template_path)
        print("Template path:")
        print(path);
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
    def _load_instruction_file(instruction_path: Path) -> str:
        try:
            return instruction_path.read_text(encoding="utf-8")
        except OSError as error:
            logger.warning("Instruction file not found at %s: %s", instruction_path, error)
            return "Instruction file unavailable."

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

        return DiagnosticPromptBuilder.build_log_section(process_logs)

    def extract_logs_from_archive(self, archive_bytes: bytes) -> Dict[str, str]:
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

                        tail_lines = log_lines[-self._config.slm_log_lines :]
                        log_name = os.path.basename(member.filename)
                        log_text = "\n".join(tail_lines) if tail_lines else "(Empty log file)"
                        extracted_logs[log_name] = self.trim_text(
                            log_text, self._config.slm_log_chars
                        )
                        #print("log_text=");
                        #print(log_lines);
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
                        tail_lines = log_lines[-self._config.slm_log_lines :]
                        log_name = os.path.basename(member.name)
                        log_text = "\n".join(tail_lines) if tail_lines else "(Empty log file)"
                        extracted_logs[log_name] = self.trim_text(
                            log_text, self._config.slm_log_chars
                        )
                        #print("log_text=");
                        #print(log_lines);
            else:
                logger.warning("Unsupported archive format received; expected zip or tar archive")
        except Exception as error:
            logger.error("Failed to extract log archive: %s", error)
        return extracted_logs

    @staticmethod
    def trim_text(text: str, max_chars: int) -> str:
        if len(text) <= max_chars:
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


class SlmClient:
    def __init__(self, config: ServerConfig) -> None:
        self._config = config

    async def request_diagnostic(self, prompt: str, history_event_count: int) -> str:
        logger.info("Dispatching diagnostic prompt to SLM (%s)...", self._config.slm_model)
        self._log_prompt_process_logs(prompt)

        payload = {
            "model": self._config.slm_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_ctx": 4096,
            },
        }
        logger.info(
            "Prepared SLM payload for model=%s prompt_chars=%d history_events=%d",
            self._config.slm_model,
            len(prompt),
            history_event_count,
        )

        candidate_urls = self._build_candidate_urls()
        logger.info("SLM endpoint candidates: %s", ", ".join(candidate_urls))
        for candidate_url in candidate_urls:
            if self._probe_tcp_endpoint(candidate_url):
                break

        if httpx is not None:
            for candidate_url in candidate_urls:
                try:
                    timeout = httpx.Timeout(
                        connect=5.0,
                        write=15.0,
                        read=self._config.slm_timeout_sec,
                        pool=5.0,
                    )
                    async with httpx.AsyncClient(
                        timeout=timeout,
                        trust_env=not self._should_bypass_proxy(candidate_url),
                    ) as client:
                        return await self._post_with_httpx(client, candidate_url, payload)
                except Exception as error:
                    logger.warning(
                        "httpx request to SLM failed for %s: %s: %r",
                        candidate_url,
                        type(error).__name__,
                        error,
                    )

        last_error: Optional[Exception] = None
        for candidate_url in candidate_urls:
            try:
                return self._post_with_urllib(candidate_url, payload)
            except Exception as error:
                last_error = error
                logger.warning(
                    "urllib request to SLM failed for %s: %s: %r",
                    candidate_url,
                    type(error).__name__,
                    error,
                )

        if last_error is not None:
            return (
                "[SLM Connection Failed] Could not connect to any SLM endpoint "
                f"derived from {self._config.slm_api_url}: {last_error}. Ensure Ollama or local LLM server is running."
            )
        return (
            "[SLM Connection Failed] Could not connect to any SLM endpoint "
            f"derived from {self._config.slm_api_url}. Ensure Ollama or local LLM server is running."
        )

    def _build_candidate_urls(self) -> List[str]:
        parsed_url = urlparse(self._config.slm_api_url)
        path = parsed_url.path or "/api/generate"
        port = parsed_url.port or 11434
        scheme = parsed_url.scheme or "http"

        candidate_hosts = [parsed_url.hostname or "localhost"]
        for fallback_host in ("ollama", "host.docker.internal", "127.0.0.1", "localhost"):
            if fallback_host not in candidate_hosts:
                candidate_hosts.append(fallback_host)
        return [f"{scheme}://{host}:{port}{path}" for host in candidate_hosts]

    def _probe_tcp_endpoint(self, url: str) -> bool:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname or "localhost"
        port = parsed_url.port or 11434

        try:
            resolved_entries = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
            resolved_hosts = sorted({entry[4][0] for entry in resolved_entries})
            logger.info("Resolved SLM host %s:%s to %s", hostname, port, ", ".join(resolved_hosts))
        except OSError as error:
            logger.warning("Failed to resolve SLM host %s:%s: %s: %r", hostname, port, type(error).__name__, error)
            return False

        last_error: Optional[OSError] = None
        for family, socket_type, protocol, _, socket_address in resolved_entries:
            tcp_socket = socket.socket(family, socket_type, protocol)
            tcp_socket.settimeout(3.0)
            try:
                tcp_socket.connect(socket_address)
                logger.info("TCP connect to SLM endpoint succeeded: %s", socket_address)
                return True
            except OSError as error:
                last_error = error
            finally:
                tcp_socket.close()

        logger.warning(
            "TCP connect to SLM endpoint failed for %s:%s: %s: %r",
            hostname,
            port,
            type(last_error).__name__,
            last_error,
        )
        return False

    async def _post_with_httpx(self, client: Any, url: str, payload: Dict[str, Any]) -> str:
        response = await client.post(
            url,
            content=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        if response.status_code == 200:
            return response.json().get("response", "No response generated by SLM.")
        return f"SLM API Error {response.status_code}: {response.text}"

    def _post_with_urllib(self, url: str, payload: Dict[str, Any]) -> str:
        import urllib.request

        data_bytes = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
        )

        if self._should_bypass_proxy(url):
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            response = opener.open(request, timeout=self._config.slm_timeout_sec)
        else:
            response = urllib.request.urlopen(request, timeout=self._config.slm_timeout_sec)

        with response as raw_response:
            if raw_response.status == 200:
                parsed_response = json.loads(raw_response.read().decode("utf-8"))
                return parsed_response.get("response", "No response generated by SLM.")
            return f"SLM API Error {raw_response.status}"

    @staticmethod
    def _log_prompt_process_logs(prompt: str) -> None:
        if "$process_logs" in prompt:
            logger.warning("Outgoing SLM prompt still contains unresolved $process_logs placeholder")
            return

        process_logs_marker = "## Process Logs"
        next_section_marker = "## Ollama Server Logs"
        process_logs_start = prompt.find(process_logs_marker)
        if process_logs_start == -1:
            logger.warning("Outgoing SLM prompt does not contain a process logs section")
            return

        process_logs_end = prompt.find(next_section_marker, process_logs_start)
        if process_logs_end == -1:
            process_logs_end = len(prompt)

        process_logs_section = prompt[process_logs_start:process_logs_end].strip()
        logger.info("Outgoing SLM process logs section:\n%s", process_logs_section)

    @staticmethod
    def _should_bypass_proxy(url: str) -> bool:
        hostname = (urlparse(url).hostname or "").lower()
        return hostname in {"ollama", "localhost", "127.0.0.1", "host.docker.internal"}


class AiDiagnosticServer:
    def __init__(
        self,
        config: ServerConfig,
        prompt_builder: DiagnosticPromptBuilder,
        slm_client: SlmClient,
    ) -> None:
        self._config = config
        self._prompt_builder = prompt_builder
        self._slm_client = slm_client
        self._session = DiagnosticSession()
        self._event_handlers: Dict[str, Callable[[Dict[str, Any]], Awaitable[None]]] = {
            "onUpdateState": self._handle_update_state,
            "onUpdateProgress": self._handle_update_progress,
            "onUpdateError": self._handle_update_error,
             ARCHIVE_EVENT_NAME: self._handle_diagnostic_archive,
            "onCancelUpdResult": self._handle_result_event,
            "onCompleteUpdResult": self._handle_result_event,
        }

    async def serve(self) -> None:
        logger.info(
            "Starting AI Diagnostic Server on %s:%s (Model: %s)",
            self._config.tcp_host,
            self._config.tcp_port,
            self._config.slm_model,
        )
        logger.info(
            "Connected SLM Endpoint: %s (Model: %s)",
            self._config.slm_api_url,
            self._config.slm_model,
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
            logger.error("STATE ERROR DETECTED! Triggering initial SLM analysis...")
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

            archive_logs = self._prompt_builder.extract_logs_from_archive(archive_bytes)
            direct_logs = self._extract_direct_process_logs(event_data)
            process_logs = self._merge_process_logs(archive_logs, direct_logs)
            latest_error_event = self._session.find_latest_diagnostic_event(event_data)
            await self._generate_diagnostic_report(
                latest_error_event,
                instructions=self._extract_client_instructions(event_data),
                process_logs=process_logs,
                title="         SLM ROOT CAUSE DIAGNOSIS (WITH PROCESS LOGS)",
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
        title: str = "                SLM AUTOMATED ROOT CAUSE DIAGNOSIS",
        path_label: str = "Report File Created",
    ) -> None:
        recent_history = self._session.recent_events()
        logger.info(
            "Entering query_slm for event=%s errorCode=%s history_events=%d process_logs=%d",
            trigger_event.get("event", "unknown"),
            trigger_event.get("errorCode", trigger_event.get("state", "n/a")),
            len(recent_history),
            len(process_logs or {}),
        )
        self._log_process_logs(process_logs)

        prompt = self._prompt_builder.build_prompt(
            instructions,
            trigger_event,
            recent_history,
            process_logs,
        )
        report_text = await self._slm_client.request_diagnostic(prompt, len(recent_history))
        
        print("*****report text**********")
        print(report_text)
        print("***************")
        report_text = self._enforce_report_error_code(report_text, process_logs)
        next_steps_text = await self._request_enum_next_steps(report_text, process_logs, len(recent_history))
        report_path = self._save_report_file(report_text)
        
        self._print_report(title, report_text, report_path, path_label, next_steps_text)
        recovery_plan_text = await self._request_recovery_plan(report_text, next_steps_text, process_logs, len(recent_history))
        self._print_recovery_plan(recovery_plan_text)
        

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

        #logger.info(
        #    "process_logs data:\n%s",
        #    json.dumps(non_empty_logs, indent=2, ensure_ascii=False),
        #)

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
        match = re.search(rf'(?mi)^\s*{re.escape(label)}\s*:\s*(.+)$', report_text)
        if match is None:
            return "N/A"
        version_value = match.group(1).strip()
        return version_value or "N/A"

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

    async def _request_enum_next_steps(
        self,
        report_text: str,
        process_logs: Optional[Dict[str, str]],
        history_event_count: int,
    ) -> Optional[str]:
        error_code = self._extract_error_code_from_report(report_text)
        error_enum_name = self._resolve_error_enum_name(error_code)
        if error_enum_name is None:
            return None

        next_steps_prompt = self._prompt_builder.build_next_steps_prompt(
            error_enum_name,
            process_logs,
        )
        next_steps_response = await self._slm_client.request_diagnostic(next_steps_prompt, history_event_count)
        print(next_steps_response)
        print("*********")
        return self._normalize_next_steps_response(
            next_steps_response,
            error_enum_name,
            process_logs,
        )

    async def _request_recovery_plan(
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
        from_version = self._resolve_version_value(report_text, process_logs, "FROM_VERSION")
        to_version = self._resolve_version_value(report_text, process_logs, "TO_VERSION")
        evidence_text = self._extract_evidence_text(next_steps_text, process_logs)

        recovery_prompt = self._prompt_builder.build_recovery_plan_prompt(
            error_code,
            error_enum_name,
            failure_reason,
            evidence_text,
            package_type,
            from_version,
            to_version,
        )

        #print("Recovery prompt")
        #print(recovery_prompt)
        recovery_response = await self._slm_client.request_diagnostic(recovery_prompt, history_event_count)
        print("***************")
        print(recovery_response)
        print("******************")
        return self._normalize_recovery_plan_response(recovery_response, error_code, error_enum_name)

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
            f"recovery_action: {recovery_action}",
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
        error_code = AiDiagnosticServer._extract_error_code_from_report(report_text)
        error_enum_name = AiDiagnosticServer._resolve_error_enum_name(error_code)

        print("\n" + REPORT_SEPARATOR)
        print(title)
        print(REPORT_SEPARATOR)
        print(report_text)
        if error_code is not None:
            print(f"Resolved Errorcode: {error_code}")
        if error_enum_name is not None:
            print(f"Resolved Error Enum: {error_enum_name}")
        if next_steps_text:
            print(REPORT_SEPARATOR)
            print("SLM ENUM NEXT STEPS")
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
        print("SLM RECOVERY PLAN")
        print(REPORT_SEPARATOR)
        print(recovery_plan_text)
        print(REPORT_SEPARATOR + "\n")


async def main() -> None:
    config = ServerConfig.from_env()
    server = AiDiagnosticServer(config, DiagnosticPromptBuilder(config), SlmClient(config))
    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("AI Server shutting down.")
        sys.exit(0)
