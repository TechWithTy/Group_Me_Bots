"""
Additional Telegram Bot API payment endpoints.

This module extends the TelegramBotAPI with payment-related methods.
"""

from typing import Optional, List, Dict, Any, Union

# Import base classes from telegram_api.py
from .telegram_api import TelegramBotAPI, Message


class TelegramPaymentsAPI(TelegramBotAPI):
    """Extension for payment endpoints."""

    def send_invoice(self, chat_id: Union[int, str], title: str, description: str, payload: str, provider_token: str, currency: str, prices: List[Dict[str, Any]], **kwargs) -> Message:
        """Send an invoice."""
        params = {
            'chat_id': chat_id,
            'title': title,
            'description': description,
            'payload': payload,
            'provider_token': provider_token,
            'currency': currency,
            'prices': prices,
            **kwargs
        }
        response = self._make_request("sendInvoice", params)
        if response.get('ok'):
            return Message.from_dict(response['result'])
        raise Exception(response.get('description', 'Unknown error'))

    def answer_shipping_query(self, shipping_query_id: str, ok: bool, **kwargs) -> bool:
        """Answer a shipping query."""
        params = {'shipping_query_id': shipping_query_id, 'ok': ok, **kwargs}
        response = self._make_request("answerShippingQuery", params)
        return response.get('ok', False)

    def answer_pre_checkout_query(self, pre_checkout_query_id: str, ok: bool, **kwargs) -> bool:
        """Answer a pre-checkout query."""
        params = {'pre_checkout_query_id': pre_checkout_query_id, 'ok': ok, **kwargs}
        response = self._make_request("answerPreCheckoutQuery", params)
        return response.get('ok', False)

    def create_invoice_link(self, title: str, description: str, payload: str, provider_token: str, currency: str, prices: List[Dict[str, Any]], **kwargs) -> str:
        """Create an invoice link."""
        params = {
            'title': title,
            'description': description,
            'payload': payload,
            'provider_token': provider_token,
            'currency': currency,
            'prices': prices,
            **kwargs
        }
        response = self._make_request("createInvoiceLink", params)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def get_star_transactions(self, **kwargs) -> List[Dict[str, Any]]:
        """Get Telegram Star transactions."""
        response = self._make_request("getStarTransactions", kwargs)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def refund_star_payment(self, user_id: int, telegram_payment_charge_id: str) -> bool:
        """Refund a Telegram Star payment."""
        params = {'user_id': user_id, 'telegram_payment_charge_id': telegram_payment_charge_id}
        response = self._make_request("refundStarPayment", params)
        return response.get('ok', False)

    def edit_user_star_subscription(self, user_id: int, telegram_payment_charge_id: str, is_canceled: bool) -> bool:
        """Edit a user's Telegram Star subscription."""
        params = {'user_id': user_id, 'telegram_payment_charge_id': telegram_payment_charge_id, 'is_canceled': is_canceled}
        response = self._make_request("editUserStarSubscription", params)
        return response.get('ok', False)

    def set_chat_photo(self, chat_id: Union[int, str], photo: str) -> bool:
        """Set a chat photo."""
        params = {'chat_id': chat_id, 'photo': photo}
        response = self._make_request("setChatPhoto", params)
        return response.get('ok', False)

    def delete_chat_photo(self, chat_id: Union[int, str]) -> bool:
        """Delete a chat photo."""
        params = {'chat_id': chat_id}
        response = self._make_request("deleteChatPhoto", params)
        return response.get('ok', False)
