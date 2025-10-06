"""Lightweight NiceGUI compatibility layer for test execution."""

from __future__ import annotations


class _DummyUI:
    """Minimal placeholder for the NiceGUI ``ui`` module."""

    def __getattr__(self, name: str) -> "_DummyUI":
        def _noop(*_args, **_kwargs):  # type: ignore[override]
            return self

        return _noop

    def __call__(self, *_args, **_kwargs) -> "_DummyUI":
        return self


ui = _DummyUI()

__all__ = ["ui"]
