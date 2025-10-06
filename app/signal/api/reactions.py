"""
Signal Reactions API Routes

This module handles message reaction operations.
Note: Reactions are also handled in the messages module for sending/removing reactions.
This module provides a separate endpoint if needed for reaction-specific operations.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter()


@router.get("/")
async def get_reactions():
    """
    Get message reactions.

    This endpoint would be used to retrieve reactions for messages.
    Currently, reaction operations are handled in the messages module.
    """
    try:
        # Get message reactions for the account
        # This would typically query Signal for reactions data

        # TODO: Replace with actual Signal API call
        # reactions = signal_client.get_reactions()

        # For now, return a placeholder indicating reactions are handled in messages module
        return {
            "message": "Reactions endpoint - see messages module for reaction operations",
            "reactions_handled_in": "/v1/reactions/{number}"
        }
    except Exception as e:
        class ErrorResponse(BaseModel):
            error: str

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(error=str(e)).dict()
        )
