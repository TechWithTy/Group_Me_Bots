"""
Signal Devices API Routes

This module handles all device-related operations including:
- Device registration and verification
- Device linking and management
- Device listing
- Account unregistration
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Path, Body, Query
from pydantic import BaseModel

router = APIRouter()


# Pydantic models for request/response bodies
class RegisterNumberRequest(BaseModel):
    captcha: Optional[str] = None
    use_voice: Optional[bool] = False


class VerifyNumberSettings(BaseModel):
    pin: Optional[str] = None


class AddDeviceRequest(BaseModel):
    uri: str


class UnregisterNumberRequest(BaseModel):
    delete_account: Optional[bool] = False
    delete_local_data: Optional[bool] = False


class ListDevicesResponse(BaseModel):
    id: int
    name: str
    created: int
    last_seen: int
    # Additional fields would be added based on actual API response


class ErrorResponse(BaseModel):
    error: str


@router.post("/register/{number}")
async def register_number(
    number: str = Path(..., description="Registered Phone Number"),
    data: Optional[RegisterNumberRequest] = Body(None, description="Additional Settings")
):
    """
    Register a phone number with the signal network.

    Initiates the registration process for a phone number.
    """
    # TODO: Implement number registration logic
    return {"message": "Registration initiated"}


@router.post("/register/{number}/verify/{token}")
async def verify_number(
    number: str = Path(..., description="Registered Phone Number"),
    token: str = Path(..., description="Verification Code"),
    data: Optional[VerifyNumberSettings] = Body(None, description="Additional Settings")
):
    """
    Verify a registered phone number with the signal network.

    Completes the verification process using the SMS or voice code.
    """
    # TODO: Implement number verification logic
    return {"message": "Number verified successfully"}


@router.get("/qrcodelink")
async def link_device_qr(
    device_name: str = Query(..., description="Device Name"),
    qrcode_version: Optional[int] = Query(10, description="QRCode Version")
):
    """
    Link device and generate QR code.

    Generates a QR code for linking a new device to the account.
    """
    # TODO: Implement QR code generation logic
    return {"qr_code": "base64_encoded_qr_code"}


@router.get("/devices/{number}")
async def list_devices(
    number: str = Path(..., description="Registered Phone Number")
):
    """
    List linked devices associated to this device.

    Returns a list of all devices linked to this account.
    """
    # TODO: Implement device listing logic
    return [
        ListDevicesResponse(
            id=1,
            name="Primary Device",
            created=1234567890,
            last_seen=1234567890
        )
    ]


@router.post("/devices/{number}")
async def link_device(
    number: str = Path(..., description="Registered Phone Number"),
    data: AddDeviceRequest = Body(..., description="Request")
):
    """
    Links another device to this device.

    Links a new device to the existing account.
    Only works if this is the master device.
    """
    # TODO: Implement device linking logic
    return {"message": "Device linked successfully"}


@router.post("/unregister/{number}")
async def unregister_number(
    number: str = Path(..., description="Registered Phone Number"),
    data: Optional[UnregisterNumberRequest] = Body(None, description="Additional Settings")
):
    """
    Unregister a phone number.

    Disables push support for this device.
    WARNING: If delete_account is true, the account will be deleted permanently.
    """
    # TODO: Implement number unregistration logic
    return {"message": "Number unregistered successfully"}
