"""Entry point for the modular operations dashboard."""

from __future__ import annotations

from pathlib import Path
import sys

from nicegui import ui

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from app import build


try:
    print('Starting NiceGUI server...')
    ui.run(build, port=8081)
    print('Server started on port 8081')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()

# Keep the server running
input('Server is running on http://localhost:8081. Press Enter to stop...')
