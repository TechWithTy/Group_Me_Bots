"""
Signal Search API Routes

This module handles number search operations including:
- Checking if phone numbers are registered with Signal
"""

from typing import List

from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel

router = APIRouter()


# Pydantic models for request/response bodies
class SearchResponse(BaseModel):
    number: str
    registered: bool


class ErrorResponse(BaseModel):
    error: str


@router.get("/{number}")
async def search_numbers(
    number: str = Path(..., description="Registered Phone Number"),
    numbers: List[str] = Query(..., description="Numbers to check")
):
    """
    Check if one or more phone numbers are registered with the Signal Service.

    Checks the registration status of the specified phone numbers.
    """
    # TODO: Implement number search logic
    results = []
    for phone_number in numbers:
        # TODO: Implement actual search logic
        results.append(SearchResponse(
            number=phone_number,
            registered=True  # Placeholder
        ))

    return results
