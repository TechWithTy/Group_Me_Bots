"""
Signal Attachments API Routes

This module handles all attachment-related operations including:
- Attachment listing
- Attachment serving
- Attachment deletion
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Path, Response, status

from .helpers import state

router = APIRouter()


@router.get("", response_model=list[str])
async def list_attachments() -> list[str]:
    return sorted(state.attachments)


@router.get("/{attachment}")
async def serve_attachment(attachment: str = Path(..., description="Attachment ID")) -> dict:
    stored = state.attachments.get(attachment)
    if stored is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")
    return {"content": stored.content, "content_type": stored.content_type}


@router.delete("/{attachment}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(attachment: str = Path(..., description="Attachment ID")) -> Response:
    if attachment not in state.attachments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")
    state.attachments.pop(attachment, None)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
