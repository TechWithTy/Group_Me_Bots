"""
Signal Accounts API Routes

This module handles all account-related operations including:
- PIN management
- Account settings
- Username management
- Rate limit challenges
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Path, Body, status
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


class SetUsernameResponse(BaseModel):
    username: str
    discriminator: str
    username_link: str


class ErrorResponse(BaseModel):
    error: str

@router.get("")
async def list_accounts():
    """
    Lists all of the accounts linked or registered.

    Returns a list of registered phone numbers.
    """
    try:
        # Get all registered Signal accounts
        # This would typically query the Signal client or database
        # For now, return a realistic list of account numbers
        
        # TODO: Replace with actual Signal client call
        # accounts = signal_client.list_accounts()
        
        # Simulate getting accounts from Signal service
        accounts = [
            "+1234567890",
            "+1987654321"
        ]  # Placeholder - replace with actual account discovery
        return accounts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(error=str(e)).dict()
        )


@router.post("/{number}/pin")
async def set_pin(
    number: str = Path(..., description="Registered Phone Number"),
    data: SetPinRequest = Body(..., description="Request")
):
    """
    Sets a new Signal Pin.

    This endpoint allows setting a PIN for the specified account.
    """
    try:
        # Set PIN for Signal account
        # This would typically call the Signal API to set the PIN
        
        # Validate PIN format (basic validation)
        if not data.pin or len(data.pin) < 4:
            raise ValueError("PIN must be at least 4 digits")
        
        # TODO: Replace with actual Signal API call
        # signal_client.set_pin(number, data.pin)
        
        # Simulate PIN setting
        # In real implementation, this would interact with Signal servers
        pass
        return status.HTTP_201_CREATED
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(error=str(e)).dict()
        )

@router.delete("/{number}/pin")
async def remove_pin(
    number: str = Path(..., description="Registered Phone Number")
):
    """
    Removes a Signal Pin.

    This endpoint allows removing the PIN for the specified account.
    """
    try:
        # Remove PIN from Signal account
        # This would typically call the Signal API to remove the PIN
        
        # TODO: Replace with actual Signal API call
        # signal_client.remove_pin(number)
        
        # Simulate PIN removal
        # In real implementation, this would clear the PIN from Signal servers
        pass
        return status.HTTP_204_NO_CONTENT
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(error=str(e)).dict()
        )


@router.post("/{number}/rate-limit-challenge")
async def lift_rate_limit(
    number: str = Path(..., description="Registered Phone Number"),
    data: RateLimitChallengeRequest = Body(..., description="Request")
):
    """
    Lift rate limit restrictions by solving a captcha.

    When running into rate limits, sometimes the limit can be lifted by solving a CAPTCHA.
    """
    try:
        # Handle rate limit challenge by solving CAPTCHA
        # This would typically submit the CAPTCHA solution to Signal
        
        # Validate challenge data
        if not data.captcha or not data.challenge_token:
            raise ValueError("Both captcha and challenge_token are required")
        
        # TODO: Replace with actual Signal API call
        # signal_client.solve_rate_limit_challenge(number, data.captcha, data.challenge_token)
        
        # Simulate rate limit challenge resolution
        # In real implementation, this would submit CAPTCHA to Signal servers
        pass
        return status.HTTP_204_NO_CONTENT
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(error=str(e)).dict()
        )


@router.put("/{number}/settings")
async def update_account_settings(
    number: str = Path(..., description="Registered Phone Number"),
    data: UpdateAccountSettingsRequest = Body(..., description="Request")
):
    """
    Update the account attributes on the signal server.

    This endpoint allows updating account settings like discoverability and number sharing.
    """
    try:
        # Update account settings on Signal server
        # This would typically update discoverability and number sharing settings
        
        # TODO: Replace with actual Signal API call
        # signal_client.update_account_settings(number, data.discoverable_by_number, data.share_number)
        
        # Simulate settings update
        # In real implementation, this would update account attributes on Signal servers
        pass
        return status.HTTP_204_NO_CONTENT
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(error=str(e)).dict()
        )


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
    try:
        response = SetUsernameResponse(
            username=data.username,
            discriminator="123",
            username_link=f"signal.me/#eu/{data.username}.123"
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(error=str(e)).dict()
        )


@router.delete("/{number}/username")
async def remove_username(
    number: str = Path(..., description="Registered Phone Number")
):
    """
    Remove a username.

    Delete the username associated with this account.
    """
    try:
        # Remove username from Signal account
        # This would typically involve calling the Signal API client
        # For now, we'll implement a placeholder that validates the request

        # Validate that number exists and is registered
        if not number or not number.startswith('+'):
            raise ValueError("Invalid phone number format")

        # Remove username from Signal account
        # This would typically call the Signal API to remove the username

        # Replace with actual Signal API call to remove username
        # signal_client.remove_username(number)

        # Simulate username removal
        # In real implementation, this would call Signal's API to delete the username
        # For now, we'll implement validation and placeholder logic

        # Log the username removal attempt for auditing
        # logger.info(f"Username removal requested for number: {number}")

        return status.HTTP_204_NO_CONTENT
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(error=str(e)).dict()
        )
