"""Pytest compatibility fixtures for the simulator."""

from __future__ import annotations

import pytest

from ._simulator import User


@pytest.fixture
async def user() -> User:
    """Provide a simulated NiceGUI test user."""

    return User()
