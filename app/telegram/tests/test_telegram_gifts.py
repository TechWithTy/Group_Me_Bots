"""
Test suite for Telegram gifts endpoints.

This module tests the TelegramGiftsAPI class methods using mocked requests.
"""

import pytest
from unittest.mock import patch
from app.telegram.api.telegram_gifts import TelegramGiftsAPI


class TestTelegramGiftsAPI:
    """Test cases for TelegramGiftsAPI methods."""

    @pytest.fixture
    def bot(self):
        """Create a TelegramGiftsAPI instance for testing."""
        return TelegramGiftsAPI("test_token")

    def test_send_gift(self, bot):
        """Test send_gift method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.send_gift(123, 'gift_id')
            assert result is True

    def test_verify_gift(self, bot):
        """Test verify_gift method."""
        mock_response = {
            'ok': True,
            'result': {'id': 'gift_id', 'type': 'regular', 'is_valid': True}
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            gift = bot.verify_gift('gift_id')
            assert gift['is_valid'] is True

    def test_get_available_gifts(self, bot):
        """Test get_available_gifts method."""
        mock_response = {
            'ok': True,
            'result': [
                {'id': 'gift1', 'price': 100, 'star_count': 10}
            ]
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            gifts = bot.get_available_gifts()
            assert len(gifts) == 1

    def test_get_user_gifts(self, bot):
        """Test get_user_gifts method."""
        mock_response = {
            'ok': True,
            'result': [
                {'id': 'gift1', 'type': 'regular', 'owner': {'id': 123}}
            ]
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            gifts = bot.get_user_gifts(123)
            assert len(gifts) == 1

    def test_convert_gift_to_stars(self, bot):
        """Test convert_gift_to_stars method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.convert_gift_to_stars('gift_id')
            assert result is True

    def test_upgrade_gift(self, bot):
        """Test upgrade_gift method."""
        mock_response = {
            'ok': True,
            'result': {'id': 'gift1', 'type': 'unique', 'upgraded': True}
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            gift = bot.upgrade_gift('gift_id')
            assert gift['type'] == 'unique'

    def test_transfer_gift(self, bot):
        """Test transfer_gift method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.transfer_gift('gift_id', 456)
            assert result is True

    def test_get_gift_info(self, bot):
        """Test get_gift_info method."""
        mock_response = {
            'ok': True,
            'result': {'id': 'gift1', 'type': 'regular', 'price': 100}
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            gift = bot.get_gift_info('gift_id')
            assert gift['id'] == 'gift1'

    def test_get_gift_upgrade_preview(self, bot):
        """Test get_gift_upgrade_preview method."""
        mock_response = {
            'ok': True,
            'result': {'id': 'gift1', 'preview': 'unique_preview'}
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            preview = bot.get_gift_upgrade_preview('gift_id')
            assert 'preview' in preview

    def test_gift_premium_subscription(self, bot):
        """Test gift_premium_subscription method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.gift_premium_subscription(123, 3)
            assert result is True

    def test_get_my_star_balance(self, bot):
        """Test get_my_star_balance method."""
        mock_response = {
            'ok': True,
            'result': {'balance': 1000}
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            balance = bot.get_my_star_balance()
            assert balance['balance'] == 1000

    def test_get_business_account_star_balance(self, bot):
        """Test get_business_account_star_balance method."""
        mock_response = {
            'ok': True,
            'result': {'balance': 500}
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            balance = bot.get_business_account_star_balance('conn_id')
            assert balance['balance'] == 500

    def test_transfer_business_account_stars(self, bot):
        """Test transfer_business_account_stars method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.transfer_business_account_stars('conn_id', 100)
            assert result is True
