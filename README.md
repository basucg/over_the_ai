# AI Service Client and SWUpdate Diagnostic Server

This module pairs an Android SWUpdate/FOTA client with Python diagnostic server variants. The Android client receives Binder callbacks, sends update information over TCP, and responds to server requests for platform details, log artifacts, and OTA logs. A selected server variant receives those messages and runs the diagnostic/model workflow.

## Documentation

- [Android client guide](README_ANDROID.md): Android build, init startup, endpoint configuration, and Binder/TCP responsibilities.
- [Package-generator server guide](server/ai_server_packageGenerator/README.md): diagnostic server plus the package-generation TCP service.
- [Mock-device server guide](server/ai_server_DeviceSimulationUsingMock/README.md): server variant with a mock Android event client and sample archive.

## End-to-end flow

1. `ai_service_client` connects to `FcSwUpdateSrv` and registers update callbacks. It also connects to the FOTA HMI Binder service for OTA HMI events and log requests.
2. `TcpNotificationSender` exchanges newline-delimited JSON with the diagnostic server on TCP port `9000`.
3. The server tracks update events, accepts diagnostic archives, and runs root-cause analysis, detailed analysis, and recovery planning using an Ollama-compatible model endpoint.
4. Both Compose variants start a package-generation service on TCP port `9001`; the diagnostic agent can request a simulated package result.

## Choose and run a server variant

Run one Compose project at a time. The variants reuse Docker container names and host ports.

For the package-generator variant:

```sh
cd vendor/bosch/services/ai_service_client/server/ai_server_packageGenerator
docker compose up --build
```

For the mock-device variant:

```sh
cd vendor/bosch/services/ai_service_client/server/ai_server_DeviceSimulationUsingMock
docker compose up --build
```

Both Compose projects expose the diagnostic TCP listener on `9000`, Ollama on `11434`, and the package-generator endpoint on `9001`. The model initialization service pulls `gemma3:4b` into a persistent Docker volume.

To simulate client traffic with the mock variant, run this from a second terminal in its directory:

```sh
python3 mock_client_test.py --host 127.0.0.1 --port 9000
```

The mock sends representative update-state/progress messages and the bundled `version_downgrade.zip` archive. It does not interact with a physical target or perform an update.

## Configuration notes

The Android init service currently targets `127.0.0.1:9000`; change the `-ip` argument in `ai_service_client.rc` to the server's reachable address when the server runs elsewhere.

Both Python `UpdateAgent.py` variants read `AIMODEL_API_URL` and `AIMODEL_MODEL` for their model connection, while the checked-in Compose files set `SLM_API_URL` and `SLM_MODEL`. Configure `AIMODEL_API_URL` and `AIMODEL_MODEL` on the diagnostic service; inside the Compose network the Ollama URL is `http://ollama:11434/api/generate`. The code's `localhost` default would point back to the AI server container.

The package-generation endpoint currently simulates processing and returns a package filename; it does not create an update archive. Treat its response as a test result, not a flashable artifact.

For Android target build and startup details, see [README_ANDROID.md](README_ANDROID.md). For each server's files and protocol, see the variant guides above.
