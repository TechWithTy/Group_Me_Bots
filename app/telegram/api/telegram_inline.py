"""
Additional Telegram Bot API inline and callback endpoints.

This module extends the TelegramBotAPI with inline query and callback methods.
"""

from typing import Optional, List, Dict, Any, Union

# Import base classes from telegram_api.py
from .telegram_api import TelegramBotAPI


class TelegramInlineAPI(TelegramBotAPI):
    """Extension for inline queries and callbacks."""

    def answer_inline_query(self, inline_query_id: str, results: List[Dict[str, Any]], **kwargs) -> bool:
        """Answer an inline query."""
        params = {'inline_query_id': inline_query_id, 'results': results, **kwargs}
        response = self._make_request("answerInlineQuery", params)
        return response.get('ok', False)

    def answer_callback_query(self, callback_query_id: str, **kwargs) -> bool:
        """Answer a callback query."""
        params = {'callback_query_id': callback_query_id, **kwargs}
        response = self._make_request("answerCallbackQuery", params)
        return response.get('ok', False)

    def edit_message_reply_markup(self, **kwargs) -> Optional[Message]:
        """Edit the reply markup of a message."""
        response = self._make_request("editMessageReplyMarkup", kwargs)
        if response.get('ok'):
            return Message.from_dict(response['result']) if response['result'] else None
        raise Exception(response.get('description', 'Unknown error'))

    def edit_message_caption(self, **kwargs) -> Optional[Message]:
        """Edit the caption of a message."""
        response = self._make_request("editMessageCaption", kwargs)
        if response.get('ok'):
            return Message.from_dict(response['result']) if response['result'] else None
        raise Exception(response.get('description', 'Unknown error'))

    def edit_message_media(self, media: Dict[str, Any], **kwargs) -> Optional[Message]:
        """Edit the media of a message."""
        params = {'media': media, **kwargs}
        response = self._make_request("editMessageMedia", params)
        if response.get('ok'):
            return Message.from_dict(response['result']) if response['result'] else None
        raise Exception(response.get('description', 'Unknown error'))

    def delete_message_from_chat(self, chat_id: Union[int, str], message_id: int) -> bool:
        """Delete a message from a chat."""
        params = {'chat_id': chat_id, 'message_id': message_id}
        response = self._make_request("deleteMessage", params)
        return response.get('ok', False)

    def send_game(self, chat_id: Union[int, str], game_short_name: str, **kwargs) -> Message:
        """Send a game."""
        params = {'chat_id': chat_id, 'game_short_name': game_short_name, **kwargs}
        response = self._make_request("sendGame", params)
        if response.get('ok'):
            return Message.from_dict(response['result'])
        raise Exception(response.get('description', 'Unknown error'))

    def set_game_score(self, user_id: int, score: int, **kwargs) -> Optional[Dict[str, Any]]:
        """Set the score of a game."""
        params = {'user_id': user_id, 'score': score, **kwargs}
        response = self._make_request("setGameScore", params)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def get_game_high_scores(self, user_id: int, **kwargs) -> List[Dict[str, Any]]:
        """Get high scores for a game."""
        params = {'user_id': user_id, **kwargs}
        response = self._make_request("getGameHighScores", params)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))
