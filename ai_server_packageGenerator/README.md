# AI Server Package Generator Variant

This folder contains a TCP-based SWUpdate diagnostic server integrated with a separate package-generation service. The diagnostic agent runs on port `9000`; the package generator listens on port `9001`.

## Services

- `UpdateAgent.py` receives newline-delimited JSON SWUpdate events, processes diagnostic archives, and coordinates root-cause analysis, detailed analysis, recovery planning, and package generation.
- `PackageGenerator.py` accepts package-generation requests on `PKG_GEN_HOST` / `PKG_GEN_PORT` (defaults: `0.0.0.0:9001`). The agent connects to this service using `PKG_GEN_HOST` / `PKG_GEN_PORT` (defaults: `127.0.0.1:9001`).
- `ModelConnector.py`, `RootcauseAnalyser.py`, `DetailedAnalyser.py`, and `RecoveryPlanner.py` implement model access and diagnostic/recovery stages.
- `prompts/` contains the SLM, error next-step, and recovery instructions; `errorconfig.aidl` provides error-code mappings.

## Run with Docker Compose

From this directory:

```sh
docker compose up --build
```

Compose starts Ollama, pulls `gemma3:4b`, runs the diagnostic agent on host port `9000`, and runs `swu_package_generator` on host port `9001`. Model data is kept in the `ollama_models` Docker volume. Stop the stack with `Ctrl+C`; use `docker compose down` to remove its containers and network while retaining the named model volume.

The diagnostic agent reads `AI_SERVER_HOST` and `AI_SERVER_PORT` for its listener, `PKG_GEN_HOST` and `PKG_GEN_PORT` for the package service, and `AIMODEL_API_URL`, `AIMODEL_MODEL`, `AIMODEL_TIMEOUT_SEC`, `AIMODEL_HISTORY_EVENTS`, `AIMODEL_LOG_LINES`, `AIMODEL_LOG_CHARS`, and `AIMODEL_PROMPT_FILE` for model behavior. The checked-in Compose file sets `SLM_API_URL` / `SLM_MODEL`, while `UpdateAgent.py` reads `AIMODEL_API_URL` / `AIMODEL_MODEL`; configure the latter names for the running AI service. In Docker, point `AIMODEL_API_URL` at `http://ollama:11434/api/generate`, not `localhost`.

## Package Generator Protocol

The service handles one JSON request per TCP connection. The request uses the `generate_package` command:

```json
{
  "request_id": "req-123",
  "command": "generate_package",
  "params": {
    "verify_version": true,
    "verification_type": "Upgrade",
    "from_version": "qpr1_a12_int_2026.19.0",
    "to_version": "qpr1_a12_int_2026.20.0",
    "package_type": "delta"
  }
}
```

The response is newline-delimited JSON and includes the original `request_id` and a `result` with `status` and `package_name`. The handler accepts the misspelled `to_verssion` parameter as a compatibility fallback for `to_version`.

**Simulation only:** `PackageGenerator.py` waits to simulate work, chooses from a hard-coded set of versions, and returns a ZIP-style filename. It does not build or write an update package. Its reported package name is a simulated result, not an artifact to flash.

## Key Files

- `UpdateAgent.py`: diagnostic TCP server and package-generator client.
- `PackageGenerator.py`: package-generation TCP service and simulated result.
- `docker-compose.yml`, `Dockerfile`: multi-container deployment.
- `AI_REPORT.md`: package-generator investigation notes.
