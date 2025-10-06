"""Entry point for the modular operations dashboard."""

from __future__ import annotations

import sys
from pathlib import Path

import logging
import os

from nicegui import app, ui

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from app import build

PORT = int(os.environ.get("NICEGUI_PORT", "8081"))
HOST = os.environ.get("NICEGUI_HOST", "127.0.0.1")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nicegui")


@app.on_startup
def _log_startup() -> None:
    """Announce that the NiceGUI server finished booting."""

    logger.info("NiceGUI server is ready at http://%s:%s", HOST, PORT)


def main() -> None:
    """Launch the NiceGUI application."""

    logger.info("Starting NiceGUI server on %s:%s", HOST, PORT)
    ui.run(build, port=PORT, host=HOST, reload=False, show=False)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("NiceGUI failed to start")
        raise
