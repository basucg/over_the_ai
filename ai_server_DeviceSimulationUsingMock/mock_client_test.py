#!/usr/bin/env python3
"""
Test script to simulate Android target sending update notifications & log archive to AI Server
"""
import base64
import argparse
import io
import json
import os
import socket
import tarfile
import time
import zipfile
from pathlib import Path

DEFAULT_SERVER_HOST = os.getenv("AI_SERVER_HOST", "127.0.0.1")
DEFAULT_SERVER_PORT = int(os.getenv("AI_SERVER_PORT", "9000"))
LOCAL_FALLBACK_HOSTS = ("127.0.0.1", "localhost")

def create_sample_zip() -> str:
    # buf = io.BytesIO()
    # with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        # da3_log = b"08-31 10:15:00.100 1001 1001 I da3_app_fcswupdate: Initiating SWUpdate payload flash\n08-31 10:15:02.120 1001 1001 E da3_app_fcswupdate: Update failed with code 28: ERROR_IMAGE_FLASHING\n"
        # tarinfo = tarfile.TarInfo(name="da3_app_fcswupdate.log")
        # tarinfo.size = len(da3_log)
        # tar.addfile(tarinfo, io.BytesIO(da3_log))

        # client_log = b"08-31 10:15:01.890 2002 2002 E update_engine_client: Status: ERROR_UPDATE_FAILED\n"
        # tarinfo = tarfile.TarInfo(name="update_engine_client.log")
        # tarinfo.size = len(client_log)
        # tar.addfile(tarinfo, io.BytesIO(client_log))

        # engine_log = b"08-31 10:15:01.850 3003 3003 E update_engine: [ERROR:delta_performer.cc(1150)] Payload hash mismatch on offset 4096\n"
        # tarinfo = tarfile.TarInfo(name="update_engine.log")
        # tarinfo.size = len(engine_log)
        # tar.addfile(tarinfo, io.BytesIO(engine_log))

    # return base64.b64encode(buf.getvalue()).decode("utf-8")
    zip_file_path = Path(__file__).resolve().parent / "version_downgrade.zip"

    buf = io.BytesIO()
    with zip_file_path.open("rb") as zip_file:
        zip_bytes = zip_file.read()
        buf.write(zip_bytes)

    print(f"Reading archive: {zip_file_path}")
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        for member_name in archive.namelist():
            print(f"--- {member_name} ---")
            with archive.open(member_name) as member_file:
                member_text = member_file.read().decode("utf-8", errors="replace")
                print(member_text)

    return base64.b64encode(buf.getvalue()).decode("utf-8")


def create_sample_process_logs() -> dict:
    zip_file_path = Path(__file__).resolve().parent / "version_downgrade.zip"
    process_logs = {}

    with zipfile.ZipFile(zip_file_path) as archive:
        for member_name in archive.namelist():
            if member_name.endswith("/"):
                continue
            with archive.open(member_name) as member_file:
                member_text = member_file.read().decode("utf-8", errors="replace")
                process_logs[Path(member_name).name] = member_text

    return process_logs

events = [
    {
        "event": "onUpdateState",
        "state": 5,
        "stateName": "RUNNING (5)",
        "estimatedUpdateTimeSec": 120,
        "timestamp": int(time.time())
    },
    {
        "event": "onUpdateProgress",
        "train": "SUZUKI_DA3_PROD_2026",
        "deviceName": "da3_in",
        "moduleName": "system_a",
        "subModuleName": "system_ext",
        "refKey": "ext4_fs_img",
        "source": "/data/usb/Full_stick.iso",
        "line1": "Flashing system_a partition",
        "line2": "Sector 45120/120000",
        "luaCmd": "flashPartition('system_a')",
        "retries": 0,
        "numAll": 8,
        "numComplete": 2,
        "numRunning": 1,
        "numNotApplicable": 0,
        "numFailed": 0,
        "numRemaining": 5,
        "subModulePercentComplete": 65,
        "releasePercentComplete": 30,
        "releasePercentCompleteForPhase": 30,
        "timestamp": int(time.time())
    },
    # {
        # "event": "onUpdateError",
        # "errorCode": 28,
        # "errorName": "ERROR_IMAGE_FLASHING (28)",
        # "timestamp": int(time.time())
    # },
    {
        "event": "swUpdateDiagnosticArchive",
        #"errorCode": 28,
        "archiveName": f"swupdate-error-{int(time.time())}.zip",
        "encoding": "base64",
        "archiveData": create_sample_zip(),
        "processLogs": create_sample_process_logs(),
        "timestamp": int(time.time())
    }
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send mock SWUpdate events to the AI diagnostic server.")
    parser.add_argument("--host", default=DEFAULT_SERVER_HOST, help="Target AI server host or IP address.")
    parser.add_argument("--port", type=int, default=DEFAULT_SERVER_PORT, help="Target AI server TCP port.")
    return parser.parse_args()


def connect_to_server(host: str, port: int) -> socket.socket:
    attempted_hosts = []
    candidate_hosts = [host]

    if host not in LOCAL_FALLBACK_HOSTS:
        candidate_hosts.extend(fallback for fallback in LOCAL_FALLBACK_HOSTS if fallback != host)

    last_error = None
    attempt_errors = []
    for candidate_host in candidate_hosts:
        attempted_hosts.append(candidate_host)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5.0)
        try:
            client_socket.connect((candidate_host, port))
            if candidate_host != host:
                print(f"Resolved connection using fallback host {candidate_host}:{port}")
            return client_socket
        except OSError as error:
            client_socket.close()
            last_error = error
            attempt_errors.append(f"{candidate_host}:{port} -> {type(error).__name__}: {error}")
            if isinstance(error, socket.gaierror):
                print(f"Name resolution failed for {candidate_host}:{port}: {error}")

    attempted_list = "; ".join(attempt_errors)
    raise ConnectionError(f"Could not connect to AI Server. Attempts: {attempted_list}") from last_error

def main():
    args = parse_args()
    print(f"Connecting to AI Server at {args.host}:{args.port}...")
    s = connect_to_server(args.host, args.port)
    print("Connected! Streaming simulated update failure events & process log archive...")

    for event in events:
        msg = json.dumps(event) + "\n"
        s.sendall(msg.encode("utf-8"))
        print(f"Sent: {event['event']}")
        time.sleep(1.0)

    time.sleep(2)
    s.close()
    print("Test stream finished.")

if __name__ == "__main__":
    main()
