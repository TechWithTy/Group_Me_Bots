"""
Test suite for Telegram payments endpoints.

This module tests the TelegramPaymentsAPI class methods using mocked requests.
"""

import pytest
from unittest.mock import patch
from app.telegram.api.telegram_payments import TelegramPaymentsAPI


class TestTelegramPaymentsAPI:
    """Test cases for TelegramPaymentsAPI methods."""

    @pytest.fixture
    def bot(self):
        """Create a TelegramPaymentsAPI instance for testing."""
        return TelegramPaymentsAPI("test_token")

    def test_send_invoice(self, bot):
        """Test send_invoice method."""
        mock_response = {
            'ok': True,
            'result': {
                'message_id': 1,
                'date': 123456789,
                'chat': {'id': 123, 'type': 'private'},
                'invoice': {'title': 'Test Invoice'}
            }
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            message = bot.send_invoice(123, 'Test', 'Description', 'payload', 'token', 'USD', [{'label': 'Item', 'amount': 100}])
            assert message.message_id == 1

    def test_answer_shipping_query(self, bot):
        """Test answer_shipping_query method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.answer_shipping_query('shipping_id', True, shipping_options=[{'id': '1', 'title': 'Option'}])
            assert result is True

    def test_answer_pre_checkout_query(self, bot):
        """Test answer_pre_checkout_query method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.answer_pre_checkout_query('pre_checkout_id', True)
            assert result is True

    def test_create_invoice_link(self, bot):
        """Test create_invoice_link method."""
        mock_response = {'ok': True, 'result': 'https://t.me/invoice/...' }
        with patch.object(bot, '_make_request', return_value=mock_response):
            link = bot.create_invoice_link('Test', 'Description', 'payload', 'token', 'USD', [{'label': 'Item', 'amount': 100}])
            assert link.startswith('https://')

    def test_get_star_transactions(self, bot):
        """Test get_star_transactions method."""
        mock_response = {
            'ok': True,
            'result': [
                {'id': 'tx1', 'amount': 100, 'date': 123456789}
            ]
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            transactions = bot.get_star_transactions()
            assert len(transactions) == 1

    def test_refund_star_payment(self, bot):
        """Test refund_star_payment method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.refund_star_payment(123, 'charge_id')
            assert result is True

    def test_edit_user_star_subscription(self, bot):
        """Test edit_user_star_subscription method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.edit_user_star_subscription(123, 'charge_id', True)
            assert result is True

    def test_set_chat_photo(self, bot):
        """Test set_chat_photo method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.set_chat_photo(123, 'photo_file_id')
            assert result is True

    def test_delete_chat_photo(self, bot):
        """Test delete_chat_photo method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.delete_chat_photo(123)
            assert result is True
