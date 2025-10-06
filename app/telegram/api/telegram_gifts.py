"""
Additional Telegram Bot API gifts and related endpoints.

This module extends the TelegramBotAPI with gifts and related methods.
"""

from typing import Optional, List, Dict, Any, Union

# Import base classes from telegram_api.py
from .telegram_api import TelegramBotAPI


class TelegramGiftsAPI(TelegramBotAPI):
    """Extension for gifts and related endpoints."""

    def send_gift(self, user_id: int, gift_id: str, **kwargs) -> bool:
        """Send a gift to a user."""
        params = {'user_id': user_id, 'gift_id': gift_id, **kwargs}
        response = self._make_request("sendGift", params)
        return response.get('ok', False)

    def verify_gift(self, gift_id: str, **kwargs) -> Dict[str, Any]:
        """Verify a gift."""
        params = {'gift_id': gift_id, **kwargs}
        response = self._make_request("verifyGift", params)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def get_available_gifts(self, **kwargs) -> List[Dict[str, Any]]:
        """Get available gifts."""
        response = self._make_request("getAvailableGifts", kwargs)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def get_user_gifts(self, user_id: int, **kwargs) -> List[Dict[str, Any]]:
        """Get gifts owned by a user."""
        params = {'user_id': user_id, **kwargs}
        response = self._make_request("getUserGifts", params)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def convert_gift_to_stars(self, gift_id: str, **kwargs) -> bool:
        """Convert a gift to Telegram Stars."""
        params = {'gift_id': gift_id, **kwargs}
        response = self._make_request("convertGiftToStars", params)
        return response.get('ok', False)

    def upgrade_gift(self, gift_id: str, **kwargs) -> Dict[str, Any]:
        """Upgrade a regular gift to a unique gift."""
        params = {'gift_id': gift_id, **kwargs}
        response = self._make_request("upgradeGift", params)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def transfer_gift(self, gift_id: str, to_user_id: int, **kwargs) -> bool:
        """Transfer a unique gift to another user."""
        params = {'gift_id': gift_id, 'to_user_id': to_user_id, **kwargs}
        response = self._make_request("transferGift", params)
        return response.get('ok', False)

    def get_gift_info(self, gift_id: str) -> Dict[str, Any]:
        """Get information about a gift."""
        params = {'gift_id': gift_id}
        response = self._make_request("getGiftInfo", params)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def get_gift_upgrade_preview(self, gift_id: str, **kwargs) -> Dict[str, Any]:
        """Get a preview of upgrading a gift."""
        params = {'gift_id': gift_id, **kwargs}
        response = self._make_request("getGiftUpgradePreview", params)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def gift_premium_subscription(self, user_id: int, months: int, **kwargs) -> bool:
        """Gift a Telegram Premium subscription."""
        params = {'user_id': user_id, 'months': months, **kwargs}
        response = self._make_request("giftPremiumSubscription", params)
        return response.get('ok', False)

    def get_my_star_balance(self) -> Dict[str, Any]:
        """Get the bot's Telegram Star balance."""
        response = self._make_request("getMyStarBalance")
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def get_business_account_star_balance(self, business_connection_id: str) -> Dict[str, Any]:
        """Get the Telegram Star balance of a business account."""
        params = {'business_connection_id': business_connection_id}
        response = self._make_request("getBusinessAccountStarBalance", params)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def transfer_business_account_stars(self, business_connection_id: str, star_amount: int) -> bool:
        """Transfer Telegram Stars from a business account."""
        params = {'business_connection_id': business_connection_id, 'star_amount': star_amount}
        response = self._make_request("transferBusinessAccountStars", params)
        return response.get('ok', False)
