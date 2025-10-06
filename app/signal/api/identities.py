"""Endpoints for managing identity trust state."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Body, Path, Response, status
from pydantic import BaseModel

from .helpers import ensure_account, now_ms
from .state.models import Identity

router = APIRouter()


class TrustIdentityRequest(BaseModel):
    verified_safety_number: Optional[str] = None
    trust_all_known_keys: Optional[bool] = False


class IdentityEntry(BaseModel):
    number: str
    uuid: str
    trust_level: str
    added_timestamp: int


@router.get("/{number}", response_model=list[IdentityEntry])
async def list_identities(number: str = Path(..., description="Registered Phone Number")) -> list[IdentityEntry]:
    account = ensure_account(number)
    return [
        IdentityEntry(
            number=identity.number,
            uuid=identity.uuid,
            trust_level=identity.trust_level,
            added_timestamp=identity.added_timestamp,
        )
        for identity in account.identities.values()
    ]


@router.put("/{number}/trust/{number_to_trust}", status_code=status.HTTP_204_NO_CONTENT)
async def trust_identity(
    number: str = Path(..., description="Registered Phone Number"),
    number_to_trust: str = Path(..., description="Number To Trust"),
    data: TrustIdentityRequest = Body(..., description="Input Data"),
) -> Response:
    account = ensure_account(number)
    trust_level = "TRUSTED_VERIFIED" if data.trust_all_known_keys or data.verified_safety_number else "TRUSTED_UNVERIFIED"
    uuid = f"uuid-{number_to_trust.strip('+')}"
    account.identities[number_to_trust] = Identity(
        number=number_to_trust,
        uuid=uuid,
        trust_level=trust_level,
        added_timestamp=now_ms(),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)

