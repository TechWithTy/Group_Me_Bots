"""Lightweight runtime that emulates NiceGUI when the dependency is missing."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import List

from ._stub_template import render_static_dashboard


class _DummyApp:
    """Subset of the NiceGUI ``app`` hooks used by the dashboard."""

    def __init__(self) -> None:
        self._startup_callbacks: List = []
        self._shutdown_callbacks: List = []

    def on_startup(self, func):  # type: ignore[override]
        self._startup_callbacks.append(func)
        return func

    def on_shutdown(self, func):  # type: ignore[override]
        self._shutdown_callbacks.append(func)
        return func

    def _emit_startup(self) -> None:
        for callback in list(self._startup_callbacks):
            callback()

    def _emit_shutdown(self) -> None:
        for callback in list(self._shutdown_callbacks):
            callback()


class _DummyElement:
    """Fluent placeholder for NiceGUI elements."""

    def __call__(self, *_args, **_kwargs):  # type: ignore[override]
        return self

    def __getattr__(self, _name):  # type: ignore[override]
        def _noop(*_args, **_kwargs):
            return self

        return _noop

    def __enter__(self):  # type: ignore[override]
        return self

    def __exit__(self, *_exc):  # type: ignore[override]
        return None


class _DashboardHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    html: str = ""

    def do_GET(self):  # type: ignore[override]
        if self.path not in {"/", "/index.html"}:
            self.send_error(404)
            return
        content = self.html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_HEAD(self):  # type: ignore[override]
        if self.path not in {"/", "/index.html"}:
            self.send_error(404)
            return
        content_length = len(self.html.encode("utf-8"))
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(content_length))
        self.end_headers()

    def log_message(self, *_args, **_kwargs):  # type: ignore[override]
        return


class _DummyUI(_DummyElement):
    """Minimal ``ui`` module exposing ``run``."""

    def __init__(self, dummy_app: _DummyApp) -> None:
        super().__init__()
        self._app = dummy_app

    def run(self, builder, *_, host: str = "127.0.0.1", port: int = 8080, **__):  # type: ignore[override]
        builder()
        self._app._emit_startup()

        _DashboardHandler.html = render_static_dashboard()
        server = ThreadingHTTPServer((host, port), _DashboardHandler)
        print(
            f"Stub NiceGUI server is rendering the dashboard at http://{host}:{port}",
            flush=True,
        )

        try:
            server.serve_forever()
        except KeyboardInterrupt:  # pragma: no cover - manual termination
            pass
        finally:
            server.server_close()
            self._app._emit_shutdown()


_DUMMY_APP = _DummyApp()
app = _DUMMY_APP
ui = _DummyUI(_DUMMY_APP)
__all__ = ["app", "ui"]
