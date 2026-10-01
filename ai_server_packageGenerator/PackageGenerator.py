#!/usr/bin/env python3
import asyncio
import json
import logging
import os
import time

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("PackageGenerator")

async def generate_package(verify_version: bool, verification_type: str, from_version: str, to_version: str, package_type: str):
    """
    Simulates the package generation process.
    In a real implementation, this would involve complex logic to build an update package.
    """
    logger.info("Received request to generate package.")
    logger.info(f"  - Package Type: {package_type}")
    logger.info(f"  - From Version: {from_version}")
    logger.info(f"  - To Version:   {to_version}")
    logger.info(f"  - Verify Version: {verify_version}")
    logger.info(f"  - Verification Type: {verification_type}")
    higher_versions={"qpr1_a12_int_2026.20.0", "qpr1_a12_int_2026.21.0", "qpr1_a12_int_2026.22.0", "qpr1_a12_int_2026.23.0",}
    # Placeholder for package generation logic.
    # This simulates a long-running task.
    await asyncio.sleep(10)
    logger.info(f"Identifying Best version higher than {from_version}")

    if higher_versions:
        def version_key(v_str):
            """Converts version string to a comparable tuple of integers."""
            # Extracts '2026.20.0' from 'qpr1_a12_int_2026.20.0'
            version_part = v_str.split('_')[-1]
            # Returns a tuple of integers, e.g., (2026, 20, 0) for comparison
            return tuple(map(int, version_part.split('.')))

        highest_version = max(higher_versions, key=version_key)
        logger.info(f"Highest available version from the list is: {highest_version}")
    logger.info(f"Generating delta between versions: {from_version} and {highest_version} ......")
    await asyncio.sleep(50)
    package_name = f"{package_type.lower()}_{from_version}-{highest_version}.zip"
    logger.info(f"Successfully generated package: {package_name}")
    return {"status": "success", "package_name": package_name}

async def handle_request(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    peer = writer.get_extra_info("peername")
    logger.info(f"Client connected from {peer}")

    try:
        line = await reader.readline()
        if not line:
            logger.info(f"Client {peer} disconnected")
            return

        raw_payload = line.decode("utf-8", errors="replace").strip()
        if raw_payload:
            try:
                request_data = json.loads(raw_payload)
                command = request_data.get("command")
                params = request_data.get("params", {})

                if command == "generate_package":
                    # Note: Handling the typo 'to_verssion' from the request
                    to_version = params.get("to_version") or params.get("to_version")
                    
                    result = await generate_package(
                        verify_version=params.get("verify_version", False),
                        verification_type=params.get("verification_type", "unknown"),
                        from_version=params.get("from_version", "N/A"),
                        to_version=to_version,
                        package_type=params.get("package_type", "UNKNOWN"),
                    )
                    response = {"request_id": request_data.get("request_id"), "result": result}
                    writer.write(json.dumps(response).encode('utf-8') + b'\n')
                    await writer.drain()
                else:
                    error_response = {"error": "Unknown command", "command": command}
                    writer.write(json.dumps(error_response).encode('utf-8') + b'\n')
                    await writer.drain()
            except (json.JSONDecodeError, Exception) as e:
                logger.error(f"Error handling request from {peer}: {e}")
                error_response = {"error": str(e)}
                writer.write(json.dumps(error_response).encode('utf-8') + b'\n')
                await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    host = os.getenv("PKG_GEN_HOST", "0.0.0.0")
    port = int(os.getenv("PKG_GEN_PORT", "9001"))
    print("Package generator")
    server = await asyncio.start_server(handle_request, host, port)
    logger.info(f"Package Generator server started on {host}:{port}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Package Generator server shutting down.")
