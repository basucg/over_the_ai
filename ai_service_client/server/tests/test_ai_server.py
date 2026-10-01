import io
import json
import tarfile
import sys
import tempfile
import asyncio
from contextlib import redirect_stdout
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import ai_server


class DiagnosticPromptBuilderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = ai_server.ServerConfig(
            tcp_host="0.0.0.0",
            tcp_port=9000,
            slm_api_url="http://ollama:11434/api/generate",
            slm_model="gemma3:1b",
            slm_timeout_sec=180.0,
            slm_history_events=2,
            slm_log_lines=3,
            slm_log_chars=40,
            prompt_template_path=str(ROOT / "prompts" / "slm_prompt.txt"),
            diagnostic_dir="/tmp/diagnostics",
            reports_dir="/tmp/reports",
        )
        self.builder = ai_server.DiagnosticPromptBuilder(self.config)

    def test_trim_text_appends_truncation_marker(self) -> None:
        result = self.builder.trim_text("abcdefghijklmnop", 8)
        self.assertEqual(result, "abcdefgh\n...(truncated)")

    def test_build_log_section_returns_placeholder_when_empty(self) -> None:
        result = self.builder.build_log_section(None)
        self.assertEqual(result, ai_server.NO_PROCESS_LOGS_TEXT)

    def test_summarize_event_keeps_relevant_fields(self) -> None:
        event = {
            "event": "onUpdateError",
            "errorCode": 28,
            "errorName": "ERROR_IMAGE_FLASHING",
            "moduleName": "system_a",
            "ignored": "value",
        }

        result = self.builder.summarize_event(event)

        self.assertEqual(
            result,
            {
                "event": "onUpdateError",
                "errorCode": 28,
                "errorName": "ERROR_IMAGE_FLASHING",
                "moduleName": "system_a",
            },
        )

    def test_build_prompt_includes_summarized_event_and_history(self) -> None:
        error_event = {
            "event": "onUpdateError",
            "errorCode": 28,
            "errorName": "ERROR_IMAGE_FLASHING",
            "timestamp": 1,
            "details": "ignored",
        }
        history = [
            {"event": "onUpdateState", "state": 5, "stateName": "RUNNING"},
            {"event": "onUpdateProgress", "moduleName": "system_a"},
            {"event": "onUpdateError", "errorCode": 99},
        ]
        process_logs = {"da3_app_fcswupdate.log": "[ERROR] flashing failed errorCode=28"}

        prompt = self.builder.build_prompt(None, error_event, history, process_logs)

        self.assertIn("## Failure Event", prompt)
        self.assertIn("ERROR_IMAGE_FLASHING", prompt)
        self.assertIn("## Recent History", prompt)
        self.assertIn("## Process Logs", prompt)
        self.assertIn("[ERROR] flashing failed errorCode=28", prompt)

    def test_prompt_template_is_loaded_from_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template_path = Path(temp_dir) / "prompt.txt"
            template_path.write_text("Template: $failure_event", encoding="utf-8")

            config = ai_server.ServerConfig(
                tcp_host="0.0.0.0",
                tcp_port=9000,
                slm_api_url="http://ollama:11434/api/generate",
                slm_model="gemma3:1b",
                slm_timeout_sec=180.0,
                slm_history_events=2,
                slm_log_lines=3,
                slm_log_chars=40,
                prompt_template_path=str(template_path),
                diagnostic_dir="/tmp/diagnostics",
                reports_dir="/tmp/reports",
            )

            builder = ai_server.DiagnosticPromptBuilder(config)

            prompt = builder.build_prompt(
                None,
                {"event": "onUpdateError", "errorCode": 7},
                [],
                None,
            )

            self.assertTrue(prompt.startswith("Template:"))
            self.assertIn("\"errorCode\": 7", prompt)

    def test_prompt_template_accepts_quoted_equals_error_code_pattern(self) -> None:
        template = (ROOT / "prompts" / "slm_prompt.txt").read_text(encoding="utf-8")

        self.assertIn('`errorCode"=<number>`', template)
        self.assertIn('`"errorCode"=<number>`', template)

    def test_extract_logs_from_archive_returns_tail_of_logs(self) -> None:
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
            content = (
                b"line1\nline2\nline3\nline4\nline5\n"
            )
            info = tarfile.TarInfo(name="update_engine.log")
            info.size = len(content)
            tar.addfile(info, io.BytesIO(content))

        logs = self.builder.extract_logs_from_archive(buffer.getvalue())

        self.assertIn("update_engine.log", logs)
        self.assertIn("line3", logs["update_engine.log"])
        self.assertNotIn("line1", logs["update_engine.log"])

    def test_build_next_steps_prompt_includes_enum_instructions_and_logs(self) -> None:
        prompt = self.builder.build_next_steps_prompt(
            "ERROR_UNKNOWN",
            {"da3_app_fcswupdate.log": "01 ERROR_UNKNOWN"},
        )

        self.assertIn("Resolved Error Enum:\nERROR_UNKNOWN", prompt)
        self.assertIn("# Error Enum To Next Diagnostic Steps", prompt)
        self.assertIn("01 ERROR_UNKNOWN", prompt)
        self.assertIn("Return exactly 3 sections.", prompt)
        self.assertIn("do not exceed 8 log lines", prompt)
        self.assertIn("every evidence line must contain [ERROR]", prompt)

    def test_build_recovery_plan_prompt_includes_prompt_inputs(self) -> None:
        prompt = self.builder.build_recovery_plan_prompt(
            "8",
            "ERROR_UNKNOWN",
            "Flash failed during system_a write",
            "[da3_app_fcswupdate.log] [ERROR] da3 failure",
            "DELTA PACKAGE",
            "2026.17.0",
            "2026.18.0",
        )

        self.assertIn("Instruction File:\n# Recovery Plan Classification", prompt)
        self.assertIn("Error Number:\n8 (ERROR_UNKNOWN)", prompt)
        self.assertIn("Failure Reason:\nFlash failed during system_a write", prompt)
        self.assertIn("Evidence:\n[da3_app_fcswupdate.log] [ERROR] da3 failure", prompt)
        self.assertIn("Package Type:\nDELTA PACKAGE", prompt)
        self.assertIn("FROM_VERSION: 2026.17.0", prompt)
        self.assertIn("TO_VERSION: 2026.18.0", prompt)
        self.assertIn("recovery_action:", prompt)
        self.assertIn("detailed_recovery_plan:", prompt)


