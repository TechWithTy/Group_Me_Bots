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
