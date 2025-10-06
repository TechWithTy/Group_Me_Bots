"""Lightweight NiceGUI compatibility layer for test execution."""

from __future__ import annotations


class _DummyUI:
    """Minimal placeholder for the NiceGUI ``ui`` module."""

    def run(
        self,
        builder,
        *,
        title: str | None = None,
        host: str = "127.0.0.1",
        port: int = 8080,
        **_kwargs,
    ) -> None:
        """Invoke ``builder`` and print a helpful stub message."""

        if callable(builder):
            builder()
        app_name = title or "NiceGUI Application"
        print(
            f"[NiceGUI stub] {app_name} ready. Server would listen on http://{host}:{port}."
        )
        print("[NiceGUI stub] This lightweight environment does not start a web server.")

    def __getattr__(self, name: str) -> "_DummyUI":
        def _noop(*_args, **_kwargs):  # type: ignore[override]
            return self

        return _noop

    def __call__(self, *_args, **_kwargs) -> "_DummyUI":
        return self

    def __enter__(self) -> "_DummyUI":  # pragma: no cover - trivial
        return self

    def __exit__(self, *_exc_info) -> None:  # pragma: no cover - trivial
        return None


ui = _DummyUI()

__all__ = ["ui"]
