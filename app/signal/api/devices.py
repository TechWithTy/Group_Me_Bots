"""
Signal Devices API Routes

This module handles all device-related operations including:
- Device registration and verification
- Device linking and management
- Device listing
- Account unregistration
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Body, HTTPException, Path, Query, Response, status
from pydantic import BaseModel

from .helpers import ensure_account, now_ms, placeholder_image, state
from .state.models import Device

router = APIRouter()


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


def _ensure_primary_device(account) -> None:
    if account.devices:
        return
    ident = account.next_device_id
    account.devices[ident] = Device(
        identifier=ident,
        name="Primary Device",
        created=now_ms(),
        last_seen=now_ms(),
        uri="device://primary",
    )
    account.next_device_id += 1


@router.post("/register/{number}", status_code=status.HTTP_201_CREATED)
async def register_number(
    number: str = Path(..., description="Registered Phone Number"),
    data: Optional[RegisterNumberRequest] = Body(None, description="Additional Settings"),
) -> Response:
    account = ensure_account(number)
    account.registered = True
    _ensure_primary_device(account)
    return Response(status_code=status.HTTP_201_CREATED)


@router.post("/register/{number}/verify/{token}", status_code=status.HTTP_201_CREATED)
async def verify_number(
    number: str = Path(..., description="Registered Phone Number"),
    token: str = Path(..., description="Verification Code"),
    data: Optional[VerifyNumberSettings] = Body(None, description="Additional Settings"),
) -> Response:
    account = ensure_account(number)
    if not account.registered:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Number not registered")
    account.verified = True
    if data and data.pin:
        account.pin = data.pin
    return Response(status_code=status.HTTP_201_CREATED)


@router.get("/qrcodelink")
async def link_device_qr(
    device_name: str = Query(..., description="Device Name"),
    qrcode_version: Optional[int] = Query(10, description="QRCode Version"),
) -> dict:
    return {"qr_code": placeholder_image(f"{device_name}:{qrcode_version or 10}")}


@router.get("/devices/{number}", response_model=list[ListDevicesResponse])
async def list_devices(number: str = Path(..., description="Registered Phone Number")) -> list[ListDevicesResponse]:
    account = ensure_account(number)
    _ensure_primary_device(account)
    return [
        ListDevicesResponse(id=device.identifier, name=device.name, created=device.created, last_seen=device.last_seen)
        for device in account.devices.values()
    ]


@router.post("/devices/{number}", status_code=status.HTTP_204_NO_CONTENT)
async def link_device(
    number: str = Path(..., description="Registered Phone Number"),
    data: AddDeviceRequest = Body(..., description="Request"),
) -> Response:
    account = ensure_account(number)
    _ensure_primary_device(account)
    ident = account.next_device_id
    account.devices[ident] = Device(
        identifier=ident,
        name=f"Linked Device {ident}",
        created=now_ms(),
        last_seen=now_ms(),
        uri=data.uri,
    )
    account.next_device_id += 1
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/unregister/{number}", status_code=status.HTTP_204_NO_CONTENT)
async def unregister_number(
    number: str = Path(..., description="Registered Phone Number"),
    data: Optional[UnregisterNumberRequest] = Body(None, description="Additional Settings"),
) -> Response:
    if data and data.delete_account:
        state.accounts.pop(number, None)
    else:
        account = ensure_account(number)
        account.registered = False
        account.verified = False
    return Response(status_code=status.HTTP_204_NO_CONTENT)
