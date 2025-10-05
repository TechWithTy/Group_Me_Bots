"""Minimal pytest-asyncio compatible plugin for running coroutine tests."""
from __future__ import annotations

import asyncio
import inspect
from typing import Any, Callable

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Register the ``asyncio`` marker so tests opt into async execution."""
    config.addinivalue_line(
        "markers",
        "asyncio: execute the decorated test function in an event loop",
    )


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem: pytest.Function) -> bool | None:
    """Execute ``async def`` tests within a fresh event loop."""
    marker = pyfuncitem.get_closest_marker("asyncio")
    if marker is None:
        return None

    test_obj: Callable[..., Any] = pyfuncitem.obj
    if not inspect.iscoroutinefunction(test_obj):
        return None

    funcargs = pyfuncitem.funcargs
    kwargs = {name: funcargs[name] for name in pyfuncitem._fixtureinfo.argnames}

    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        loop.run_until_complete(test_obj(**kwargs))
    finally:
        loop.run_until_complete(_shutdown_loop(loop))
        asyncio.set_event_loop(None)
        loop.close()

    return True


async def _shutdown_loop(loop: asyncio.AbstractEventLoop) -> None:
    """Ensure pending tasks are cancelled before closing the loop."""
    current = asyncio.current_task(loop=loop)
    pending = [task for task in asyncio.all_tasks(loop=loop) if task is not current]
    if pending:
        for task in pending:
            task.cancel()

        await asyncio.gather(*pending, return_exceptions=True)

    await loop.shutdown_asyncgens()
