"""Integration tests for the FastAPI application wiring."""
import pytest

from app.discord import api


@pytest.mark.asyncio
async def test_root_endpoint_returns_status():
    """Verify the root endpoint returns the health payload."""
    response = await api.root()
    assert response == {"message": "Discord API is running"}


def test_expected_routers_registered():
    """Ensure that high-level routers are registered on the FastAPI application."""
    prefixes = {route.path for route in api.app.router.routes}
    assert "/channels/{channel_id}" in prefixes
    assert "/guilds/{guild_id}" in prefixes
    assert "/users/@me" in prefixes
    assert "/channels/{channel_id}/messages/{message_id}" in prefixes
