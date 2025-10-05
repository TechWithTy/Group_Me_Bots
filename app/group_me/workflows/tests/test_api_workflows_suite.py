"""Integration-style tests for bot-facing API clients and routers."""
from __future__ import annotations

import types
from typing import Any, Dict

import pytest

pytest.importorskip("pydantic")

fastapi_module = pytest.importorskip("fastapi")
testclient_module = pytest.importorskip("fastapi.testclient")

FastAPI = fastapi_module.FastAPI
TestClient = testclient_module.TestClient

from app import bots_api as bots_api_module
from app import groups as groups_module
from app import messages as messages_module
from app import chats as chats_module
from app.chats import router as chats_router
from app.dependencies import get_groupme_client, get_tenant_from_api_key


@pytest.mark.asyncio
async def test_messages_api_list_for_group_applies_filters():
    """Ensure the Messages API forwards pagination filters to the client."""
    client = types.SimpleNamespace()
    captured: Dict[str, Any] = {}

    async def fake_get(path: str, params: Dict[str, Any] | None = None):
        captured["path"] = path
        captured["params"] = params or {}
        payload = {
            "count": 1,
            "messages": [
                {
                    "id": "m1",
                    "group_id": "g1",
                    "user_id": "u1",
                    "name": "Tester",
                    "created_at": 1,
                    "text": "hello",
                    "favorited_by": [],
                    "source_guid": "guid-1",
                }
            ],
        }
        return types.SimpleNamespace(response=payload)

    client._get = fake_get  # type: ignore[attr-defined]
    api = messages_module.MessagesAPI(client)  # type: ignore[arg-type]

    response = await api.list_for_group(
        "g1", before_id="b2", since_id="s3", after_id="a4", limit=42
    )

    assert response.count == 1
    assert captured["path"] == "/groups/g1/messages"
    assert captured["params"] == {
        "before_id": "b2",
        "since_id": "s3",
        "after_id": "a4",
        "limit": 42,
    }


@pytest.mark.asyncio
async def test_bots_api_post_message_includes_optional_picture():
    """The Bots API must forward optional picture URLs when present."""
    client = types.SimpleNamespace()
    recorded_body: Dict[str, Any] = {}

    async def fake_post(
        path: str,
        json: Dict[str, Any] | None = None,
        params: Dict[str, Any] | None = None,
    ):
        recorded_body["path"] = path
        recorded_body["json"] = json or {}
        return types.SimpleNamespace(response={"status": "ok"})

    client._post = fake_post  # type: ignore[attr-defined]
    api = bots_api_module.BotsAPI(client)  # type: ignore[arg-type]

    payload = await api.post_message("bot-1", "Hi there", picture_url="https://img")

    assert payload == {"status": "ok"}
    assert recorded_body["path"] == "/bots/post"
    assert recorded_body["json"] == {
        "bot_id": "bot-1",
        "text": "Hi there",
        "picture_url": "https://img",
    }


def _build_test_app(mock_client) -> FastAPI:
    app = FastAPI()
    app.include_router(chats_router)

    async def fake_client(_: Any) -> Any:
        return mock_client

    async def fake_tenant(_: Any, x_api_key: str | None = None) -> Any:
        return types.SimpleNamespace(id="tenant-1")

    app.dependency_overrides[get_groupme_client] = fake_client
    app.dependency_overrides[get_tenant_from_api_key] = fake_tenant
    return app


def test_chats_router_like_and_error_flow(monkeypatch):
    """Verify chats router returns success and surfaces failures."""
    mock_client = types.SimpleNamespace()

    async def fake_like(conversation_id: str, message_id: str, tenant_id: str) -> None:
        if message_id == "fail":
            raise RuntimeError("boom")

    async def fake_unlike(conversation_id: str, message_id: str, tenant_id: str) -> None:
        return None

    monkeypatch.setattr(chats_module, "_mock_like_message", fake_like)
    monkeypatch.setattr(chats_module, "_mock_unlike_message", fake_unlike)

    app = _build_test_app(mock_client)
    client = TestClient(app)

    ok_response = client.post("/api/v1/messages/conv-1/msg-1/like")
    assert ok_response.status_code == 200
    assert ok_response.json()["status"] == "success"

    error_response = client.post("/api/v1/messages/conv-1/fail/like")
    assert error_response.status_code == 500
    assert error_response.json()["detail"] == "Failed to like message"


@pytest.mark.asyncio
async def test_groups_api_share_link_supports_invitation_hacks():
    """Groups API should expose share URLs for ghost invitation workflows."""
    mock_client = types.SimpleNamespace()
    payload = [
        {"id": "g1", "name": "Alpha", "share_url": "https://group/alpha"},
        {"id": "g2", "name": "Beta", "share_url": None},
    ]

    async def fake_get(path: str, params: Dict[str, Any] | None = None):
        return types.SimpleNamespace(response=payload)

    mock_client._get = fake_get  # type: ignore[attr-defined]

    api = groups_module.GroupsAPI(mock_client)  # type: ignore[arg-type]
    groups = await api.list()

    share_urls = [group.share_url for group in groups if group.share_url]
    assert share_urls == ["https://group/alpha"]
