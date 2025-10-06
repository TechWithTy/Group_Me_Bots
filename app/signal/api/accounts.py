"""
Signal Accounts API Routes

This module handles all account-related operations including:
- PIN management
- Account settings
- Username management
- Rate limit challenges
"""

from __future__ import annotations

import secrets
from typing import Optional

from fastapi import APIRouter, Body, HTTPException, Path, Response, status
from pydantic import BaseModel, Field

from .helpers import ensure_account, now_ms, state

router = APIRouter()


class SetPinRequest(BaseModel):
    pin: str = Field(..., min_length=4)


class RateLimitChallengeRequest(BaseModel):
    captcha: str
    challenge_token: str


class UpdateAccountSettingsRequest(BaseModel):
    discoverable_by_number: Optional[bool] = None
    share_number: Optional[bool] = None


class SetUsernameRequest(BaseModel):
    username: str = Field(..., min_length=1)


class SetUsernameResponse(BaseModel):
    username: str
    discriminator: str
    username_link: str


@router.get("", response_model=list[str])
async def list_accounts() -> list[str]:
    return sorted(state.accounts)


@router.post("/{number}/pin", status_code=status.HTTP_201_CREATED)
async def set_pin(
    number: str = Path(..., description="Registered Phone Number"),
    data: SetPinRequest = Body(..., description="Request"),
) -> Response:
    account = ensure_account(number)
    if not data.pin.isdigit():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="PIN must contain only digits")
    account.pin = data.pin
    return Response(status_code=status.HTTP_201_CREATED)


@router.delete("/{number}/pin", status_code=status.HTTP_204_NO_CONTENT)
async def remove_pin(number: str = Path(..., description="Registered Phone Number")) -> Response:
    account = ensure_account(number)
    account.pin = None
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{number}/rate-limit-challenge", status_code=status.HTTP_204_NO_CONTENT)
async def lift_rate_limit(
    number: str = Path(..., description="Registered Phone Number"),
    data: RateLimitChallengeRequest = Body(..., description="Request"),
) -> Response:
    account = ensure_account(number)
    account.rate_limit_events.append((data.captcha, data.challenge_token, now_ms()))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{number}/settings", status_code=status.HTTP_204_NO_CONTENT)
async def update_account_settings(
    number: str = Path(..., description="Registered Phone Number"),
    data: UpdateAccountSettingsRequest = Body(..., description="Request"),
) -> Response:
    account = ensure_account(number)
    if data.discoverable_by_number is not None:
        account.settings.discoverable_by_number = data.discoverable_by_number
    if data.share_number is not None:
        account.settings.share_number = data.share_number
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{number}/username", response_model=SetUsernameResponse, status_code=status.HTTP_201_CREATED)
async def set_username(
    number: str = Path(..., description="Registered Phone Number"),
    data: SetUsernameRequest = Body(..., description="Request"),
) -> SetUsernameResponse:
    account = ensure_account(number)
    discriminator = f"{secrets.randbelow(900)+100}"
    account.username = data.username
    account.username_discriminator = discriminator
    account.username_link = f"signal.me/#eu/{data.username}.{discriminator}"
    return SetUsernameResponse(
        username=data.username,
        discriminator=discriminator,
        username_link=account.username_link,
    )


@router.delete("/{number}/username", status_code=status.HTTP_204_NO_CONTENT)
async def remove_username(number: str = Path(..., description="Registered Phone Number")) -> Response:
    account = ensure_account(number)
    account.username = None
    account.username_discriminator = None
    account.username_link = None
    return Response(status_code=status.HTTP_204_NO_CONTENT)
