from typing import Optional, List
from .client import GroupMeClient
from .models import Message, MessagesResponse, Attachment

class MessagesAPI:
    def __init__(self, client: GroupMeClient):
        self._client = client

    async def list_for_group(
        self,
        group_id: str,
        before_id: Optional[str] = None,
        since_id: Optional[str] = None,
        after_id: Optional[str] = None,
        limit: int = 20,
    ) -> MessagesResponse:
        params = {}
        if before_id:
            params["before_id"] = before_id
        if since_id:
            params["since_id"] = since_id
        if after_id:
            params["after_id"] = after_id
        params["limit"] = limit
        env = await self._client._get(f"/groups/{group_id}/messages", params=params)
        resp = env.response or {}
        return MessagesResponse.parse_obj(resp)

    async def post_to_group(
        self,
        group_id: str,
        source_guid: str,
        text: Optional[str] = None,
        attachments: Optional[List[Attachment]] = None,
    ) -> Message:
        body: dict = {"message": {"source_guid": source_guid}}
        if text is not None:
            body["message"]["text"] = text
        if attachments is not None:
            # We assume they are serializable
            body["message"]["attachments"] = [a.dict() for a in attachments]
        env = await self._client._post(f"/groups/{group_id}/messages", json=body)
        # In many cases response is nested: response.message
        resp = env.response or {}
        msgdata = resp.get("message", resp)
        return Message.parse_obj(msgdata)
