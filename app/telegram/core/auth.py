"""
Authentication middleware for Telegram API endpoints.
"""
from __future__ import annotations

import hashlib
import hmac
import time
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.telegram.core.config import settings

security = HTTPBearer(auto_error=False)


class TelegramAuth:
    """Telegram authentication utilities."""

    @staticmethod
    def verify_telegram_auth(auth_data: Dict[str, Any]) -> bool:
        """
        Verify Telegram authentication data.

        Args:
            auth_data: Dictionary containing Telegram auth data

        Returns:
            bool: True if authentication is valid
        """
        # Check if data is too old (5 minutes max)
        if 'auth_date' in auth_data:
            auth_date = int(auth_data['auth_date'])
            current_time = int(time.time())
            if current_time - auth_date > 300:  # 5 minutes
                return False

        # Create data check string
        check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(auth_data.items())
            if k != 'hash'
        )

        # Create secret key
        secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()

        # Calculate hash
        calculated_hash = hmac.new(
            secret_key,
            check_string.encode(),
            hashlib.sha256
        ).hexdigest()

        # Compare hashes
        return calculated_hash == auth_data.get('hash')


def verify_telegram_user(
    telegram_id: str,
    auth_data: Optional[Dict[str, Any]] = None,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    """
    Verify Telegram user authentication.

    Args:
        telegram_id: Telegram user ID
        auth_data: Optional Telegram authentication data
        credentials: Optional Bearer token credentials

    Returns:
        Dict containing user information

    Raises:
        HTTPException: If authentication fails
    """
    # If no auth data provided, check for Bearer token
    if not auth_data and credentials:
        # TODO: Implement JWT token verification
        # For now, assume token is valid if provided
        return {
            "user_id": telegram_id,
            "authenticated": True,
            "method": "bearer_token"
        }

    # If auth data provided, verify it
    if auth_data:
        if not TelegramAuth.verify_telegram_auth(auth_data):
            raise HTTPException(
                status_code=401,
                detail="Invalid Telegram authentication data"
            )

        return {
            "user_id": telegram_id,
            "authenticated": True,
            "method": "telegram_auth",
            "username": auth_data.get("username"),
            "first_name": auth_data.get("first_name"),
            "last_name": auth_data.get("last_name"),
        }

    # No authentication provided
    raise HTTPException(
        status_code=401,
        detail="Authentication required"
    )


async def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Get current authenticated user from request.

    This middleware function extracts user information from the request
    and verifies authentication.

    Args:
        request: FastAPI request object

    Returns:
        Dict containing user information

    Raises:
        HTTPException: If authentication fails
    """
    # Extract Telegram user ID from request (this would come from bot context)
    # For now, we'll use a placeholder - in real implementation this would
    # come from the Telegram bot's user context
    telegram_id = getattr(request.state, "telegram_user_id", None)

    if not telegram_id:
        raise HTTPException(
            status_code=401,
            detail="User ID not found in request context"
        )

    # Extract auth data from request body/headers if available
    auth_data = None
    if hasattr(request.state, "auth_data"):
        auth_data = request.state.auth_data

    return verify_telegram_user(str(telegram_id), auth_data)
