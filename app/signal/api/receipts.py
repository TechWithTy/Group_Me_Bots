"""
Signal Receipts API Routes

This module handles read receipt operations.
Note: Receipts are also handled in the messages module for sending receipts.
This module provides a separate endpoint if needed for receipt-specific operations.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_receipts():
    """
    Get message receipts.

    This endpoint would be used to retrieve receipt information for messages.
    Currently, receipt operations are handled in the messages module.
    """
    # TODO: Implement receipt retrieval logic if needed
    return {"message": "Receipts endpoint - see messages module for receipt operations"}
