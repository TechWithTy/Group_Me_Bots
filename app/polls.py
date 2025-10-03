from typing import Dict
from .client import GroupMeClient
from .models import PollCreateReq, PollCreateResponse, PollData

class PollsAPI:
    def __init__(self, client: GroupMeClient):
        self._client = client

    async def create_poll(self, poll_request: PollCreateReq) -> PollCreateResponse:
        """Create a new poll."""
        env = await self._client._post("/polls", json=poll_request.dict())
        resp = env.response or {}
        return PollCreateResponse.parse_obj(resp)

    async def get_poll(self, poll_id: str) -> PollData:
        """Get poll by ID."""
        env = await self._client._get(f"/polls/{poll_id}")
        return PollData.parse_obj(env.response)

    async def vote_poll(self, poll_id: str, option_id: str) -> Dict:
        """Vote on a poll."""
        body = {"option_id": option_id}
        env = await self._client._post(f"/polls/{poll_id}/vote", json=body)
        return env.response or {}

    async def get_poll_results(self, poll_id: str) -> Dict:
        """Get poll results."""
        env = await self._client._get(f"/polls/{poll_id}/results")
        return env.response or {}
