# AI Server Device Simulation with Mock Client

This folder is a self-contained server variant for exercising the Android-to-server diagnostic flow without connecting an Android target. `mock_client_test.py` sends representative update events and a bundled sample archive to the diagnostic server over TCP.

## Start the Stack

From this directory:

```sh
docker compose up --build
```

Compose starts Ollama and pulls `gemma3:4b`, exposes the diagnostic server at TCP port `9000`, and starts the package-generator service at TCP port `9001`. The model is stored in the `ollama_models` Docker volume. Run only one of the sibling server Compose stacks at a time because they share container names and host ports.

The checked-in Compose file sets `SLM_API_URL` / `SLM_MODEL`, but `UpdateAgent.py` reads `AIMODEL_API_URL` / `AIMODEL_MODEL`. Configure the `AIMODEL_*` variables on the diagnostic service; inside the Compose network, use `http://ollama:11434/api/generate` for `AIMODEL_API_URL`.

## Send Simulated Device Events

With the stack running, open a second terminal in this directory and run:

```sh
python3 mock_client_test.py
```

The script accepts `--host` and `--port` options; defaults come from `AI_SERVER_HOST` and `AI_SERVER_PORT` (defaulting to `127.0.0.1:9000`). For example:

```sh
python3 mock_client_test.py --host 127.0.0.1 --port 9000
```

The mock sends `onUpdateState`, `onUpdateProgress`, and `swUpdateDiagnosticArchive` events, with a base64-encoded copy of `version_downgrade.zip` and decoded process logs. It does not send a live Binder callback or perform an update on a device. The script prints archive members for inspection before sending the event stream.

## Components

- `UpdateAgent.py`: receives client events and orchestrates diagnosis and recovery.
- `mock_client_test.py`: simulated Android TCP client.
- `version_downgrade.zip`: sample diagnostic archive used by the mock client.
- `PackageGenerator.py`: simulated package-generation endpoint on port `9001`.
- `ModelConnector.py`, `RootcauseAnalyser.py`, `DetailedAnalyser.py`, `RecoveryPlanner.py`: model and diagnostic stages.
- `prompts/`, `errorconfig.aidl`: prompt templates and error-code mapping.
- `docker-compose.yml`, `Dockerfile`: local deployment.
