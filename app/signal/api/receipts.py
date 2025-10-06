"""Read receipt endpoints used by the API specification."""

from __future__ import annotations

from fastapi import APIRouter, Body, Path, Response, status
from pydantic import BaseModel

from .helpers import ensure_account
from .state.models import Receipt


router = APIRouter()


class ReceiptRequest(BaseModel):
    receipt_type: str
    recipient: str
    timestamp: int


@router.post("/{number}", status_code=status.HTTP_204_NO_CONTENT)
async def send_receipt(
    number: str = Path(..., description="Registered phone number"),
    data: ReceiptRequest = Body(..., description="Receipt"),
) -> Response:
    """Record a read/viewed receipt for a conversation."""

    account = ensure_account(number)
    ensure_account(data.recipient)
    account.receipts.append(
        Receipt(receipt_type=data.receipt_type, recipient=data.recipient, timestamp=data.timestamp)
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
