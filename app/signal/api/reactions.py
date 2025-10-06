"""
Signal Reactions API Routes

This module handles message reaction operations.
Note: Reactions are also handled in the messages module for sending/removing reactions.
This module provides a separate endpoint if needed for reaction-specific operations.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_reactions():
    """
    Get message reactions.

    This endpoint would be used to retrieve reactions for messages.
    Currently, reaction operations are handled in the messages module.
    """
    # TODO: Implement reaction retrieval logic if needed
    return {"message": "Reactions endpoint - see messages module for reaction operations"}
