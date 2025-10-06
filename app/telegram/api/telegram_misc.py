"""
Additional Telegram Bot API miscellaneous endpoints.

This module extends the TelegramBotAPI with remaining miscellaneous methods.
"""

from typing import Optional, List, Dict, Any, Union

# Import base classes from telegram_api.py
from .telegram_api import TelegramBotAPI, Message


class TelegramMiscAPI(TelegramBotAPI):
    """Extension for miscellaneous endpoints."""

    def set_my_commands(self, commands: List[Dict[str, Any]], **kwargs) -> bool:
        """Set the list of the bot's commands."""
        params = {'commands': commands, **kwargs}
        response = self._make_request("setMyCommands", params)
        return response.get('ok', False)

    def get_my_commands(self, **kwargs) -> List[Dict[str, Any]]:
        """Get the current list of the bot's commands."""
        response = self._make_request("getMyCommands", kwargs)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def set_my_name(self, name: str, **kwargs) -> bool:
        """Set the bot's name."""
        params = {'name': name, **kwargs}
        response = self._make_request("setMyName", params)
        return response.get('ok', False)

    def get_my_name(self, **kwargs) -> Optional[Dict[str, Any]]:
        """Get the bot's name."""
        response = self._make_request("getMyName", kwargs)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def set_my_description(self, description: str, **kwargs) -> bool:
        """Set the bot's description."""
        params = {'description': description, **kwargs}
        response = self._make_request("setMyDescription", params)
        return response.get('ok', False)

    def get_my_description(self, **kwargs) -> Optional[Dict[str, Any]]:
        """Get the bot's description."""
        response = self._make_request("getMyDescription", kwargs)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def set_my_short_description(self, short_description: str, **kwargs) -> bool:
        """Set the bot's short description."""
        params = {'short_description': short_description, **kwargs}
        response = self._make_request("setMyShortDescription", params)
        return response.get('ok', False)

    def get_my_short_description(self, **kwargs) -> Optional[Dict[str, Any]]:
        """Get the bot's short description."""
        response = self._make_request("getMyShortDescription", kwargs)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def set_chat_menu_button(self, chat_id: Union[int, str], menu_button: Dict[str, Any]) -> bool:
        """Set the chat menu button."""
        params = {'chat_id': chat_id, 'menu_button': menu_button}
        response = self._make_request("setChatMenuButton", params)
        return response.get('ok', False)

    def get_chat_menu_button(self, chat_id: Union[int, str]) -> Dict[str, Any]:
        """Get the chat menu button."""
        params = {'chat_id': chat_id}
        response = self._make_request("getChatMenuButton", params)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def set_my_default_administrator_rights(self, rights: Dict[str, Any], **kwargs) -> bool:
        """Set default administrator rights."""
        params = {'rights': rights, **kwargs}
        response = self._make_request("setMyDefaultAdministratorRights", params)
        return response.get('ok', False)

    def get_my_default_administrator_rights(self, **kwargs) -> Dict[str, Any]:
        """Get default administrator rights."""
        response = self._make_request("getMyDefaultAdministratorRights", kwargs)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def delete_my_commands(self, **kwargs) -> bool:
        """Delete the list of the bot's commands."""
        response = self._make_request("deleteMyCommands", kwargs)
        return response.get('ok', False)

    def log_out(self) -> bool:
        """Log out from the cloud Bot API server."""
        response = self._make_request("logOut")
        return response.get('ok', False)

    def close(self) -> bool:
        """Close the bot instance."""
        response = self._make_request("close")
        return response.get('ok', False)

    def get_webhook_info(self) -> Dict[str, Any]:
        """Get current webhook status."""
        response = self._make_request("getWebhookInfo")
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def get_me(self) -> Dict[str, Any]:
        """Get basic information about the bot (override for consistency)."""
        response = self._make_request("getMe")
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def get_updates(self, offset: Optional[int] = None, limit: int = 100, timeout: int = 0) -> List[Dict[str, Any]]:
        """Get updates using long polling."""
        params = {'offset': offset, 'limit': limit, 'timeout': timeout}
        response = self._make_request("getUpdates", params)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))

    def send_message(self, chat_id: Union[int, str], text: str, **kwargs) -> Dict[str, Any]:
        """Send a text message."""
        params = {'chat_id': chat_id, 'text': text, **kwargs}
        response = self._make_request("sendMessage", params)
        if response.get('ok'):
            return response['result']
        raise Exception(response.get('description', 'Unknown error'))
