"""
Test suite for Telegram miscellaneous endpoints.

This module tests the TelegramMiscAPI class methods using mocked requests.
"""

import pytest
from unittest.mock import patch
from app.telegram.api.telegram_misc import TelegramMiscAPI


class TestTelegramMiscAPI:
    """Test cases for TelegramMiscAPI methods."""

    @pytest.fixture
    def bot(self):
        """Create a TelegramMiscAPI instance for testing."""
        return TelegramMiscAPI("test_token")

    def test_set_my_commands(self, bot):
        """Test set_my_commands method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.set_my_commands([{'command': 'start', 'description': 'Start bot'}])
            assert result is True

    def test_get_my_commands(self, bot):
        """Test get_my_commands method."""
        mock_response = {
            'ok': True,
            'result': [
                {'command': 'start', 'description': 'Start bot'}
            ]
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            commands = bot.get_my_commands()
            assert len(commands) == 1

    def test_set_my_name(self, bot):
        """Test set_my_name method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.set_my_name('Test Bot')
            assert result is True

    def test_get_my_name(self, bot):
        """Test get_my_name method."""
        mock_response = {
            'ok': True,
            'result': {'name': 'Test Bot'}
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            name = bot.get_my_name()
            assert name['name'] == 'Test Bot'

    def test_set_my_description(self, bot):
        """Test set_my_description method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.set_my_description('Test description')
            assert result is True

    def test_get_my_description(self, bot):
        """Test get_my_description method."""
        mock_response = {
            'ok': True,
            'result': {'description': 'Test description'}
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            desc = bot.get_my_description()
            assert desc['description'] == 'Test description'

    def test_set_my_short_description(self, bot):
        """Test set_my_short_description method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.set_my_short_description('Short desc')
            assert result is True

    def test_get_my_short_description(self, bot):
        """Test get_my_short_description method."""
        mock_response = {
            'ok': True,
            'result': {'short_description': 'Short desc'}
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            desc = bot.get_my_short_description()
            assert desc['short_description'] == 'Short desc'

    def test_set_chat_menu_button(self, bot):
        """Test set_chat_menu_button method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.set_chat_menu_button(123, {'type': 'web_app', 'text': 'App', 'web_app': {'url': 'https://example.com'}})
            assert result is True

    def test_get_chat_menu_button(self, bot):
        """Test get_chat_menu_button method."""
        mock_response = {
            'ok': True,
            'result': {'type': 'web_app', 'text': 'App'}
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            button = bot.get_chat_menu_button(123)
            assert button['type'] == 'web_app'

    def test_set_my_default_administrator_rights(self, bot):
        """Test set_my_default_administrator_rights method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.set_my_default_administrator_rights({'is_anonymous': False, 'can_manage_chat': True})
            assert result is True

    def test_get_my_default_administrator_rights(self, bot):
        """Test get_my_default_administrator_rights method."""
        mock_response = {
            'ok': True,
            'result': {'is_anonymous': False, 'can_manage_chat': True}
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            rights = bot.get_my_default_administrator_rights()
            assert rights['can_manage_chat'] is True

    def test_delete_my_commands(self, bot):
        """Test delete_my_commands method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.delete_my_commands()
            assert result is True

    def test_log_out(self, bot):
        """Test log_out method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.log_out()
            assert result is True

    def test_close(self, bot):
        """Test close method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.close()
            assert result is True

    def test_get_webhook_info(self, bot):
        """Test get_webhook_info method."""
        mock_response = {
            'ok': True,
            'result': {'url': 'https://example.com', 'has_custom_certificate': False}
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            info = bot.get_webhook_info()
            assert info['url'] == 'https://example.com'

    def test_get_me(self, bot):
        """Test get_me method."""
        mock_response = {
            'ok': True,
            'result': {'id': 123, 'is_bot': True, 'first_name': 'Test Bot'}
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            info = bot.get_me()
            assert info['id'] == 123

    def test_get_updates(self, bot):
        """Test get_updates method."""
        mock_response = {
            'ok': True,
            'result': [
                {'update_id': 1, 'message': {'message_id': 1}}
            ]
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            updates = bot.get_updates()
            assert len(updates) == 1

    def test_send_message(self, bot):
        """Test send_message method."""
        mock_response = {
            'ok': True,
            'result': {'message_id': 1, 'text': 'Hello'}
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.send_message(123, 'Hello')
            assert result['message_id'] == 1
