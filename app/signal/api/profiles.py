"""Profile update endpoints exposed by the unofficial Signal API."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Body, Path, Response, status
from pydantic import BaseModel

from .helpers import ensure_account, placeholder_image

router = APIRouter()


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    about: Optional[str] = None
    base64_avatar: Optional[str] = None


@router.put("/{number}", status_code=status.HTTP_204_NO_CONTENT)
async def update_profile(
    number: str = Path(..., description="Registered Phone Number"),
    data: UpdateProfileRequest = Body(..., description="Profile Data"),
) -> Response:
    account = ensure_account(number)
    if data.name is not None:
        account.profile_name = data.name
    if data.about is not None:
        account.profile_about = data.about
    if data.base64_avatar is not None:
        account.profile_avatar = data.base64_avatar or placeholder_image(number)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
