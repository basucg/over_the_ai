#!/usr/bin/env python3
import asyncio
import json
import time
import base64
import io
import tarfile

async def send_test_events():
    """Connects to the AI Diagnostic Server and sends a sequence of test events."""
    host = "127.0.0.1"
    port = 9000

    try:
        reader, writer = await asyncio.open_connection(host, port)
        print(f"Connected to server at {host}:{port}")

        # 1. Send an onUpdateState event indicating an error state
        state_error_event = {
            "event": "onUpdateState",
            "timestamp": time.time(),
            "state": 6, # ERROR_STATE_CODE from UpdateAgent.py
            "stateName": "ERROR",
            "estimatedUpdateTimeSec": 0,
        }
        writer.write(json.dumps(state_error_event).encode('utf-8') + b'\n')
        await writer.drain()
        print(f"Sent event: {json.dumps(state_error_event, indent=2)}")
        await asyncio.sleep(2) # Give server time to process

        # 2. Send a diagnostic archive event
        # Create a dummy tar.gz in memory for testing
        dummy_log_content = b"This is a log file inside a tar archive.\n[ERROR] A critical error occurred here."
        tar_buffer = io.BytesIO()
        with tarfile.open(fileobj=tar_buffer, mode="w:gz") as tar:
            tarinfo = tarfile.TarInfo(name="da3_app_fcswupdate.log")
            tarinfo.size = len(dummy_log_content)
            tar.addfile(tarinfo, io.BytesIO(dummy_log_content))

        archive_bytes = tar_buffer.getvalue()
        archive_b64 = base64.b64encode(archive_bytes).decode('utf-8')

        archive_event = {
            "event": "swUpdateDiagnosticArchive",
            "timestamp": time.time(),
            "archiveName": "test_diagnostics.tar.gz",
            "archiveData": archive_b64,
            "instructions": "This is a test with a diagnostic archive."
        }

        # The payload can be large, so we just print a summary
        print(f"Sending event: swUpdateDiagnosticArchive (archive size: {len(archive_bytes)} bytes)")
        writer.write(json.dumps(archive_event).encode('utf-8') + b'\n')
        await writer.drain()

        # The analysis can take a while.
        print("Waiting for server to process the archive...")
        await asyncio.sleep(20)

        writer.close()
        await writer.wait_closed()
        print("Connection closed.")

    except ConnectionRefusedError:
        print(f"Connection refused. Is the server running at {host}:{port}?")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # To run this, first start UpdateAgent.py, then run this script.
    print("Starting mock client test...")
    asyncio.run(send_test_events())
    print("Mock client test finished.")