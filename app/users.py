from .client import GroupMeClient
from .models import User, UserUpdateReq

class UsersAPI:
    def __init__(self, client: GroupMeClient):
        self._client = client

    async def get_me(self) -> User:
        """Get current user info."""
        env = await self._client._get("/users/me")
        return User.parse_obj(env.response)

    async def update_me(self, updates: UserUpdateReq) -> User:
        """Update current user info."""
        env = await self._client._post("/users/update/me", json=updates.dict())
        return User.parse_obj(env.response)

    async def get_user(self, user_id: str) -> User:
        """Get user by ID."""
        env = await self._client._get(f"/users/{user_id}")
        return User.parse_obj(env.response)
