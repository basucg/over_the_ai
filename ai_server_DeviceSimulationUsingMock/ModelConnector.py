#!/usr/bin/env python3
import json
import logging
import socket
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from urllib.parse import urlparse
import urllib.request

if TYPE_CHECKING:
    from UpdateAgent import ServerConfig

try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger("AIModelConnector")


class AIModelClient:
    def __init__(self, config: "ServerConfig") -> None:
        self._config = config

    async def request_analysis(self, prompt: str, history_event_count: int) -> str:
        logger.info("Dispatching diagnostic prompt to AI Model (%s)...", self._config.aimodel_model)
        self._log_prompt_process_logs(prompt)

        payload = {
            "model": self._config.aimodel_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_ctx": 4096,
            },
        }
        logger.info(
            "Prepared AI Model payload for model=%s prompt_chars=%d history_events=%d",
            self._config.aimodel_model,
            len(prompt),
            history_event_count,
        )

        candidate_urls = self._build_candidate_urls()
        logger.info("AI Model endpoint candidates: %s", ", ".join(candidate_urls))
        for candidate_url in candidate_urls:
            if self._probe_tcp_endpoint(candidate_url):
                break

        if httpx is not None:
            for candidate_url in candidate_urls:
                try:
                    timeout = httpx.Timeout(
                        connect=5.0,
                        write=15.0,
                        read=self._config.aimodel_timeout_sec,
                        pool=5.0,
                    )
                    async with httpx.AsyncClient(
                        timeout=timeout,
                        trust_env=not self._should_bypass_proxy(candidate_url),
                    ) as client:
                        return await self._post_with_httpx(client, candidate_url, payload)
                except Exception as error:
                    logger.warning(
                        "httpx request to AI Model failed for %s: %s: %r",
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
                    "urllib request to AI Model failed for %s: %s: %r",
                    candidate_url,
                    type(error).__name__,
                    error,
                )

        if last_error is not None:
            return (
                "[AI Model Connection Failed] Could not connect to any AI Model endpoint "
                f"derived from {self._config.aimodel_api_url}: {last_error}. Ensure Ollama or local LLM server is running."
            )
        return (
            "[AI Model Connection Failed] Could not connect to any AI Model endpoint "
            f"derived from {self._config.aimodel_api_url}. Ensure Ollama or local LLM server is running."
        )

    def _build_candidate_urls(self) -> List[str]:
        parsed_url = urlparse(self._config.aimodel_api_url)
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
            logger.info("Resolved AI Model host %s:%s to %s", hostname, port, ", ".join(resolved_hosts))
        except OSError as error:
            logger.warning("Failed to resolve AI Model host %s:%s: %s: %r", hostname, port, type(error).__name__, error)
            return False

        last_error: Optional[OSError] = None
        for family, socket_type, protocol, _, socket_address in resolved_entries:
            tcp_socket = socket.socket(family, socket_type, protocol)
            tcp_socket.settimeout(3.0)
            try:
                tcp_socket.connect(socket_address)
                logger.info("TCP connect to AI Model endpoint succeeded: %s", socket_address)
                return True
            except OSError as error:
                last_error = error
            finally:
                tcp_socket.close()

        logger.warning(
            "TCP connect to AI Model endpoint failed for %s:%s: %s: %r",
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
            return response.json().get("response", "No response generated by AI Model.")
        return f"AI Model API Error {response.status_code}: {response.text}"

    def _post_with_urllib(self, url: str, payload: Dict[str, Any]) -> str:
        data_bytes = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
        )

        if self._should_bypass_proxy(url):
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            response = opener.open(request, timeout=self._config.aimodel_timeout_sec)
        else:
            response = urllib.request.urlopen(request, timeout=self._config.aimodel_timeout_sec)

        with response as raw_response:
            if raw_response.status == 200:
                parsed_response = json.loads(raw_response.read().decode("utf-8"))
                return parsed_response.get("response", "No response generated by AI Model.")
            return f"AI Model API Error {raw_response.status}"

    @staticmethod
    def _log_prompt_process_logs(prompt: str) -> None:
        if "$process_logs" in prompt:
            logger.warning("Outgoing AI Model prompt still contains unresolved $process_logs placeholder")
            return

        process_logs_marker = "## Process Logs"
        next_section_marker = "## Ollama Server Logs"
        process_logs_start = prompt.find(process_logs_marker)
        if process_logs_start == -1:
            logger.warning("Outgoing AI Model prompt does not contain a process logs section")
            return

        process_logs_end = prompt.find(next_section_marker, process_logs_start)
        if process_logs_end == -1:
            process_logs_end = len(prompt)

        process_logs_section = prompt[process_logs_start:process_logs_end].strip()
        logger.info("Outgoing AI Model process logs section:\n%s", process_logs_section)

    @staticmethod
    def _should_bypass_proxy(url: str) -> bool:
        hostname = (urlparse(url).hostname or "").lower()
        return hostname in {"ollama", "localhost", "127.0.0.1", "host.docker.internal"}