"""
Test suite for Telegram media endpoints.

This module tests the TelegramMediaAPI class methods using mocked requests.
"""

import pytest
from unittest.mock import patch
from app.telegram.api.telegram_media import TelegramMediaAPI


class TestTelegramMediaAPI:
    """Test cases for TelegramMediaAPI methods."""

    @pytest.fixture
    def bot(self):
        """Create a TelegramMediaAPI instance for testing."""
        return TelegramMediaAPI("test_token")

    def test_send_sticker(self, bot):
        """Test send_sticker method."""
        mock_response = {
            'ok': True,
            'result': {
                'message_id': 1,
                'date': 123456789,
                'chat': {'id': 123, 'type': 'private'},
                'sticker': {'file_id': 'sticker_id'}
            }
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            message = bot.send_sticker(123, 'sticker_file_id')
            assert message.message_id == 1

    def test_send_animation(self, bot):
        """Test send_animation method."""
        mock_response = {
            'ok': True,
            'result': {
                'message_id': 1,
                'date': 123456789,
                'chat': {'id': 123, 'type': 'private'},
                'animation': {'file_id': 'animation_id'}
            }
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            message = bot.send_animation(123, 'animation_file_id')
            assert message.message_id == 1

    def test_send_voice(self, bot):
        """Test send_voice method."""
        mock_response = {
            'ok': True,
            'result': {
                'message_id': 1,
                'date': 123456789,
                'chat': {'id': 123, 'type': 'private'},
                'voice': {'file_id': 'voice_id'}
            }
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            message = bot.send_voice(123, 'voice_file_id')
            assert message.message_id == 1

    def test_send_video_note(self, bot):
        """Test send_video_note method."""
        mock_response = {
            'ok': True,
            'result': {
                'message_id': 1,
                'date': 123456789,
                'chat': {'id': 123, 'type': 'private'},
                'video_note': {'file_id': 'video_note_id'}
            }
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            message = bot.send_video_note(123, 'video_note_file_id')
            assert message.message_id == 1

    def test_send_location(self, bot):
        """Test send_location method."""
        mock_response = {
            'ok': True,
            'result': {
                'message_id': 1,
                'date': 123456789,
                'chat': {'id': 123, 'type': 'private'},
                'location': {'latitude': 40.7128, 'longitude': -74.0060}
            }
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            message = bot.send_location(123, 40.7128, -74.0060)
            assert message.message_id == 1

    def test_send_contact(self, bot):
        """Test send_contact method."""
        mock_response = {
            'ok': True,
            'result': {
                'message_id': 1,
                'date': 123456789,
                'chat': {'id': 123, 'type': 'private'},
                'contact': {'phone_number': '1234567890', 'first_name': 'John'}
            }
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            message = bot.send_contact(123, '1234567890', 'John')
            assert message.message_id == 1

    def test_send_poll(self, bot):
        """Test send_poll method."""
        mock_response = {
            'ok': True,
            'result': {
                'message_id': 1,
                'date': 123456789,
                'chat': {'id': 123, 'type': 'private'},
                'poll': {'id': 'poll_id', 'question': 'Test?', 'options': []}
            }
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            message = bot.send_poll(123, 'Test?', ['Option 1', 'Option 2'])
            assert message.message_id == 1

    def test_send_Group Mint(self, bot):
        """Test send_Group Mint method."""
        mock_response = {
            'ok': True,
            'result': {
                'message_id': 1,
                'date': 123456789,
                'chat': {'id': 123, 'type': 'private'},
                'Group Mint': {'emoji': '🎲', 'value': 6}
            }
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            message = bot.send_Group Mint(123)
            assert message.message_id == 1

    def test_send_venue(self, bot):
        """Test send_venue method."""
        mock_response = {
            'ok': True,
            'result': {
                'message_id': 1,
                'date': 123456789,
                'chat': {'id': 123, 'type': 'private'},
                'venue': {'location': {'latitude': 40.7128, 'longitude': -74.0060}, 'title': 'Test Venue', 'address': '123 Main St'}
            }
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            message = bot.send_venue(123, 40.7128, -74.0060, 'Test Venue', '123 Main St')
            assert message.message_id == 1
