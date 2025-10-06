from __future__ import annotations

import base64
from typing import Optional

from fastapi import APIRouter, Body, HTTPException, Path, Response, status
from pydantic import BaseModel

from .helpers import ensure_account, placeholder_image
from .state.models import Contact

router = APIRouter()


class UpdateContactRequest(BaseModel):
    recipient: str
    name: Optional[str] = None
    expiration_in_seconds: Optional[int] = None


class ListContactsResponse(BaseModel):
    number: str
    name: Optional[str] = None
    uuid: Optional[str] = None
    profile_key: Optional[str] = None


def _generate_uuid(recipient: str) -> str:
    return base64.b64encode(recipient.encode()).decode().strip("=")


def _profile_key(recipient: str) -> str:
    return base64.b64encode(f"profile-{recipient}".encode()).decode()


@router.get("/{number}", response_model=list[ListContactsResponse])
async def list_contacts(number: str = Path(..., description="Registered Phone Number")) -> list[ListContactsResponse]:
    account = ensure_account(number)
    return [
        ListContactsResponse(
            number=contact.number,
            name=contact.name,
            uuid=uuid,
            profile_key=contact.profile_key,
        )
        for uuid, contact in account.contacts.items()
    ]


@router.put("/{number}", status_code=status.HTTP_204_NO_CONTENT)
async def update_contact(
    number: str = Path(..., description="Registered Phone Number"),
    data: UpdateContactRequest = Body(..., description="Contact"),
) -> Response:
    if not data.recipient:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Recipient number is required")
    account = ensure_account(number)
    contact_uuid = _generate_uuid(data.recipient)
    contact = account.contacts.get(contact_uuid)
    if contact is None:
        contact = Contact(
            uuid=contact_uuid,
            number=data.recipient,
            name=data.name,
            profile_key=_profile_key(data.recipient),
            avatar=placeholder_image(contact_uuid),
            expiration_in_seconds=data.expiration_in_seconds,
        )
        account.contacts[contact_uuid] = contact
    else:
        contact.number = data.recipient
        contact.name = data.name
        contact.profile_key = _profile_key(data.recipient)
        contact.avatar = placeholder_image(contact_uuid)
        contact.expiration_in_seconds = data.expiration_in_seconds
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{number}/sync", status_code=status.HTTP_204_NO_CONTENT)
async def sync_contacts(number: str = Path(..., description="Registered Phone Number")) -> Response:
    ensure_account(number)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{number}/{uuid}", response_model=ListContactsResponse)
async def get_contact(
    number: str = Path(..., description="Registered Phone Number"),
    uuid: str = Path(..., description="Contact UUID"),
) -> ListContactsResponse:
    account = ensure_account(number)
    contact = account.contacts.get(uuid)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return ListContactsResponse(
        number=contact.number,
        name=contact.name,
        uuid=uuid,
        profile_key=contact.profile_key,
    )


@router.get("/{number}/{uuid}/avatar")
async def get_contact_avatar(
    number: str = Path(..., description="Registered Phone Number"),
    uuid: str = Path(..., description="Contact UUID"),
) -> dict:
    account = ensure_account(number)
    contact = account.contacts.get(uuid)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return {"avatar": contact.avatar or placeholder_image(uuid), "content_type": "image/png"}

