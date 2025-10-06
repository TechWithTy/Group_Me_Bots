"""Compatibility layer that prefers the real Pydantic package when available."""

from __future__ import annotations

import sys
import sysconfig
from importlib import util
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional


_purelib = sysconfig.get_paths().get("purelib")
_real_loaded = False
if _purelib is not None:
    _real_init = Path(_purelib) / "pydantic" / "__init__.py"
    if _real_init.exists():
        _spec = util.spec_from_file_location(__name__, _real_init)
        if _spec is not None and _spec.loader is not None:
            _module = util.module_from_spec(_spec)
            sys.modules[__name__] = _module
            _spec.loader.exec_module(_module)
            globals().update(_module.__dict__)
            _real_loaded = True


if not _real_loaded:

    class ValidationError(Exception):
        """Exception raised when data cannot be coerced into the target model."""


    class _Undefined:
        pass


    _UNDEFINED = _Undefined()


    class FieldInfo:
        """Stores default values and factories for pseudo-fields."""

        def __init__(
            self,
            default: Any = _UNDEFINED,
            *,
            default_factory: Optional[Callable[[], Any]] = None,
            metadata: Optional[Dict[str, Any]] = None,
        ) -> None:
            self.default = default
            self.default_factory = default_factory
            self.metadata = metadata or {}


    def Field(
        default: Any = _UNDEFINED,
        *,
        default_factory: Optional[Callable[[], Any]] = None,
        **metadata: Any,
    ) -> FieldInfo:
        """Capture default metadata for lazy instantiation."""

        return FieldInfo(
            default=default,
            default_factory=default_factory,
            metadata=dict(metadata),
        )


    class EmailStr(str):
        """Fallback type representing validated email strings."""


    class ConfigDict(dict):
        """Lightweight stand-in for :class:`pydantic.ConfigDict`."""

        def __init__(self, **kwargs: Any) -> None:
            super().__init__(**kwargs)


    def validator(*_fields: str, **_kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """No-op decorator placeholder for Pydantic validators."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            return func

        return decorator


    class BaseModel:
        """Simplified data container emulating Pydantic's ``BaseModel``."""

        __slots__ = ("__dict__",)

        def __init__(self, **data: Any) -> None:
            fields = getattr(self, "__annotations__", {})
            for name, annotation in fields.items():
                value = data.get(name, _UNDEFINED)
                if value is _UNDEFINED:
                    value = self._resolve_default(name)
                setattr(self, name, value)
            for name, value in data.items():
                if name not in fields:
                    setattr(self, name, value)

        @classmethod
        def _resolve_default(cls, name: str) -> Any:
            attr = getattr(cls, name, _UNDEFINED)
            if isinstance(attr, FieldInfo):
                if attr.default_factory is not None:
                    return attr.default_factory()
                if attr.default is not _UNDEFINED:
                    return attr.default
                return None
            if attr is _UNDEFINED:
                return None
            return attr

        def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
            fields = getattr(self, "__annotations__", {})
            return {name: getattr(self, name, None) for name in fields}

        def model_dump(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
            return self.dict(*args, **kwargs)

        @classmethod
        def parse_obj(cls, obj: Any) -> "BaseModel":
            if isinstance(obj, cls):
                return obj
            if isinstance(obj, dict):
                return cls(**obj)
            raise ValidationError(f"Cannot parse object of type {type(obj)!r}")

        def copy(self) -> "BaseModel":
            return self.__class__(**self.dict())

        def __repr__(self) -> str:  # pragma: no cover - debugging helper
            fields = ", ".join(f"{k}={v!r}" for k, v in self.dict().items())
            return f"{self.__class__.__name__}({fields})"