class DiagnosticSessionTests(unittest.TestCase):
    def test_find_latest_diagnostic_event_prefers_latest_error(self) -> None:
        session = ai_server.DiagnosticSession()
        session.record_event({"event": "onUpdateState", "state": 5})
        session.record_event({"event": "onUpdateError", "errorCode": 28})
        fallback = {"event": "fallback"}

        result = session.find_latest_diagnostic_event(fallback)

        self.assertEqual(result, {"event": "onUpdateError", "errorCode": 28})


class DiagnosticReportErrorCodeTests(unittest.TestCase):
    def test_extract_error_code_from_da3_log_handles_quoted_equals_pattern(self) -> None:
        process_logs = {
            "da3_app_fcswupdate.log": "line1\nline2 errorCode\"=8\nline3",
            "update_engine.log": "errorCode=99",
        }

        result = ai_server.AiDiagnosticServer._extract_error_code_from_process_logs(process_logs)

        self.assertEqual(result, "8")

    def test_extract_error_code_ignores_non_da3_logs(self) -> None:
        process_logs = {
            "downloadpipe.log": "errorCode=8",
        }

        result = ai_server.AiDiagnosticServer._extract_error_code_from_process_logs(process_logs)

        self.assertIsNone(result)

    def test_enforce_report_error_code_replaces_na_placeholder(self) -> None:
        report_text = "3. Errorcode: errorCode:N/A (Not present in da3_app_fcswupdate)"
        process_logs = {
            "da3_app_fcswupdate.log": "errorCode\"=8",
        }

        result = ai_server.AiDiagnosticServer._enforce_report_error_code(report_text, process_logs)

        self.assertEqual(result, "3. Errorcode:8 (ERROR_UNKNOWN)")

    def test_enforce_report_error_code_normalizes_existing_value(self) -> None:
        report_text = "3. Errorcode: errorCode:12"
        process_logs = {
            "da3_app_fcswupdate.log": "errorCode\"=8",
        }

        result = ai_server.AiDiagnosticServer._enforce_report_error_code(report_text, process_logs)

        self.assertEqual(result, "3. Errorcode:8 (ERROR_UNKNOWN)")

    def test_enforce_report_error_code_adds_enum_to_existing_report_value(self) -> None:
        report_text = "3. Errorcode:12"

        result = ai_server.AiDiagnosticServer._enforce_report_error_code(report_text, None)

        self.assertEqual(result, "3. Errorcode:12 (ERROR_METAINFO_PARSE)")

    def test_resolve_error_enum_name_uses_aidl_mapping(self) -> None:
        result = ai_server.AiDiagnosticServer._resolve_error_enum_name("8")

        self.assertEqual(result, "ERROR_UNKNOWN")

    def test_print_report_outputs_embedded_error_details(self) -> None:
        output_buffer = io.StringIO()

        with redirect_stdout(output_buffer):
            ai_server.AiDiagnosticServer._print_report(
                "title",
                "3. Errorcode:8 (ERROR_UNKNOWN)",
                "",
                "Report File Created",
            )

        output = output_buffer.getvalue()

        self.assertIn("3. Errorcode:8 (ERROR_UNKNOWN)", output)
        self.assertIn("Resolved Errorcode: 8", output)
        self.assertIn("Resolved Error Enum: ERROR_UNKNOWN", output)

    def test_normalize_next_steps_response_preserves_evidence_section_from_response(self) -> None:
        raw_response = (
            "1. Failure Reason: Flash failed\n"
            "2. Evidence:\nprovided line 1\nprovided line 2\n"
            "3. Next Steps: Check update_engine_log"
        )
        process_logs = {
            "update_engine.log": "\n".join(
                ["[INFO] skip"]
                + [f"[ERROR] issue {index}" for index in range(1, 11)]
            )
        }

        result = ai_server.AiDiagnosticServer._normalize_next_steps_response(
            raw_response,
            "ERROR_IMAGE_FLASHING",
            process_logs,
        )

        self.assertIn("1. Failure Reason: Flash failed", result)
        self.assertIn("3. Next Steps: Check update_engine_log", result)
        self.assertIn("2. Evidence:\nprovided line 1\nprovided line 2", result)
        self.assertNotIn("[update_engine.log] [ERROR] issue 1", result)

    def test_normalize_recovery_plan_response_falls_back_to_resolved_error(self) -> None:
        result = ai_server.AiDiagnosticServer._normalize_recovery_plan_response(
            "RETRY_UPDATE",
            "8",
            "ERROR_UNKNOWN",
        )

        self.assertEqual(
            result,
            "error_code: 8 (ERROR_UNKNOWN)\nrecovery_action: RETRY_UPDATE\ndetailed_recovery_plan: RETRY_UPDATE",
        )

    def test_normalize_recovery_plan_response_enforces_mapped_action_for_known_error(self) -> None:
        result = ai_server.AiDiagnosticServer._normalize_recovery_plan_response(
            "error_code: ERROR_IMAGE_CHECKSUM\nrecovery_action: RETRY_UPDATE",
            "8",
            "ERROR_UNKNOWN",
        )

        self.assertEqual(
            result,
            "error_code: ERROR_IMAGE_CHECKSUM\nrecovery_action: REGENERATE_PACKAGE\ndetailed_recovery_plan: REGENERATE_PACKAGE",
        )

    def test_extract_failure_reason_prefers_next_steps_section(self) -> None:
        result = ai_server.AiDiagnosticServer._extract_failure_reason(
            "1. Failure Reason: Flash failed during activation\n2. Evidence:\n[log] [ERROR] fail\n3. Next Steps: Retry",
            "ERROR_UNKNOWN",
        )

        self.assertEqual(result, "Flash failed during activation")

    def test_resolve_version_value_falls_back_to_da3_logs(self) -> None:
        process_logs = {
            "da3_app_fcswupdate.log": (
                "CUSTOMER_VERSION: qpr1_a12_int_2026.17.0\n"
                "updateBuildLabel from bosch.xml: [qpr1_a12_int_2026.18.0]"
            )
        }

        from_version = ai_server.AiDiagnosticServer._resolve_version_value(
            "1. Package Type: DELTA PACKAGE\n3. Errorcode:8",
            process_logs,
            "FROM_VERSION",
        )
        to_version = ai_server.AiDiagnosticServer._resolve_version_value(
            "1. Package Type: DELTA PACKAGE\n3. Errorcode:8",
            process_logs,
            "TO_VERSION",
        )

        self.assertEqual(from_version, "qpr1_a12_int_2026.17.0")
        self.assertEqual(to_version, "qpr1_a12_int_2026.18.0")

    def test_extract_evidence_text_prefers_next_steps_section_without_reformatting(self) -> None:
        result = ai_server.AiDiagnosticServer._extract_evidence_text(
            "1. Failure Reason: Flash failed\n2. Evidence:\nline A\nline B\n3. Next Steps: Retry",
            {"update_engine.log": "[ERROR] fallback"},
        )

        self.assertEqual(result, "line A\nline B")


