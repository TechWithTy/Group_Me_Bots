"""
Signal General API Routes

This module handles general API operations including:
- API information and health checks
- Configuration management
- Account-specific settings
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Path, Body
from pydantic import BaseModel

router = APIRouter()


# Pydantic models for request/response bodies
class LoggingConfiguration(BaseModel):
    level: Optional[str] = None


class Configuration(BaseModel):
    logging: Optional[LoggingConfiguration] = None


class TrustModeRequest(BaseModel):
    trust_mode: str


class TrustModeResponse(BaseModel):
    trust_mode: str


class AboutResponse(BaseModel):
    build: int
    capabilities: dict
    mode: str
    version: str
    versions: List[str]


class ErrorResponse(BaseModel):
    error: str


@router.get("/about")
async def get_about():
    """
    Returns the supported API versions and the internal build nr.

    Provides general information about the API including supported versions.
    """
    # TODO: Implement about endpoint logic
    return AboutResponse(
        build=12345,
        capabilities={"gv2": ["create", "update"]},
        mode="native",
        version="1.0.0",
        versions=["v1"]
    )


@router.get("/health")
async def health_check():
    """
    API Health Check.

    Internally used by the docker container to perform health checks.
    """
    # TODO: Implement health check logic
    return {"status": "healthy"}


@router.get("/configuration")
async def get_configuration():
    """
    List the REST API configuration.

    Returns the current API configuration settings.
    """
    # TODO: Implement configuration retrieval logic
    return Configuration(
        logging=LoggingConfiguration(level="INFO")
    )


@router.post("/configuration")
async def set_configuration(
    data: Configuration = Body(..., description="Configuration")
):
    """
    Set the REST API configuration.

    Updates the API configuration with the provided settings.
    """
    # TODO: Implement configuration update logic
    return {"message": "Configuration updated successfully"}


@router.get("/configuration/{number}/settings")
async def get_account_settings(
    number: str = Path(..., description="Registered Phone Number"),
    data: TrustModeResponse = Body(..., description="Request")
):
    """
    List account specific settings.

    Returns account-specific configuration settings.
    """
    # TODO: Implement account settings retrieval logic
    return {"trust_mode": "TRUSTED_UNVERIFIED"}


@router.post("/configuration/{number}/settings")
async def set_account_settings(
    number: str = Path(..., description="Registered Phone Number"),
    data: TrustModeRequest = Body(..., description="Request")
):
    """
    Set account specific settings.

    Updates account-specific settings like trust mode.
    """
    # TODO: Implement account settings update logic
    return {"message": "Account settings updated successfully"}
