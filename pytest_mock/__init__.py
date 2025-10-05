"""Minimal implementation of the :mod:`pytest_mock` helper used in tests."""
from __future__ import annotations

from typing import Any, Iterator, List
from unittest import mock

import pytest


class MockerFixture:
    """Lightweight stand-in for ``pytest_mock``'s fixture."""

    def __init__(self) -> None:
        self._patches: List[mock._patch] = []

    def patch(self, target: str, *args: Any, **kwargs: Any) -> Any:
        patcher = mock.patch(target, *args, **kwargs)
        started = patcher.start()
        self._patches.append(patcher)
        return started

    def stopall(self) -> None:
        while self._patches:
            self._patches.pop().stop()

    def spy(self, obj: Any, attribute: str) -> Any:
        patcher = mock.patch.object(obj, attribute, wraps=getattr(obj, attribute))
        started = patcher.start()
        self._patches.append(patcher)
        return started


@pytest.fixture
def mocker() -> Iterator[MockerFixture]:
    fixture = MockerFixture()
    try:
        yield fixture
    finally:
        fixture.stopall()


__all__ = ["MockerFixture", "mocker"]
