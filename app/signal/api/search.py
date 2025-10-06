"""Phone number search endpoints for the unofficial Signal API."""

from __future__ import annotations

from typing import List, Sequence

from fastapi import APIRouter, HTTPException, Path, Query, Request, status
from pydantic import BaseModel

from .helpers import ensure_account, state

router = APIRouter()


class SearchResponse(BaseModel):
    number: str
    registered: bool


@router.get("/{number}")
async def search_numbers(
    request: Request,
    number: str = Path(..., description="Registered Phone Number"),
    numbers: Sequence[str] | str | None = Query(None, description="Numbers to check"),
) -> List[SearchResponse]:
    ensure_account(number)
    if numbers is None:
        extracted = request.query_params.getlist("numbers")
    elif isinstance(numbers, str):
        extracted = [numbers]
    else:
        extracted = list(numbers)
    if not extracted:
        extracted = [number]
    return [
        SearchResponse(
            number=phone_number,
            registered=bool(state.accounts.get(phone_number) and state.accounts[phone_number].registered),
        )
        for phone_number in extracted
    ]
