"""
Telegram Bot API implementation for Group_Me_Bots.

This module provides Python classes and methods to interact with the Telegram Bot API.
Based on the official Telegram Bot API documentation.
"""

import json
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass, field
from enum import Enum


class ChatType(Enum):
    PRIVATE = "private"
    GROUP = "group"
    SUPERGROUP = "supergroup"
    CHANNEL = "channel"


class MessageEntityType(Enum):
    MENTION = "mention"
    HASHTAG = "hashtag"
    CASHTAG = "cashtag"
    BOT_COMMAND = "bot_command"
    URL = "url"
    EMAIL = "email"
    PHONE_NUMBER = "phone_number"
    BOLD = "bold"
    ITALIC = "italic"
    UNDERLINE = "underline"
    STRIKETHROUGH = "strikethrough"
    SPOILER = "spoiler"
    BLOCKQUOTE = "blockquote"
    EXPANDABLE_BLOCKQUOTE = "expandable_blockquote"
    CODE = "code"
    PRE = "pre"
    TEXT_LINK = "text_link"
    TEXT_MENTION = "text_mention"
    CUSTOM_EMOJI = "custom_emoji"


@dataclass
class User:
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = None
    added_to_attachment_menu: Optional[bool] = None
    can_join_groups: Optional[bool] = None
    can_read_all_group_messages: Optional[bool] = None
    supports_inline_queries: Optional[bool] = None
    can_connect_to_business: Optional[bool] = None
    has_main_web_app: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        return cls(**data)


@dataclass
class Chat:
    id: int
    type: str
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_forum: Optional[bool] = None
    is_direct_messages: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Chat':
        return cls(**data)


@dataclass
class MessageEntity:
    type: str
    offset: int
    length: int
    url: Optional[str] = None
    user: Optional[User] = None
    language: Optional[str] = None
    custom_emoji_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MessageEntity':
        return cls(**data)


@dataclass
class Message:
    message_id: int
    date: int
    chat: Chat
    from_user: Optional[User] = None
    sender_chat: Optional[Chat] = None
    text: Optional[str] = None
    entities: Optional[List[MessageEntity]] = None
    reply_to_message: Optional['Message'] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        # Handle nested objects
        if 'from' in data:
            data['from_user'] = User.from_dict(data.pop('from'))
        if 'chat' in data:
            data['chat'] = Chat.from_dict(data['chat'])
        if 'entities' in data:
            data['entities'] = [MessageEntity.from_dict(e) for e in data['entities']]
        if 'reply_to_message' in data:
            data['reply_to_message'] = cls.from_dict(data['reply_to_message'])
        return cls(**data)


@dataclass
class Update:
    update_id: int
    message: Optional[Message] = None
    edited_message: Optional[Message] = None
    channel_post: Optional[Message] = None
    edited_channel_post: Optional[Message] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Update':
        # Handle message types
        for key in ['message', 'edited_message', 'channel_post', 'edited_channel_post']:
            if key in data and data[key]:
                data[key] = Message.from_dict(data[key])
        return cls(**data)


@dataclass
class TelegramAPIResponse:
    ok: bool
    result: Any = None
    description: Optional[str] = None
    error_code: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TelegramAPIResponse':
        return cls(**data)


