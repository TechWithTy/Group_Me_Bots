"""Comprehensive tests covering the unofficial Signal REST API specification.

These tests exercise each documented endpoint from
``_docs/platforms/signal/unofficial/swagger.json`` to ensure our FastAPI
implementation matches the contract.  The suite intentionally focuses on the
HTTP status codes and response payload structure described in the spec.
"""

from __future__ import annotations

from typing import Iterable

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.signal.api import router as signal_router
from app.signal.api.state import state


def _create_client() -> TestClient:
    app = FastAPI()
    app.include_router(signal_router)
    return TestClient(app)


@pytest.fixture()
def client() -> Iterable[TestClient]:
    """Provide a clean API client with isolated in-memory state."""

    state.reset()
    client = _create_client()
    try:
        yield client
    finally:
        state.reset()


def test_configuration_flow(client: TestClient) -> None:
    """Configuration endpoints should expose and persist settings."""

    about = client.get("/v1/about")
    assert about.status_code == 200
    for key in {"build", "capabilities", "mode", "version", "versions"}:
        assert key in about.json()

    config = client.get("/v1/configuration")
    assert config.status_code == 200
    assert config.json()["logging"]["level"] == "INFO"

    update = client.post(
        "/v1/configuration",
        json={"logging": {"level": "DEBUG"}},
    )
    assert update.status_code == 204

    updated_config = client.get("/v1/configuration")
    assert updated_config.status_code == 200
    assert updated_config.json()["logging"]["level"] == "DEBUG"


def test_account_management_flow(client: TestClient) -> None:
    """Account endpoints should follow the swagger contract."""

    # Registration creates the account and exposes it via the listing endpoint.
    register = client.post(
        "/v1/register/+15551234567",
        json={"captcha": "signal", "use_voice": False},
    )
    assert register.status_code == 201

    accounts = client.get("/v1/accounts")
    assert accounts.status_code == 200
    assert "+15551234567" in accounts.json()

    # PIN management
    set_pin = client.post(
        "/v1/accounts/+15551234567/pin",
        json={"pin": "1234"},
    )
    assert set_pin.status_code == 201

    clear_pin = client.delete("/v1/accounts/+15551234567/pin")
    assert clear_pin.status_code == 204

    # Rate limit challenge
    challenge = client.post(
        "/v1/accounts/+15551234567/rate-limit-challenge",
        json={
            "captcha": "signalcaptcha://token",
            "challenge_token": "challenge-id",
        },
    )
    assert challenge.status_code == 204

    # Account settings and trust mode
    update_settings = client.put(
        "/v1/accounts/+15551234567/settings",
        json={"discoverable_by_number": False, "share_number": False},
    )
    assert update_settings.status_code == 204

    trust_mode = client.get("/v1/configuration/+15551234567/settings")
    assert trust_mode.status_code == 200
    assert trust_mode.json()["trust_mode"] == "TRUSTED_UNVERIFIED"

    set_trust_mode = client.post(
        "/v1/configuration/+15551234567/settings",
        json={"trust_mode": "TRUSTED_VERIFIED"},
    )
    assert set_trust_mode.status_code == 204

    updated_trust = client.get("/v1/configuration/+15551234567/settings")
    assert updated_trust.status_code == 200
    assert updated_trust.json()["trust_mode"] == "TRUSTED_VERIFIED"

    # Username lifecycle
    set_username = client.post(
        "/v1/accounts/+15551234567/username",
        json={"username": "tester"},
    )
    assert set_username.status_code == 201
    payload = set_username.json()
    assert payload["username"] == "tester"
    assert payload["username_link"].startswith("signal.me/")

    remove_username = client.delete("/v1/accounts/+15551234567/username")
    assert remove_username.status_code == 204


