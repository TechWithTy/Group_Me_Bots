"""NiceGUI compatibility layer that prefers the real package when available."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any


def _load_real_nicegui():
    """Attempt to load the installed NiceGUI distribution."""

    module_name = __name__
    package_parent = Path(__file__).resolve().parents[1]

    submodule_prefix = f"{module_name}."
    cached_modules = {
        name: sys.modules[name]
        for name in list(sys.modules)
        if name == module_name or name.startswith(submodule_prefix)
    }
    original_sys_path = list(sys.path)

    try:
        for name in cached_modules:
            sys.modules.pop(name, None)

        sys.path = [
            entry
            for entry in original_sys_path
            if Path(entry).resolve() != package_parent.resolve()
        ]

        module = importlib.import_module(module_name)
    except Exception:  # pragma: no cover - falls back to stub
        sys.modules.update(cached_modules)
        return None
    else:
        sys.modules[module_name] = module
        return module
    finally:
        sys.path = original_sys_path


_REAL_MODULE = _load_real_nicegui()

if _REAL_MODULE is not None:
    ui = _REAL_MODULE.ui  # type: ignore[attr-defined]
    __all__ = getattr(_REAL_MODULE, "__all__", ["ui"])

    def __getattr__(name: str) -> Any:  # noqa: D401
        """Proxy missing attributes to the real NiceGUI module."""

        return getattr(_REAL_MODULE, name)

else:

    class _DummyApp:
        """Small subset of the NiceGUI ``app`` object used by the project."""

        def __init__(self) -> None:
            self._startup_callbacks = []
            self._shutdown_callbacks = []

        def on_startup(self, func):  # type: ignore[override]
            """Register a startup callback and return the original function."""

            self._startup_callbacks.append(func)
            return func

        def on_shutdown(self, func):  # type: ignore[override]
            """Register a shutdown callback and return the original function."""

            self._shutdown_callbacks.append(func)
            return func

        def _emit_startup(self) -> None:
            for callback in list(self._startup_callbacks):
                callback()

        def _emit_shutdown(self) -> None:
            for callback in list(self._shutdown_callbacks):
                callback()


    class _DummyElement:
        """Placeholder element that mimics the fluent NiceGUI API."""

        def __call__(self, *_args, **_kwargs) -> "_DummyElement":
            return self

        def __getattr__(self, _name: str):  # type: ignore[override]
            def _noop(*_args, **_kwargs):
                return self

            return _noop

        # Context manager support -------------------------------------------------
        def __enter__(self) -> "_DummyElement":
            return self

        def __exit__(self, *_exc) -> None:
            return None


    class _DummyUI(_DummyElement):
        """Minimal placeholder for the NiceGUI ``ui`` module."""

        def __init__(self, dummy_app: _DummyApp) -> None:
            super().__init__()
            self._app = dummy_app

        def run(self, builder, *_, **__):  # type: ignore[override]
            """Invoke ``builder`` immediately and trigger lifecycle hooks."""

            builder()
            self._app._emit_startup()


    _DUMMY_APP = _DummyApp()
    app = _DUMMY_APP
    ui = _DummyUI(_DUMMY_APP)
    __all__ = ["app", "ui"]
