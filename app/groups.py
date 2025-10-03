from typing import List, Optional

from .client import GroupMeClient
from .models import Group, Member, MemberAddRequest

class GroupsAPI:
    def __init__(self, client: GroupMeClient):
        self._client = client

    async def list(self, page: int = 1, per_page: int = 10, omit: Optional[str] = None) -> List[Group]:
        params = {"page": page, "per_page": per_page}
        if omit:
            params["omit"] = omit
        env = await self._client._get("/groups", params=params)
        data = env.response or []
        return [Group.parse_obj(item) for item in data]

    async def former(self) -> List[Group]:
        env = await self._client._get("/groups/former")
        data = env.response or []
        return [Group.parse_obj(item) for item in data]

    async def get(self, group_id: str) -> Group:
        env = await self._client._get(f"/groups/{group_id}")
        return Group.parse_obj(env.response)

    async def add_members(self, group_id: str, members: MemberAddRequest) -> str:
        """Returns results_id for later polling."""
        env = await self._client._post(f"/groups/{group_id}/members/add", json=members.dict())
        resp = env.response or {}
        return resp.get("results_id")

    async def get_add_results(self, group_id: str, results_id: str) -> List[Member]:
        env = await self._client._get(f"/groups/{group_id}/members/results/{results_id}")
        resp = env.response or {}
        members = resp.get("members", [])
        return [Member.parse_obj(m) for m in members]

    async def remove_member(self, group_id: str, membership_id: str) -> None:
        await self._client._post(f"/groups/{group_id}/members/{membership_id}/remove")

    async def update_membership(self, group_id: str, nickname: str) -> Member:
        body = {"membership": {"nickname": nickname}}
        env = await self._client._post(f"/groups/{group_id}/memberships/update", json=body)
        return Member.parse_obj(env.response)
