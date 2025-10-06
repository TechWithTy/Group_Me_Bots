"""
Member Management Workflow for Telegram Bot.

This workflow manages chat members using existing Telegram API endpoints
like ban, unban, promote, etc.
"""

import time
from typing import Dict, Any, List
from app.telegram.api.telegram_api import TelegramBotAPI, Update, Message


class MemberManagementWorkflow:
    """Workflow for managing chat members."""

    def __init__(self, bot: TelegramBotAPI):
        self.bot = bot
        self.admin_commands = {
            '/ban': self.handle_ban,
            '/unban': self.handle_unban,
            '/promote': self.handle_promote,
            '/demote': self.handle_demote,
        }

    def process_update(self, update: Update) -> None:
        """Process an incoming update for member management."""
        if update.message and update.message.text:
            self.handle_member_command(update.message)

    def handle_member_command(self, message: Message) -> None:
        """Handle member management commands."""
        if message.text.startswith('/'):
            parts = message.text.split()
            if len(parts) >= 2 and parts[0] in self.admin_commands:
                command = parts[0]
                target_user_id = self.extract_user_id(parts[1:])
                if target_user_id:
                    self.admin_commands[command](message.chat.id, target_user_id)

    def extract_user_id(self, args: List[str]) -> Optional[int]:
        """Extract user ID from command arguments."""
        try:
            return int(args[0])
        except (ValueError, IndexError):
            return None

    def handle_ban(self, chat_id: int, user_id: int) -> None:
        """Ban a user from the chat."""
        if self.bot.ban_chat_member(chat_id, user_id):
            self.bot.send_message(chat_id, f"User {user_id} has been banned.")
        else:
            self.bot.send_message(chat_id, "Failed to ban user.")

    def handle_unban(self, chat_id: int, user_id: int) -> None:
        """Unban a user from the chat."""
        if self.bot.unban_chat_member(chat_id, user_id):
            self.bot.send_message(chat_id, f"User {user_id} has been unbanned.")
        else:
            self.bot.send_message(chat_id, "Failed to unban user.")

    def handle_promote(self, chat_id: int, user_id: int) -> None:
        """Promote a user to admin."""
        if self.bot.promote_chat_member(chat_id, user_id, can_manage_chat=True):
            self.bot.send_message(chat_id, f"User {user_id} has been promoted to admin.")
        else:
            self.bot.send_message(chat_id, "Failed to promote user.")

    def handle_demote(self, chat_id: int, user_id: int) -> None:
        """Demote a user from admin (remove admin rights)."""
        # Note: Telegram API doesn't have a direct demote, so we set minimal rights
        if self.bot.promote_chat_member(chat_id, user_id, can_manage_chat=False, can_post_messages=False):
            self.bot.send_message(chat_id, f"User {user_id} has been demoted.")
        else:
            self.bot.send_message(chat_id, "Failed to demote user.")

    def check_member_status(self, chat_id: int, user_id: int) -> None:
        """Check and report member status."""
        try:
            member = self.bot.get_chat_member(chat_id, user_id)
            status = member.get('status', 'unknown')
            self.bot.send_message(chat_id, f"User {user_id} status: {status}")
        except Exception as e:
            self.bot.send_message(chat_id, f"Error checking member: {str(e)}")

    def list_admins(self, chat_id: int) -> None:
        """List all chat administrators."""
        try:
            admins = self.bot.get_chat_administrators(chat_id)
            admin_list = [admin['user']['first_name'] for admin in admins if admin['status'] == 'administrator']
            response = "Admins: " + ", ".join(admin_list) if admin_list else "No admins found."
            self.bot.send_message(chat_id, response)
        except Exception as e:
            self.bot.send_message(chat_id, f"Error listing admins: {str(e)}")

    def run_workflow(self, updates: List[Update]) -> None:
        """Run the workflow on a list of updates."""
        for update in updates:
            self.process_update(update)
            time.sleep(0.1)  # Small delay
