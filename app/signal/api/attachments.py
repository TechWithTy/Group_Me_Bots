"""
Signal Attachments API Routes

This module handles all attachment-related operations including:
- Attachment listing
- Attachment serving
- Attachment deletion
"""

from typing import List

from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel

router = APIRouter()


# Pydantic models for request/response bodies
class ErrorResponse(BaseModel):
    error: str


@router.get("/")
async def list_attachments():
    """
    List all downloaded attachments.

    Returns a list of all attachment IDs that have been downloaded.
    """
    # TODO: Implement attachment listing logic
    return ["attachment_123", "attachment_456"]  # Placeholder response


@router.get("/{attachment}")
async def serve_attachment(
    attachment: str = Path(..., description="Attachment ID")
):
    """
    Serve the attachment with the given id.

    Returns the attachment data for the specified attachment ID.
    """
    # TODO: Implement attachment serving logic
    return {
        "id": attachment,
        "filename": "example.jpg",
        "content_type": "image/jpeg",
        "data": "base64_encoded_attachment_data"
    }


@router.delete("/{attachment}")
async def delete_attachment(
    attachment: str = Path(..., description="Attachment ID")
):
    """
    Remove the attachment with the given id from filesystem.

    Permanently deletes the specified attachment from the filesystem.
    """
    # TODO: Implement attachment deletion logic
    return {"message": "Attachment deleted successfully"}
