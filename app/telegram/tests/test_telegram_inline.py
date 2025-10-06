"""
Test suite for Telegram inline and callback endpoints.

This module tests the TelegramInlineAPI class methods using mocked requests.
"""

import pytest
from unittest.mock import patch
from app.telegram.api.telegram_inline import TelegramInlineAPI


class TestTelegramInlineAPI:
    """Test cases for TelegramInlineAPI methods."""

    @pytest.fixture
    def bot(self):
        """Create a TelegramInlineAPI instance for testing."""
        return TelegramInlineAPI("test_token")

    def test_answer_inline_query(self, bot):
        """Test answer_inline_query method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.answer_inline_query('query_id', [{'type': 'article', 'id': '1', 'title': 'Test'}])
            assert result is True

    def test_answer_callback_query(self, bot):
        """Test answer_callback_query method."""
        mock_response = {'ok': True}
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.answer_callback_query('callback_id', text='Response')
            assert result is True

    def test_edit_message_reply_markup(self, bot):
        """Test edit_message_reply_markup method."""
        mock_response = {
            'ok': True,
            'result': {
                'message_id': 1,
                'date': 123456789,
                'chat': {'id': 123, 'type': 'private'},
                'text': 'Updated'
            }
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            message = bot.edit_message_reply_markup(chat_id=123, message_id=1)
            assert message.message_id == 1

    def test_edit_message_caption(self, bot):
        """Test edit_message_caption method."""
        mock_response = {
            'ok': True,
            'result': {
                'message_id': 1,
                'date': 123456789,
                'chat': {'id': 123, 'type': 'private'},
                'caption': 'New Caption'
            }
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            message = bot.edit_message_caption(chat_id=123, message_id=1, caption='New Caption')
            assert message.caption == 'New Caption'

    def test_edit_message_media(self, bot):
        """Test edit_message_media method."""
        mock_response = {
            'ok': True,
            'result': {
                'message_id': 1,
                'date': 123456789,
                'chat': {'id': 123, 'type': 'private'},
                'photo': [{'file_id': 'new_photo_id'}]
            }
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            message = bot.edit_message_media({'type': 'photo', 'media': 'new_file_id'}, chat_id=123, message_id=1)
            assert message.message_id == 1

    def test_send_game(self, bot):
        """Test send_game method."""
        mock_response = {
            'ok': True,
            'result': {
                'message_id': 1,
                'date': 123456789,
                'chat': {'id': 123, 'type': 'private'},
                'game': {'title': 'Test Game'}
            }
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            message = bot.send_game(123, 'test_game')
            assert message.message_id == 1

    def test_set_game_score(self, bot):
        """Test set_game_score method."""
        mock_response = {
            'ok': True,
            'result': {
                'user': {'id': 456, 'first_name': 'Player'},
                'score': 100
            }
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            result = bot.set_game_score(456, 100, chat_id=123, message_id=1)
            assert result['score'] == 100

    def test_get_game_high_scores(self, bot):
        """Test get_game_high_scores method."""
        mock_response = {
            'ok': True,
            'result': [
                {'user': {'id': 456, 'first_name': 'Player'}, 'score': 100}
            ]
        }
        with patch.object(bot, '_make_request', return_value=mock_response):
            scores = bot.get_game_high_scores(456, chat_id=123, message_id=1)
            assert len(scores) == 1
            assert scores[0]['score'] == 100
