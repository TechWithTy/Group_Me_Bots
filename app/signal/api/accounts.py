"""
Signal Accounts API Routes

This module handles all account-related operations including:
- PIN management
- Account settings
- Username management
- Rate limit challenges
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Path, Body
from pydantic import BaseModel

router = APIRouter()


# Pydantic models for request/response bodies
class SetPinRequest(BaseModel):
    pin: str


class RateLimitChallengeRequest(BaseModel):
    captcha: str
    challenge_token: str


class UpdateAccountSettingsRequest(BaseModel):
    discoverable_by_number: Optional[bool] = None
    share_number: Optional[bool] = None


class SetUsernameRequest(BaseModel):
    username: str


class ErrorResponse(BaseModel):
    error: str


@router.get("/")
async def list_accounts():
    """
    Lists all of the accounts linked or registered.

    Returns a list of registered phone numbers.
    """
    # TODO: Implement actual account listing logic
    return ["+1234567890"]  # Placeholder response


@router.post("/{number}/pin")
async def set_pin(
    number: str = Path(..., description="Registered Phone Number"),
    data: SetPinRequest = Body(..., description="Request")
):
    """
    Sets a new Signal Pin.

    This endpoint allows setting a PIN for the specified account.
    """
    # TODO: Implement PIN setting logic
    return {"message": "PIN set successfully"}


@router.delete("/{number}/pin")
async def remove_pin(
    number: str = Path(..., description="Registered Phone Number")
):
    """
    Removes a Signal Pin.

    This endpoint allows removing the PIN for the specified account.
    """
    # TODO: Implement PIN removal logic
    return {"message": "PIN removed successfully"}


@router.post("/{number}/rate-limit-challenge")
async def lift_rate_limit(
    number: str = Path(..., description="Registered Phone Number"),
    data: RateLimitChallengeRequest = Body(..., description="Request")
):
    """
    Lift rate limit restrictions by solving a captcha.

    When running into rate limits, sometimes the limit can be lifted by solving a CAPTCHA.
    """
    # TODO: Implement rate limit challenge logic
    return {"message": "Rate limit lifted successfully"}


@router.put("/{number}/settings")
async def update_account_settings(
    number: str = Path(..., description="Registered Phone Number"),
    data: UpdateAccountSettingsRequest = Body(..., description="Request")
):
    """
    Update the account attributes on the signal server.

    This endpoint allows updating account settings like discoverability and number sharing.
    """
    # TODO: Implement account settings update logic
    return {"message": "Account settings updated successfully"}


@router.post("/{number}/username")
async def set_username(
    number: str = Path(..., description="Registered Phone Number"),
    data: SetUsernameRequest = Body(..., description="Request")
):
    """
    Set a username.

    Allows setting the username that should be used for this account.
    Can be just the nickname or the complete username with discriminator.
    Returns the new username with discriminator and the username link.
    """
    # TODO: Implement username setting logic
    return {
        "username": data.username,
        "discriminator": "123",
        "username_link": f"signal.me/#eu/{data.username}.123"
    }


@router.delete("/{number}/username")
async def remove_username(
    number: str = Path(..., description="Registered Phone Number")
):
    """
    Remove a username.

    Delete the username associated with this account.
    """
    # TODO: Implement username removal logic
    return {"message": "Username removed successfully"}
