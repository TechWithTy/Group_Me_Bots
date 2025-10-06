"""
Additional Telegram Bot API chat management endpoints.

This module extends the TelegramBotAPI with advanced chat management methods.
"""

from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass

# Import base classes from telegram_api.py
from .telegram_api import TelegramBotAPI, Chat, User, Message


class TelegramChatAPI(TelegramBotAPI):
    """Extension for chat management endpoints."""

    def set_chat_title(self, chat_id: Union[int, str], title: str) -> bool:
        """Set chat title."""
        params = {'chat_id': chat_id, 'title': title}
        response = self._make_request("setChatTitle", params)
        return response.get('ok', False)

    def set_chat_description(self, chat_id: Union[int, str], description: str) -> bool:
        """Set chat description."""
        params = {'chat_id': chat_id, 'description': description}
        response = self._make_request("setChatDescription", params)
        return response.get('ok', False)

    def pin_chat_message(self, chat_id: Union[int, str], message_id: int, **kwargs) -> bool:
        """Pin a message in the chat."""
        params = {'chat_id': chat_id, 'message_id': message_id, **kwargs}
        response = self._make_request("pinChatMessage", params)
        return response.get('ok', False)

    def unpin_chat_message(self, chat_id: Union[int, str], **kwargs) -> bool:
        """Unpin a message in the chat."""
        params = {'chat_id': chat_id, **kwargs}
        response = self._make_request("unpinChatMessage", params)
        return response.get('ok', False)

    def leave_chat(self, chat_id: Union[int, str]) -> bool:
        """Leave a chat."""
        params = {'chat_id': chat_id}
        response = self._make_request("leaveChat", params)
        return response.get('ok', False)

    def get_chat_administrators(self, chat_id: Union[int, str]) -> List[Dict[str, Any]]:
        """Get chat administrators."""
        params = {'chat_id': chat_id}
        response = self._make_request("getChatAdministrators", params)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def get_chat_member_count(self, chat_id: Union[int, str]) -> int:
        """Get the number of chat members."""
        params = {'chat_id': chat_id}
        response = self._make_request("getChatMemberCount", params)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def get_chat_member(self, chat_id: Union[int, str], user_id: int) -> Dict[str, Any]:
        """Get information about a chat member."""
        params = {'chat_id': chat_id, 'user_id': user_id}
        response = self._make_request("getChatMember", params)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def set_chat_sticker_set(self, chat_id: Union[int, str], sticker_set_name: str) -> bool:
        """Set the chat sticker set."""
        params = {'chat_id': chat_id, 'sticker_set_name': sticker_set_name}
        response = self._make_request("setChatStickerSet", params)
        return response.get('ok', False)

    def delete_chat_sticker_set(self, chat_id: Union[int, str]) -> bool:
        """Delete the chat sticker set."""
        params = {'chat_id': chat_id}
        response = self._make_request("deleteChatStickerSet", params)
        return response.get('ok', False)

    def export_chat_invite_link(self, chat_id: Union[int, str]) -> str:
        """Export chat invite link."""
        params = {'chat_id': chat_id}
        response = self._make_request("exportChatInviteLink", params)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def create_chat_invite_link(self, chat_id: Union[int, str], **kwargs) -> Dict[str, Any]:
        """Create a chat invite link."""
        params = {'chat_id': chat_id, **kwargs}
        response = self._make_request("createChatInviteLink", params)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def edit_chat_invite_link(self, chat_id: Union[int, str], invite_link: str, **kwargs) -> Dict[str, Any]:
        """Edit a chat invite link."""
        params = {'chat_id': chat_id, 'invite_link': invite_link, **kwargs}
        response = self._make_request("editChatInviteLink", params)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def revoke_chat_invite_link(self, chat_id: Union[int, str], invite_link: str) -> Dict[str, Any]:
        """Revoke a chat invite link."""
        params = {'chat_id': chat_id, 'invite_link': invite_link}
        response = self._make_request("revokeChatInviteLink", params)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))
