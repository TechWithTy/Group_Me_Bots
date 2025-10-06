"""General informational and configuration endpoints for the Signal API."""

from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import APIRouter, Body, Path, Response, status
from pydantic import BaseModel, Field

from .helpers import ensure_account, state


router = APIRouter()


class LoggingConfiguration(BaseModel):
    level: Optional[str] = Field(default="INFO")


class Configuration(BaseModel):
    logging: LoggingConfiguration = Field(default_factory=LoggingConfiguration)


class TrustModeRequest(BaseModel):
    trust_mode: str


class TrustModeResponse(BaseModel):
    trust_mode: str


class AboutResponse(BaseModel):
    build: int
    capabilities: Dict[str, object]
    mode: str
    version: str
    versions: List[str]


@router.get("/about", response_model=AboutResponse)
async def get_about() -> AboutResponse:
    """Return static build metadata enriched with basic usage stats."""

    account_count = len(state.accounts)
    attachment_count = len(state.attachments)
    return AboutResponse(
        build=1,
        capabilities={
            "accounts": ["register", "verify", "settings"],
            "attachments": ["list", "retrieve", "delete"],
            "messages": ["send", "receive", "react"],
            "stats": {"accounts": account_count, "attachments": attachment_count},
        },
        mode="native",
        version="1.0.0",
        versions=["v1"],
    )


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Expose a simple health indicator for readiness checks."""

    return {"status": "healthy"}


@router.get("/configuration", response_model=Configuration)
async def get_configuration() -> Configuration:
    """Return the mutable API configuration tracked in memory."""

    return Configuration(logging=LoggingConfiguration(level=state.configuration.logging.level))


@router.post("/configuration", status_code=status.HTTP_204_NO_CONTENT)
async def set_configuration(data: Configuration = Body(..., description="Configuration")) -> Response:
    """Persist configuration changes provided by the caller."""

    if data.logging and data.logging.level:
        state.configuration.logging.level = data.logging.level
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/configuration/{number}/settings", response_model=TrustModeResponse)
async def get_account_settings(number: str = Path(..., description="Registered Phone Number")) -> TrustModeResponse:
    """Return the trust mode associated with a specific account."""

    account = ensure_account(number)
    return TrustModeResponse(trust_mode=account.trust_mode)


@router.post("/configuration/{number}/settings", status_code=status.HTTP_204_NO_CONTENT)
async def set_account_settings(
    number: str = Path(..., description="Registered Phone Number"),
    data: TrustModeRequest = Body(..., description="Request"),
) -> Response:
    """Update the trust mode tracked for an account."""

    account = ensure_account(number)
    account.trust_mode = data.trust_mode
    return Response(status_code=status.HTTP_204_NO_CONTENT)
