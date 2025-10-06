"""
Test suite for core Telegram Bot API endpoints.

This module tests the TelegramBotAPI class methods using mocked requests.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.telegram.api.telegram_api import TelegramBotAPI, User, Chat, Message, Update


class TestTelegramBotAPI:
    """Test cases for TelegramBotAPI core methods."""

    @pytest.fixture
    def bot(self):
        """Create a TelegramBotAPI instance for testing."""
        return TelegramBotAPI("test_token")

    def test_get_me(self, bot):
        """Test get_me method."""
        mock_response = {'ok': True, 'result': {'id': 123, 'is_bot': True, 'first_name': 'Test Bot'}}
        with patch.object(bot, '_make_request', return_value=mock_response):
            user = bot.get_me()
            assert user.id == 123
            assert user.is_bot is True
            assert user.first_name == 'Test Bot'

    def test_send_message(self, bot):
        """Test send_message method."""
        mock_response = {
            'ok': True,
            'result': {
                'message_id': 1,
                'date': 123456789,
                'chat': {'id': 123, 'type': 'private'},
                'text': 'Hello'
            }
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            message = bot.send_message(123, 'Hello')
            assert message.message_id == 1
            assert message.text == 'Hello'

    def test_get_updates(self, bot):
        """Test get_updates method."""
        mock_response = {
            'ok': True,
            'result': [
                {
                    'update_id': 1,
                    'message': {
                        'message_id': 1,
                        'date': 123456789,
                        'chat': {'id': 123, 'type': 'private'},
                        'text': 'Test'
                    }
                }
            ]
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            updates = bot.get_updates()
            assert len(updates) == 1
            assert updates[0].update_id == 1

    def test_set_webhook(self, bot):
        """Test set_webhook method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.set_webhook("https://example.com/webhook")
            assert result is True

    def test_delete_webhook(self, bot):
        """Test delete_webhook method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.delete_webhook()
            assert result is True

    def test_edit_message_text(self, bot):
        """Test edit_message_text method."""
        mock_response = {
            'ok': True,
            'result': {
                'message_id': 1,
                'date': 123456789,
                'chat': {'id': 123, 'type': 'private'},
                'text': 'Updated text'
            }
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            message = bot.edit_message_text("Updated text", chat_id=123, message_id=1)
            assert message.text == 'Updated text'

    def test_delete_message(self, bot):
        """Test delete_message method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.delete_message(123, 1)
            assert result is True

    def test_send_photo(self, bot):
        """Test send_photo method."""
        mock_response = {
            'ok': True,
            'result': {
                'message_id': 1,
                'date': 123456789,
                'chat': {'id': 123, 'type': 'private'},
                'photo': [{'file_id': 'photo_id'}]
            }
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            message = bot.send_photo(123, 'photo_file_id')
            assert message.message_id == 1

    def test_get_chat(self, bot):
        """Test get_chat method."""
        mock_response = {
            'ok': True,
            'result': {'id': 123, 'type': 'private', 'first_name': 'John'}
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            chat = bot.get_chat(123)
            assert chat.id == 123
            assert chat.type == 'private'

    def test_ban_chat_member(self, bot):
        """Test ban_chat_member method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.ban_chat_member(123, 456)
            assert result is True

    def test_get_file(self, bot):
        """Test get_file method."""
        mock_response = {
            'ok': True,
            'result': {'file_id': 'file_id', 'file_path': 'path/to/file'}
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            file_info = bot.get_file('file_id')
            assert file_info['file_id'] == 'file_id'

    def test_send_media_group(self, bot):
        """Test send_media_group method."""
        mock_response = {
            'ok': True,
            'result': [
                {
                    'message_id': 1,
                    'date': 123456789,
                    'chat': {'id': 123, 'type': 'private'}
                }
            ]
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            messages = bot.send_media_group(123, [{'type': 'photo', 'media': 'file_id'}])
            assert len(messages) == 1
            assert messages[0].message_id == 1
