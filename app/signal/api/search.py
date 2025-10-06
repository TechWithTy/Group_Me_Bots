"""
Signal Search API Routes

This module handles number search operations including:
- Checking if phone numbers are registered with Signal
"""

from typing import List

from fastapi import APIRouter, HTTPException, Path, Query, status
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
    try:
        # Check if phone numbers are registered with Signal Service
        # This would typically query the Signal directory service
        
        # Validate input numbers
        if not numbers:
            raise ValueError("At least one number must be provided")
        
        # TODO: Replace with actual Signal API calls
        # results = []
        # for phone_number in numbers:
        #     is_registered = signal_client.check_registration(phone_number)
        #     results.append(SearchResponse(
        #         number=phone_number,
        #         registered=is_registered
        #     ))
        
        # For now, simulate realistic registration check results
        results = []
        for phone_number in numbers:
            # Simulate some numbers being registered, others not
            # In real implementation, this would query Signal's directory
            registered = phone_number in ["+1234567890", "+1987654321"]
            results.append(SearchResponse(
                number=phone_number,
                registered=registered
            ))
        
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(error=str(e)).dict()
        )
