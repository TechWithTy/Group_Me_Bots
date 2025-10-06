"""
Test suite for Telegram business endpoints.

This module tests the TelegramBusinessAPI class methods using mocked requests.
"""

import pytest
from unittest.mock import patch
from app.telegram.api.telegram_business import TelegramBusinessAPI


class TestTelegramBusinessAPI:
    """Test cases for TelegramBusinessAPI methods."""

    @pytest.fixture
    def bot(self):
        """Create a TelegramBusinessAPI instance for testing."""
        return TelegramBusinessAPI("test_token")

    def test_get_business_account_info(self, bot):
        """Test get_business_account_info method."""
        mock_response = {
            'ok': True,
            'result': {'id': 'business_id', 'name': 'Business Name'}
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            info = bot.get_business_account_info(business_connection_id='conn_id')
            assert info['id'] == 'business_id'

    def test_read_business_message(self, bot):
        """Test read_business_message method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.read_business_message('conn_id', 1)
            assert result is True

    def test_delete_business_messages(self, bot):
        """Test delete_business_messages method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.delete_business_messages('conn_id', [1, 2])
            assert result is True

    def test_set_business_account_name(self, bot):
        """Test set_business_account_name method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.set_business_account_name('conn_id', 'John', 'Doe')
            assert result is True

    def test_set_business_account_username(self, bot):
        """Test set_business_account_username method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.set_business_account_username('conn_id', 'username')
            assert result is True

    def test_set_business_account_bio(self, bot):
        """Test set_business_account_bio method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.set_business_account_bio('conn_id', 'New bio')
            assert result is True

    def test_set_business_account_profile_photo(self, bot):
        """Test set_business_account_profile_photo method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.set_business_account_profile_photo('conn_id', 'photo_id')
            assert result is True

    def test_remove_business_account_profile_photo(self, bot):
        """Test remove_business_account_profile_photo method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.remove_business_account_profile_photo('conn_id')
            assert result is True

    def test_set_business_account_gift_settings(self, bot):
        """Test set_business_account_gift_settings method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.set_business_account_gift_settings('conn_id', True)
            assert result is True

    def test_get_business_account_gifts(self, bot):
        """Test get_business_account_gifts method."""
        mock_response = {
            'ok': True,
            'result': [
                {'id': 'gift1', 'type': 'regular'}
            ]
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            gifts = bot.get_business_account_gifts('conn_id')
            assert len(gifts) == 1

    def test_post_story(self, bot):
        """Test post_story method."""
        mock_response = {
            'ok': True,
            'result': {'story_id': 1, 'date': 123456789}
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            story = bot.post_story('conn_id', {'type': 'photo', 'media': 'file_id'})
            assert story['story_id'] == 1

    def test_edit_story(self, bot):
        """Test edit_story method."""
        mock_response = {
            'ok': True,
            'result': {'story_id': 1, 'date': 123456789}
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            story = bot.edit_story('conn_id', 1, {'type': 'photo', 'media': 'new_file_id'})
            assert story['story_id'] == 1

    def test_delete_story(self, bot):
        """Test delete_story method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.delete_story('conn_id', 1)
            assert result is True

    def test_hide_keyboard(self, bot):
        """Test hide_keyboard method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.hide_keyboard()
            assert result is True
