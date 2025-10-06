"""Ensure the NiceGUI application boots a live HTTP server."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Optional

import httpx
import pytest

from nicegui import ui


if ui.__class__.__name__ == "_DummyUI":  # pragma: no cover - fallback stub
    pytest.skip("NiceGUI stub is active; skipping server startup test.", allow_module_level=True)


def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def test_nicegui_server_responds(tmp_path: Path) -> None:
    """The dashboard should become reachable over HTTP once started."""

    port = _get_free_port()
    project_root = Path(__file__).resolve().parents[1]
    main_script = project_root / "main.py"

    env = os.environ.copy()
    env.update(
        {
            "NICEGUI_PORT": str(port),
            "NICEGUI_HOST": "127.0.0.1",
            "PYTHONUNBUFFERED": "1",
            "NICEGUI_SCREEN_TEST_PORT": str(port),
        }
    )

    process = subprocess.Popen(
        [sys.executable, str(main_script)],
        cwd=str(project_root),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    output_lines: list[str] = []

    def _drain_stdout() -> None:
        assert process.stdout is not None
        for line in process.stdout:
            output_lines.append(line)

    reader = threading.Thread(target=_drain_stdout, daemon=True)
    reader.start()

    response: Optional[httpx.Response] = None
    deadline = time.time() + 45
    url = f"http://127.0.0.1:{port}"

    try:
        while time.time() < deadline:
            if process.poll() is not None:
                reader.join(timeout=2)
                pytest.fail(
                    "NiceGUI process exited early with code"
                    f" {process.returncode}: {''.join(output_lines)}"
                )

            try:
                response = httpx.get(url, timeout=1.0)
            except httpx.RequestError:
                time.sleep(0.5)
                continue

            if response.status_code < 500:
                break
            time.sleep(0.5)
        else:
            reader.join(timeout=2)
            pytest.fail(
                "NiceGUI server did not become reachable in time. Output:\n"
                + "".join(output_lines)
            )
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        reader.join(timeout=2)

    assert response is not None
    assert response.status_code == 200
