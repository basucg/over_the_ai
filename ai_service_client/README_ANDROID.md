# Android AI Service Client

This guide covers the Android component that connects SWUpdate and FOTA HMI Binder services to the AI diagnostic server. For the combined architecture and backend choices, see [README.md](README.md).

## Build and install

Build from an initialized Android source/build environment:

```sh
m ai_service_client
```

`Android.bp` builds `libai_service_client` and the `ai_service_client` system-ext binary. `ai_service_client.mk` includes the binary in `PRODUCT_PACKAGES`. The binary is installed at `/system_ext/bin/ai_service_client` and uses `ai_service_client.rc` for init integration.

## Startup and server address

Init starts the service when either `da3_app_fcswupdate` or `app_fcswupdate` becomes active, and also starts it after `sys.boot_completed` as a fallback. The checked-in init command is:

```sh
/system_ext/bin/ai_service_client -ip 127.0.0.1 -p 9000
```

Change the `-ip` value in `ai_service_client.rc` to the reachable host address when the diagnostic server is not on the Android target's loopback interface. The server must be reachable on TCP port `9000` (or update `-p` to match its port).

## Client responsibilities

- `SwuNotificationClient` connects to `FcSwUpdateSrv` and registers `SwuUpdateCallback` for update-state, progress, error, cancel-result, and completion-result callbacks.
- `getSystemInformation()` and `sendSystemInformation()` provide target platform details to the server.
- `getRequiredFiles()` gathers the artifact tags requested by the server, packages the requested diagnostic content, base64-encodes the archive, and queues it for transport.
- `FotaHmiNotificationClient` connects to `fota.hmi.HmiService`, registers its callback, handles Binder service death/reconnection, and recognizes the server's `request_ota_logs` command.
- `TcpNotificationSender` manages the asynchronous send queue, maintains the TCP connection, dispatches incoming server messages, and allows the endpoint to be updated by its owner.

## Android sources

- `include/SwuNotificationClient.hpp`: SWUpdate Binder client and diagnostic collection API.
- `include/SwuUpdateCallback.hpp`: SWUpdate callback implementation contract.
- `include/FotaHmiNotificationClient.hpp`: FOTA HMI Binder client contract.
- `include/TcpNotificationSender.hpp`: TCP transport API.
- `aidl/fota/`: FOTA HMI AIDL interfaces and parcelables.
- `Android.bp`, `ai_service_client.mk`, `ai_service_client.rc`: Soong definitions, product inclusion, and init service configuration.
