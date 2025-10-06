"""
Signal Profiles API Routes

This module handles profile-related operations including:
- Profile updates (name, avatar, about)
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Path, Body
from pydantic import BaseModel

router = APIRouter()


# Pydantic models for request/response bodies
class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    about: Optional[str] = None
    base64_avatar: Optional[str] = None


class ErrorResponse(BaseModel):
    error: str


@router.put("/{number}")
async def update_profile(
    number: str = Path(..., description="Registered Phone Number"),
    data: UpdateProfileRequest = Body(..., description="Profile Data")
):
    """
    Update Profile.

    Set your name and optional avatar and about information.
    """
    # TODO: Implement profile update logic
    return {"message": "Profile updated successfully"}
