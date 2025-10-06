"""
Additional Telegram Bot API business and mini app endpoints.

This module extends the TelegramBotAPI with business account and mini app methods.
"""

from typing import Optional, List, Dict, Any, Union

# Import base classes from telegram_api.py
from .telegram_api import TelegramBotAPI, Message, User


class TelegramBusinessAPI(TelegramBotAPI):
    """Extension for business accounts and mini apps."""

    def get_business_account_info(self, **kwargs) -> Dict[str, Any]:
        """Get information about a business account."""
        response = self._make_request("getBusinessAccountInfo", kwargs)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def read_business_message(self, business_connection_id: str, message_id: int) -> bool:
        """Mark a business message as read."""
        params = {'business_connection_id': business_connection_id, 'message_id': message_id}
        response = self._make_request("readBusinessMessage", params)
        return response.get('ok', False)

    def delete_business_messages(self, business_connection_id: str, message_ids: List[int]) -> bool:
        """Delete business messages."""
        params = {'business_connection_id': business_connection_id, 'message_ids': message_ids}
        response = self._make_request("deleteBusinessMessages", params)
        return response.get('ok', False)

    def set_business_account_name(self, business_connection_id: str, first_name: str, last_name: str) -> bool:
        """Set the name of a business account."""
        params = {'business_connection_id': business_connection_id, 'first_name': first_name, 'last_name': last_name}
        response = self._make_request("setBusinessAccountName", params)
        return response.get('ok', False)

    def set_business_account_username(self, business_connection_id: str, username: str) -> bool:
        """Set the username of a business account."""
        params = {'business_connection_id': business_connection_id, 'username': username}
        response = self._make_request("setBusinessAccountUsername", params)
        return response.get('ok', False)

    def set_business_account_bio(self, business_connection_id: str, bio: str) -> bool:
        """Set the bio of a business account."""
        params = {'business_connection_id': business_connection_id, 'bio': bio}
        response = self._make_request("setBusinessAccountBio", params)
        return response.get('ok', False)

    def set_business_account_profile_photo(self, business_connection_id: str, photo: str) -> bool:
        """Set the profile photo of a business account."""
        params = {'business_connection_id': business_connection_id, 'photo': photo}
        response = self._make_request("setBusinessAccountProfilePhoto", params)
        return response.get('ok', False)

    def remove_business_account_profile_photo(self, business_connection_id: str) -> bool:
        """Remove the profile photo of a business account."""
        params = {'business_connection_id': business_connection_id}
        response = self._make_request("removeBusinessAccountProfilePhoto", params)
        return response.get('ok', False)

    def set_business_account_gift_settings(self, business_connection_id: str, can_receive_gifts: bool, **kwargs) -> bool:
        """Set gift settings for a business account."""
        params = {'business_connection_id': business_connection_id, 'can_receive_gifts': can_receive_gifts, **kwargs}
        response = self._make_request("setBusinessAccountGiftSettings", params)
        return response.get('ok', False)

    def get_business_account_gifts(self, business_connection_id: str, **kwargs) -> List[Dict[str, Any]]:
        """Get gifts owned by a business account."""
        params = {'business_connection_id': business_connection_id, **kwargs}
        response = self._make_request("getBusinessAccountGifts", params)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def post_story(self, business_connection_id: str, content: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Post a story on behalf of a business account."""
        params = {'business_connection_id': business_connection_id, 'content': content, **kwargs}
        response = self._make_request("postStory", params)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def edit_story(self, business_connection_id: str, story_id: int, content: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Edit a story."""
        params = {'business_connection_id': business_connection_id, 'story_id': story_id, 'content': content, **kwargs}
        response = self._make_request("editStory", params)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def delete_story(self, business_connection_id: str, story_id: int) -> bool:
        """Delete a story."""
        params = {'business_connection_id': business_connection_id, 'story_id': story_id}
        response = self._make_request("deleteStory", params)
        return response.get('ok', False)

    def hide_keyboard(self, **kwargs) -> bool:
        """Hide the keyboard in a Web App."""
        response = self._make_request("hideKeyboard", kwargs)
        return response.get('ok', False)
