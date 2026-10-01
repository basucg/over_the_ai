# AI Service Client & SLM Diagnostic Server

An end-to-end system for streaming automotive software update notifications from an **Android Target (`FcSwUpdateSrv`)** to a **Linux Docker Server** running a **Small Language Model (SLM)** for automated root cause diagnosis upon update failures.

```
┌──────────────────────────┐             ┌──────────────────────────────────┐
│      Android Target      │             │      Linux Host / Docker         │
│                          │             │                                  │
│  ┌────────────────────┐  │             │  ┌────────────────────────────┐  │
│  │   FcSwUpdateSrv    │  │             │  │ AI Diagnostic Server (Py)  │  │
│  └─────────┬──────────┘  │ Bidirection │  │ (Port 9000, Event Tracker) │  │
│            │ (Binder)    │ TCP Socket  │  └──────────────┬─────────────┘  │
│            ▼             │◀───────────▶│                 │ Prompt         │
│  ┌────────────────────┐  │ (JSON line) │                 ▼                │
│  │ ai_service_client  │  │             │  ┌────────────────────────────┐  │
│  └────────────────────┘  │             │  │   SLM Server (Ollama)      │  │
│                          │             │  │   (gemma3:12b)               │  │
│                          │             │  └────────────────────────────┘  │
└──────────────────────────┘             └──────────────────────────────────┘
```

---

## 1. Android Target (`ai_service_client`)

### Features & Workflow
- **Binder IPC Listener**: Implements `swu::FcSwUpdateSrv::BnUpdateCallback` to receive `onUpdateState`, `onUpdateProgress`, `onUpdateError`, `onCancelUpdResult`, and `onCompleteUpdResult`.
- **Error Notification**: On update failure (`onUpdateError`), immediately sends an error notification to the AI server.
- **Server-Driven Diagnostic APIs**:
  - **API 1 (`getSystemInformation` / `sendSystemInformation`)**: When the server requests system details (`request_system_details`), the client gathers `product_class` (e.g. `IVI`), `primary_os` (e.g. `Android`), and `secondary_os` (e.g. `["Linux"]`) and returns them in a structured JSON response.
  - **API 2 (`getRequiredFiles`)**: When the server requests specific log files based on the platform details (`request_artifacts` with tags such as `update_engine_logs`, `logcat_logs`, `update_persistent_logs`, `downloadpipe`), the client runs `logcat -d -s "<TAG>"` for each requested tag, packages them into a `.tar.gz` archive, base64-encodes the archive, and transmits it back to the AI server.
- **Bidirectional TCP Communication**: `TcpNotificationSender` manages background send queues and incoming server message dispatching.
- **Configurable Endpoint**:
  - Android system properties: `vendor.bosch.ai.server.ip` and `vendor.bosch.ai.server.port`.
  - CLI overrides: `-ip <host> -p <port>`.
- **Init Integration**: Runs automatically on boot or when SWUpdate daemon starts via `ai_service_client.rc`.

### Building
```bash
m ai_service_client
```

### Running on Target
```bash
# Configure server IP via system property
setprop vendor.bosch.ai.server.ip 192.168.1.100
setprop vendor.bosch.ai.server.port 9000
ai_service_client

# Or pass directly via CLI
ai_service_client -ip 192.168.1.100 -p 9000
ai_service_client -ip 127.0.0.1 -p 9000
```

---

## Directory Structure
```
ai_service_client/
├── docs/
│   └── system_flow.puml          # PlantUML sequence diagram for complete flow
├── Android.bp                    # Soong build definition
├── ai_service_client.rc          # Android init script
├── include/
│   ├── SwuNotificationClient.hpp # Manager for FcSwUpdateSrv Binder + AI Diagnostic APIs
│   ├── SwuUpdateCallback.hpp     # BnUpdateCallback + JSON formatting
│   └── TcpNotificationSender.hpp # Thread-safe bidirectional async TCP socket client
├── src/
│   ├── main.cpp                  # Daemon entry point with property/CLI parsing
│   ├── SwuNotificationClient.cpp
│   ├── SwuUpdateCallback.cpp
│   └── TcpNotificationSender.cpp
└── server/                       # Linux Docker Server & SLM stack
    ├── ai_server.py              # Async Python TCP server + Ollama prompt handler
    ├── Dockerfile                # AI Server container build
    ├── docker-compose.yml        # Multi-container stack (AI Server + Ollama)
    ├── mock_client_test.py       # Standalone test generator
    └── requirements.txt
```