class TelegramBotAPI:
    """
    Client for interacting with the Telegram Bot API.
    """

    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}/"

    def _make_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        import requests
        url = f"{self.base_url}{method}"
        response = requests.post(url, json=params) if params else requests.get(url)
        return response.json()

    def get_me(self) -> User:
        """Get basic information about the bot."""
        response = self._make_request("getMe")
        if response.get('ok'):
            return User.from_dict(response['result'])
        raise Exception(response.get('description', 'Unknown error'))

    def send_message(self, chat_id: Union[int, str], text: str, **kwargs) -> Message:
        """Send a text message."""
        params = {'chat_id': chat_id, 'text': text, **kwargs}
        response = self._make_request("sendMessage", params)
        if response.get('ok'):
            return Message.from_dict(response['result'])
        raise Exception(response.get('description', 'Unknown error'))

    def get_updates(self, offset: Optional[int] = None, limit: int = 100, timeout: int = 0) -> List[Update]:
        """Get updates using long polling."""
        params = {'offset': offset, 'limit': limit, 'timeout': timeout}
        response = self._make_request("getUpdates", params)
        if response.get('ok'):
            return [Update.from_dict(update) for update in response['result']]
        raise Exception(response.get('description', 'Unknown error'))

    def set_webhook(self, url: str, **kwargs) -> bool:
        """Set a webhook URL."""
        params = {'url': url, **kwargs}
        response = self._make_request("setWebhook", params)
        return response.get('ok', False)

    def delete_webhook(self, **kwargs) -> bool:
        """Remove webhook integration."""
        response = self._make_request("deleteWebhook", kwargs)
        return response.get('ok', False)

    def edit_message_text(self, text: str, **kwargs) -> Optional[Message]:
        """Edit text of a message."""
        params = {'text': text, **kwargs}
        response = self._make_request("editMessageText", params)
        if response.get('ok'):
            return Message.from_dict(response['result']) if response['result'] else None
        raise Exception(response.get('description', 'Unknown error'))

    def delete_message(self, chat_id: Union[int, str], message_id: int) -> bool:
        """Delete a message."""
        params = {'chat_id': chat_id, 'message_id': message_id}
        response = self._make_request("deleteMessage", params)
        return response.get('ok', False)

    def send_photo(self, chat_id: Union[int, str], photo: str, **kwargs) -> Message:
        """Send a photo."""
        params = {'chat_id': chat_id, 'photo': photo, **kwargs}
        response = self._make_request("sendPhoto", params)
        if response.get('ok'):
            return Message.from_dict(response['result'])
        raise Exception(response.get('description', 'Unknown error'))

    def send_video(self, chat_id: Union[int, str], video: str, **kwargs) -> Message:
        """Send a video."""
        params = {'chat_id': chat_id, 'video': video, **kwargs}
        response = self._make_request("sendVideo", params)
        if response.get('ok'):
            return Message.from_dict(response['result'])
        raise Exception(response.get('description', 'Unknown error'))

    def send_audio(self, chat_id: Union[int, str], audio: str, **kwargs) -> Message:
        """Send an audio file."""
        params = {'chat_id': chat_id, 'audio': audio, **kwargs}
        response = self._make_request("sendAudio", params)
        if response.get('ok'):
            return Message.from_dict(response['result'])
        raise Exception(response.get('description', 'Unknown error'))

    def send_document(self, chat_id: Union[int, str], document: str, **kwargs) -> Message:
        """Send a document."""
        params = {'chat_id': chat_id, 'document': document, **kwargs}
        response = self._make_request("sendDocument", params)
        if response.get('ok'):
            return Message.from_dict(response['result'])
        raise Exception(response.get('description', 'Unknown error'))

    def get_chat(self, chat_id: Union[int, str]) -> Chat:
        """Get information about a chat."""
        params = {'chat_id': chat_id}
        response = self._make_request("getChat", params)
        if response.get('ok'):
            return Chat.from_dict(response['result'])
        raise Exception(response.get('description', 'Unknown error'))

    def ban_chat_member(self, chat_id: Union[int, str], user_id: int, **kwargs) -> bool:
        """Ban a user from a chat."""
        params = {'chat_id': chat_id, 'user_id': user_id, **kwargs}
        response = self._make_request("banChatMember", params)
        return response.get('ok', False)

    def unban_chat_member(self, chat_id: Union[int, str], user_id: int, **kwargs) -> bool:
        """Unban a user from a chat."""
        params = {'chat_id': chat_id, 'user_id': user_id, **kwargs}
        response = self._make_request("unbanChatMember", params)
        return response.get('ok', False)

    def promote_chat_member(self, chat_id: Union[int, str], user_id: int, **kwargs) -> bool:
        """Promote a chat member."""
        params = {'chat_id': chat_id, 'user_id': user_id, **kwargs}
        response = self._make_request("promoteChatMember", params)
        return response.get('ok', False)

    def set_chat_permissions(self, chat_id: Union[int, str], permissions: Dict[str, Any]) -> bool:
        """Set chat permissions."""
        params = {'chat_id': chat_id, 'permissions': permissions}
        response = self._make_request("setChatPermissions", params)
        return response.get('ok', False)

    def get_file(self, file_id: str) -> Dict[str, Any]:
        """Get file information."""
        params = {'file_id': file_id}
        response = self._make_request("getFile", params)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def send_media_group(self, chat_id: Union[int, str], media: List[Dict[str, Any]], **kwargs) -> List[Message]:
        """Send a group of media."""
        params = {'chat_id': chat_id, 'media': media, **kwargs}
        response = self._make_request("sendMediaGroup", params)
        if response.get('ok'):
            return [Message.from_dict(msg) for msg in response['result']]
        raise Exception(response.get('description', 'Unknown error'))