class RecordingSlmClient:
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.prompts: list[str] = []

    async def request_diagnostic(self, prompt: str, history_event_count: int) -> str:
        self.prompts.append(prompt)
        return self.responses.pop(0)


class EnumNextStepsIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_generate_report_requests_next_steps_with_resolved_enum_and_logs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ai_server.ServerConfig(
                tcp_host="0.0.0.0",
                tcp_port=9000,
                slm_api_url="http://ollama:11434/api/generate",
                slm_model="gemma3:1b",
                slm_timeout_sec=180.0,
                slm_history_events=2,
                slm_log_lines=3,
                slm_log_chars=200,
                prompt_template_path=str(ROOT / "prompts" / "slm_prompt.txt"),
                diagnostic_dir=temp_dir,
                reports_dir=temp_dir,
            )
            prompt_builder = ai_server.DiagnosticPromptBuilder(config)
            slm_client = RecordingSlmClient(
                [
                    "1. Package Type: DELTA PACKAGE\n2. Version Information:\n   FROM_VERSION: 2026.17.0\n   TO_VERSION: 2026.18.0\n3. Errorcode:8",
                    "unstructured log dump\nsecond line",
                    "error_code: ERROR_IMAGE_FLASHING\nrecovery_action: RETRY_UPDATE\ndetailed_recovery_plan: Retry flashing after validating media and update prerequisites.",
                ]
            )
            server = ai_server.AiDiagnosticServer(config, prompt_builder, slm_client)  # type: ignore[arg-type]
            process_logs = {
                "da3_app_fcswupdate.log": "time ERROR_UNKNOWN errorCode\"=8\n[ERROR] da3 failure",
                "update_engine.log": "[INFO] ignore\n[ERROR] engine failure\n[ERROR] retry failed",
            }

            output_buffer = io.StringIO()
            with redirect_stdout(output_buffer):
                await server._generate_diagnostic_report(
                    {"event": "onUpdateError", "errorCode": 8},
                    process_logs=process_logs,
                )

            output = output_buffer.getvalue()

            self.assertEqual(len(slm_client.prompts), 3)
            self.assertIn("Resolved Error Enum:\nERROR_UNKNOWN", slm_client.prompts[1])
            self.assertIn("# Error Enum To Next Diagnostic Steps", slm_client.prompts[1])
            self.assertIn("time ERROR_UNKNOWN errorCode\"=8", slm_client.prompts[1])
            self.assertIn("Instruction File:\n# Recovery Plan Classification", slm_client.prompts[2])
            self.assertIn("Error Number:\n8 (ERROR_UNKNOWN)", slm_client.prompts[2])
            self.assertIn("Failure Reason:\nERROR_UNKNOWN", slm_client.prompts[2])
            self.assertIn(
                "Evidence:\n[da3_app_fcswupdate.log] [ERROR] da3 failure\n[update_engine.log] [ERROR] engine failure\n[update_engine.log] [ERROR] retry failed",
                slm_client.prompts[2],
            )
            self.assertIn("Package Type:\nDELTA PACKAGE", slm_client.prompts[2])
            self.assertIn("FROM_VERSION: 2026.17.0", slm_client.prompts[2])
            self.assertIn("TO_VERSION: 2026.18.0", slm_client.prompts[2])
            self.assertIn("SLM ENUM NEXT STEPS", output)
            self.assertIn("1. Failure Reason: ERROR_UNKNOWN", output)
            self.assertIn("2. Evidence:", output)
            self.assertIn("[da3_app_fcswupdate.log] [ERROR] da3 failure", output)
            self.assertIn("[update_engine.log] [ERROR] engine failure", output)
            self.assertNotIn("[INFO] ignore", output)
            self.assertIn("3. Next Steps: unstructured log dump", output)
            self.assertIn("SLM RECOVERY PLAN", output)
            self.assertIn("error_code: ERROR_IMAGE_FLASHING", output)
            self.assertIn("recovery_action: RETRY_UPDATE", output)
            self.assertIn("detailed_recovery_plan: Retry flashing after validating media and update prerequisites.", output)


if __name__ == "__main__":
    unittest.main()