def test_attachment_crud(client: TestClient) -> None:
    """Attachment endpoints expose stored artifacts."""

    attachment_id = state.store_attachment("ZmFrZS1hdHRhY2htZW50", "text/plain")

    listing = client.get("/v1/attachments")
    assert listing.status_code == 200
    assert attachment_id in listing.json()

    served = client.get(f"/v1/attachments/{attachment_id}")
    assert served.status_code == 200
    assert served.json()["content"] == "ZmFrZS1hdHRhY2htZW50"

    deleted = client.delete(f"/v1/attachments/{attachment_id}")
    assert deleted.status_code == 204

    refreshed_listing = client.get("/v1/attachments")
    assert refreshed_listing.status_code == 200
    assert attachment_id not in refreshed_listing.json()


def test_contact_management(client: TestClient) -> None:
    """Contacts can be added, listed, retrieved, and synced."""

    client.post("/v1/register/+15559876543")

    put_contact = client.put(
        "/v1/contacts/+15559876543",
        json={"recipient": "+15550001111", "name": "Alice"},
    )
    assert put_contact.status_code == 204

    contacts = client.get("/v1/contacts/+15559876543")
    assert contacts.status_code == 200
    contact_entry = contacts.json()[0]
    assert contact_entry["name"] == "Alice"
    contact_uuid = contact_entry["uuid"]

    fetched = client.get(f"/v1/contacts/+15559876543/{contact_uuid}")
    assert fetched.status_code == 200
    assert fetched.json()["uuid"] == contact_uuid

    avatar = client.get(f"/v1/contacts/+15559876543/{contact_uuid}/avatar")
    assert avatar.status_code == 200
    assert avatar.json()["content_type"].startswith("image/")

    sync = client.post("/v1/contacts/+15559876543/sync")
    assert sync.status_code == 204


def test_device_registration_and_linking(client: TestClient) -> None:
    """Device lifecycle operations follow the documented responses."""

    client.post("/v1/register/+15557778888")

    verification = client.post(
        "/v1/register/+15557778888/verify/000111",
        json={"pin": "9999"},
    )
    assert verification.status_code == 201

    qr = client.get("/v1/qrcodelink", params={"device_name": "Laptop", "qrcode_version": 12})
    assert qr.status_code == 200
    assert qr.json()["qr_code"].startswith("data:image/png;base64,")

    devices = client.get("/v1/devices/+15557778888")
    assert devices.status_code == 200
    assert isinstance(devices.json(), list)

    link = client.post(
        "/v1/devices/+15557778888",
        json={"uri": "device://uuid"},
    )
    assert link.status_code == 204

    unregister = client.post(
        "/v1/unregister/+15557778888",
        json={"delete_account": False, "delete_local_data": False},
    )
    assert unregister.status_code == 204


def test_group_management(client: TestClient) -> None:
    """Group endpoints must manage membership and metadata."""

    client.post("/v1/register/+15556667777")

    created = client.post(
        "/v1/groups/+15556667777",
        json={"name": "Test Group", "members": ["+15550002222"]},
    )
    assert created.status_code == 201
    group_id = created.json()["id"]

    groups = client.get("/v1/groups/+15556667777")
    assert groups.status_code == 200
    assert groups.json()[0]["id"] == group_id

    detail = client.get(f"/v1/groups/+15556667777/{group_id}")
    assert detail.status_code == 200
    assert detail.json()["id"] == group_id

    update = client.put(
        f"/v1/groups/+15556667777/{group_id}",
        json={"description": "Updated", "permissions": {"send_messages": "every-member"}},
    )
    assert update.status_code == 204

    add_admins = client.post(
        f"/v1/groups/+15556667777/{group_id}/admins",
        json={"admins": ["+15556667777"]},
    )
    assert add_admins.status_code == 204

    add_members = client.post(
        f"/v1/groups/+15556667777/{group_id}/members",
        json={"members": ["+15550003333"]},
    )
    assert add_members.status_code == 204

    block = client.post(f"/v1/groups/+15556667777/{group_id}/block")
    assert block.status_code == 204

    join = client.post(f"/v1/groups/+15556667777/{group_id}/join")
    assert join.status_code == 204

    remove_admins = client.delete(
        f"/v1/groups/+15556667777/{group_id}/admins",
        json={"admins": ["+15556667777"]},
    )
    assert remove_admins.status_code == 204

    remove_members = client.delete(
        f"/v1/groups/+15556667777/{group_id}/members",
        json={"members": ["+15550003333"]},
    )
    assert remove_members.status_code == 204

    avatar = client.get(f"/v1/groups/+15556667777/{group_id}/avatar")
    assert avatar.status_code == 200
    assert avatar.json()["avatar"].startswith("data:image/png;base64,")

    quit_group = client.post(f"/v1/groups/+15556667777/{group_id}/quit")
    assert quit_group.status_code == 204

    delete_group = client.delete(f"/v1/groups/+15556667777/{group_id}")
    assert delete_group.status_code == 200


