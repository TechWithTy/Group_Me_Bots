"""
Test suite for Telegram chat management endpoints.

This module tests the TelegramChatAPI class methods using mocked requests.
"""

import pytest
from unittest.mock import patch
from app.telegram.api.telegram_chat import TelegramChatAPI


class TestTelegramChatAPI:
    """Test cases for TelegramChatAPI methods."""

    @pytest.fixture
    def bot(self):
        """Create a TelegramChatAPI instance for testing."""
        return TelegramChatAPI("test_token")

    def test_set_chat_title(self, bot):
        """Test set_chat_title method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.set_chat_title(123, 'New Title')
            assert result is True

    def test_set_chat_description(self, bot):
        """Test set_chat_description method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.set_chat_description(123, 'New Description')
            assert result is True

    def test_pin_chat_message(self, bot):
        """Test pin_chat_message method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.pin_chat_message(123, 1)
            assert result is True

    def test_unpin_chat_message(self, bot):
        """Test unpin_chat_message method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.unpin_chat_message(123)
            assert result is True

    def test_leave_chat(self, bot):
        """Test leave_chat method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.leave_chat(123)
            assert result is True

    def test_get_chat_administrators(self, bot):
        """Test get_chat_administrators method."""
        mock_response = {
            'ok': True,
            'result': [
                {'user': {'id': 123, 'is_bot': False, 'first_name': 'Admin'}, 'status': 'administrator'}
            ]
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            admins = bot.get_chat_administrators(123)
            assert len(admins) == 1
            assert admins[0]['status'] == 'administrator'

    def test_get_chat_member_count(self, bot):
        """Test get_chat_member_count method."""
        mock_response = {'ok': True, 'result': 100}
        with patch.object(bot, '_make_request', return_value=mock_response):
            count = bot.get_chat_member_count(123)
            assert count == 100

    def test_get_chat_member(self, bot):
        """Test get_chat_member method."""
        mock_response = {
            'ok': True,
            'result': {'user': {'id': 456, 'is_bot': False, 'first_name': 'Member'}, 'status': 'member'}
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            member = bot.get_chat_member(123, 456)
            assert member['status'] == 'member'

    def test_set_chat_sticker_set(self, bot):
        """Test set_chat_sticker_set method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.set_chat_sticker_set(123, 'sticker_set_name')
            assert result is True

    def test_delete_chat_sticker_set(self, bot):
        """Test delete_chat_sticker_set method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.delete_chat_sticker_set(123)
            assert result is True

    def test_export_chat_invite_link(self, bot):
        """Test export_chat_invite_link method."""
        mock_response = {'ok': True, 'result': 'https://t.me/joinchat/...' }
        with patch.object(bot, '_make_request', return_value=mock_response):
            link = bot.export_chat_invite_link(123)
            assert link.startswith('https://')

    def test_create_chat_invite_link(self, bot):
        """Test create_chat_invite_link method."""
        mock_response = {
            'ok': True,
            'result': {'invite_link': 'https://t.me/joinchat/...', 'creator': {'id': 123}}
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            link = bot.create_chat_invite_link(123)
            assert 'invite_link' in link

    def test_edit_chat_invite_link(self, bot):
        """Test edit_chat_invite_link method."""
        mock_response = {
            'ok': True,
            'result': {'invite_link': 'https://t.me/joinchat/...', 'creator': {'id': 123}}
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            link = bot.edit_chat_invite_link(123, 'https://t.me/joinchat/...')
            assert 'invite_link' in link

    def test_revoke_chat_invite_link(self, bot):
        """Test revoke_chat_invite_link method."""
        mock_response = {
            'ok': True,
            'result': {'invite_link': 'https://t.me/joinchat/...', 'creator': {'id': 123}}
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            link = bot.revoke_chat_invite_link(123, 'https://t.me/joinchat/...')
            assert 'invite_link' in link
