"""
Additional Telegram Bot API media endpoints.

This module extends the TelegramBotAPI with media-related methods.
"""

from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass

# Import base classes from telegram_api.py
from .telegram_api import TelegramBotAPI, Message


class TelegramMediaAPI(TelegramBotAPI):
    """Extension for media-related endpoints."""

    def send_sticker(self, chat_id: Union[int, str], sticker: str, **kwargs) -> Message:
        """Send a sticker."""
        params = {'chat_id': chat_id, 'sticker': sticker, **kwargs}
        response = self._make_request("sendSticker", params)
        if response.get('ok'):
            return Message.from_dict(response['result'])
        raise Exception(response.get('description', 'Unknown error'))

    def send_animation(self, chat_id: Union[int, str], animation: str, **kwargs) -> Message:
        """Send an animation."""
        params = {'chat_id': chat_id, 'animation': animation, **kwargs}
        response = self._make_request("sendAnimation", params)
        if response.get('ok'):
            return Message.from_dict(response['result'])
        raise Exception(response.get('description', 'Unknown error'))

    def send_voice(self, chat_id: Union[int, str], voice: str, **kwargs) -> Message:
        """Send a voice message."""
        params = {'chat_id': chat_id, 'voice': voice, **kwargs}
        response = self._make_request("sendVoice", params)
        if response.get('ok'):
            return Message.from_dict(response['result'])
        raise Exception(response.get('description', 'Unknown error'))

    def send_video_note(self, chat_id: Union[int, str], video_note: str, **kwargs) -> Message:
        """Send a video note."""
        params = {'chat_id': chat_id, 'video_note': video_note, **kwargs}
        response = self._make_request("sendVideoNote", params)
        if response.get('ok'):
            return Message.from_dict(response['result'])
        raise Exception(response.get('description', 'Unknown error'))

    def send_location(self, chat_id: Union[int, str], latitude: float, longitude: float, **kwargs) -> Message:
        """Send a location."""
        params = {'chat_id': chat_id, 'latitude': latitude, 'longitude': longitude, **kwargs}
        response = self._make_request("sendLocation", params)
        if response.get('ok'):
            return Message.from_dict(response['result'])
        raise Exception(response.get('description', 'Unknown error'))

    def send_contact(self, chat_id: Union[int, str], phone_number: str, first_name: str, **kwargs) -> Message:
        """Send a contact."""
        params = {'chat_id': chat_id, 'phone_number': phone_number, 'first_name': first_name, **kwargs}
        response = self._make_request("sendContact", params)
        if response.get('ok'):
            return Message.from_dict(response['result'])
        raise Exception(response.get('description', 'Unknown error'))

    def send_poll(self, chat_id: Union[int, str], question: str, options: List[str], **kwargs) -> Message:
        """Send a poll."""
        params = {'chat_id': chat_id, 'question': question, 'options': options, **kwargs}
        response = self._make_request("sendPoll", params)
        if response.get('ok'):
            return Message.from_dict(response['result'])
        raise Exception(response.get('description', 'Unknown error'))

    def send_dice(self, chat_id: Union[int, str], **kwargs) -> Message:
        """Send a dice."""
        params = {'chat_id': chat_id, **kwargs}
        response = self._make_request("sendDice", params)
        if response.get('ok'):
            return Message.from_dict(response['result'])
        raise Exception(response.get('description', 'Unknown error'))

    def send_venue(self, chat_id: Union[int, str], latitude: float, longitude: float, title: str, address: str, **kwargs) -> Message:
        """Send a venue."""
        params = {'chat_id': chat_id, 'latitude': latitude, 'longitude': longitude, 'title': title, 'address': address, **kwargs}
        response = self._make_request("sendVenue", params)
        if response.get('ok'):
            return Message.from_dict(response['result'])
        raise Exception(response.get('description', 'Unknown error'))
