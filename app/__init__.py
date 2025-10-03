from .client import GroupMeClient
from .groups import GroupsAPI
from .messages_api import MessagesAPI
from .bots_api import BotsAPI
from .users import UsersAPI
from .blocks import BlocksAPI
from .polls import PollsAPI
from . import models

class GroupMe:
    def __init__(self, token: str):
        self.client = GroupMeClient(token)
        self.groups = GroupsAPI(self.client)
        self.messages = MessagesAPI(self.client)
        self.bots = BotsAPI(self.client)
        self.users = UsersAPI(self.client)
        self.blocks = BlocksAPI(self.client)
        self.polls = PollsAPI(self.client)

    async def close(self):
        await self.client.close()