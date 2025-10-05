import httpx
from typing import Any, Dict, Optional

from .models import Envelope

class ApiError(Exception):
    def __init__(self, code: int, errors: Optional[Any]):
        self.code = code
        self.errors = errors
        super().__init__(f"API Error {code}: {errors}")

class GroupMeClient:
    def __init__(self, token: str, base_url: str = "https://api.groupme.com/v3", timeout: float = 10.0):
        self.token = token
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)

    def _url(self, path: str) -> str:
        if path.startswith("/"):
            path = path[1:]
        return f"{self.base_url}/{path}"

    async def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Envelope:
        params = params.copy() if params else {}
        params["token"] = self.token
        resp = await self._client.get(self._url(path), params=params)
        obj = resp.json()
        envelope = Envelope.parse_obj(obj)
        self._check_error(envelope)
        return envelope

    async def _post(self, path: str, json: Optional[Any] = None, params: Optional[Dict[str, Any]] = None) -> Envelope:
        params = params.copy() if params else {}
        params["token"] = self.token
        resp = await self._client.post(self._url(path), json=json, params=params)
        obj = resp.json()
        envelope = Envelope.parse_obj(obj)
        self._check_error(envelope)
        return envelope

    def _check_error(self, envelope: Envelope):
        if envelope.meta.code >= 400:
            raise ApiError(envelope.meta.code, envelope.meta.errors)

    async def close(self):
        await self._client.aclose()
