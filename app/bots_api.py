from typing import List, Optional, Dict
from .client import GroupMeClient
from .models import Bot, BotCreateReq, BotPostReq

class BotsAPI:
    def __init__(self, client: GroupMeClient):
        self._client = client

    async def list(self) -> List[Bot]:
        """Get all bots for the authenticated user."""
        env = await self._client._get("/bots")
        data = env.response or []
        return [Bot.parse_obj(item) for item in data]

    async def create(self, bot_data: BotCreateReq) -> Bot:
        """Create a new bot."""
        env = await self._client._post("/bots", json=bot_data.dict())
        return Bot.parse_obj(env.response)

    async def destroy(self, bot_id: str) -> None:
        """Destroy a bot."""
        await self._client._post(f"/bots/{bot_id}/destroy")

    async def post_message(self, bot_id: str, text: str, picture_url: Optional[str] = None) -> Dict:
        """Post a message via bot."""
        body = {"bot_id": bot_id, "text": text}
        if picture_url:
            body["picture_url"] = picture_url
        env = await self._client._post("/bots/post", json=body)
        return env.response or {}
