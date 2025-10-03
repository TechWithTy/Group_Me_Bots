from .client import GroupMeClient
from .models import Block, BlocksResponse, BlockBetweenResponse

class BlocksAPI:
    def __init__(self, client: GroupMeClient):
        self._client = client

    async def list(self) -> BlocksResponse:
        """List all blocks."""
        env = await self._client._get("/blocks")
        resp = env.response or {}
        return BlocksResponse.parse_obj(resp)

    async def create(self, user_id: str) -> Block:
        """Block a user."""
        body = {"user_id": user_id}
        env = await self._client._post("/blocks", json=body)
        return Block.parse_obj(env.response)

    async def destroy(self, user_id: str) -> None:
        """Unblock a user."""
        await self._client._post(f"/blocks/{user_id}/destroy")

    async def check_between(self, user_id: str) -> BlockBetweenResponse:
        """Check if there's a block between current user and specified user."""
        env = await self._client._get(f"/blocks/between/{user_id}")
        resp = env.response or {}
        return BlockBetweenResponse.parse_obj(resp)