def test_identity_and_profile_endpoints(client: TestClient) -> None:
    """Identity trust and profile updates adhere to the API contract."""

    client.post("/v1/register/+15553334444")

    profile = client.put(
        "/v1/profiles/+15553334444",
        json={"name": "Example", "about": "Testing"},
    )
    assert profile.status_code == 204

    trust = client.put(
        "/v1/identities/+15553334444/trust/+15550009999",
        json={"verified_safety_number": "safe", "trust_all_known_keys": True},
    )
    assert trust.status_code == 204

    identities = client.get("/v1/identities/+15553334444")
    assert identities.status_code == 200
    assert identities.json()[0]["number"] == "+15550009999"


def test_message_and_reaction_flow(client: TestClient) -> None:
    """Messaging endpoints move data between inboxes and support reactions."""

    client.post("/v1/register/+15554445555")
    client.post("/v1/register/+15559998888")

    send_v2 = client.post(
        "/v2/send",
        json={
            "message": "Hello",
            "number": "+15554445555",
            "recipients": ["+15559998888"],
            "base64_attachments": ["Zm9v"],
        },
    )
    assert send_v2.status_code == 201
    timestamp = int(send_v2.json()["timestamp"])

    inbox = client.get("/v1/receive/+15559998888")
    assert inbox.status_code == 200
    assert inbox.json()[0]["message"] == "Hello"

    reaction = client.post(
        "/v1/reactions/+15554445555",
        json={
            "reaction": "👍",
            "recipient": "+15559998888",
            "target_author": "+15554445555",
            "timestamp": timestamp,
        },
    )
    assert reaction.status_code == 204

    remove_reaction = client.delete(
        "/v1/reactions/+15554445555",
        json={
            "reaction": "👍",
            "recipient": "+15559998888",
            "target_author": "+15554445555",
            "timestamp": timestamp,
        },
    )
    assert remove_reaction.status_code == 204

    receipt = client.post(
        "/v1/receipts/+15554445555",
        json={"receipt_type": "read", "recipient": "+15559998888", "timestamp": timestamp},
    )
    assert receipt.status_code == 204

    typing_start = client.put(
        "/v1/typing-indicator/+15554445555",
        json={"recipient": "+15559998888"},
    )
    assert typing_start.status_code == 204

    typing_stop = client.delete(
        "/v1/typing-indicator/+15554445555",
        json={"recipient": "+15559998888"},
    )
    assert typing_stop.status_code == 204

    remote_delete = client.delete(
        "/v1/remote-delete/+15554445555",
        json={"recipient": "+15559998888", "timestamp": timestamp},
    )
    assert remote_delete.status_code == 201


def test_search_and_stickers(client: TestClient) -> None:
    """Search and sticker pack operations follow the swagger documentation."""

    client.post("/v1/register/+15558887777")

    sticker_add = client.post(
        "/v1/sticker-packs/+15558887777",
        json={"pack_id": "pack-1", "pack_key": "key-1"},
    )
    assert sticker_add.status_code == 204

    sticker_list = client.get("/v1/sticker-packs/+15558887777")
    assert sticker_list.status_code == 200
    assert sticker_list.json()[0]["id"] == "pack-1"

    search = client.get(
        "/v1/search/+15558887777",
        params=("numbers", "+15558887777"),
    )
    assert search.status_code == 200
    assert search.json()[0]["registered"] is True
