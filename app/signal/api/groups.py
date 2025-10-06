"""Group management endpoints that emulate the Signal CLI behaviour."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Body, HTTPException, Path, Response, status
from pydantic import BaseModel, Field

from .helpers import add_members, ensure_account, placeholder_image, state
from .state.models import Group, GroupPermissions

router = APIRouter()


class GroupPermissionsPayload(BaseModel):
    add_members: Optional[str] = None
    edit_group: Optional[str] = None
    send_messages: Optional[str] = None


class CreateGroupRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    members: List[str] = Field(default_factory=list)
    group_link: Optional[str] = None
    permissions: Optional[GroupPermissionsPayload] = None
    expiration_time: Optional[int] = None


class CreateGroupResponse(BaseModel):
    id: str


class UpdateGroupRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    base64_avatar: Optional[str] = None
    group_link: Optional[str] = None
    permissions: Optional[GroupPermissionsPayload] = None
    expiration_time: Optional[int] = None


class ChangeGroupMembersRequest(BaseModel):
    members: List[str]


class ChangeGroupAdminsRequest(BaseModel):
    admins: List[str]


class GroupEntry(BaseModel):
    id: str
    name: Optional[str] = None
    description: Optional[str] = None
    members: List[str] = Field(default_factory=list)
    admins: List[str] = Field(default_factory=list)
    group_link: Optional[str] = None
    expiration_time: Optional[int] = None


def _fetch_group(number: str, group_id: str) -> Group:
    account = ensure_account(number)
    group = account.groups.get(group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return group


@router.get("/{number}", response_model=list[GroupEntry])
async def list_groups(number: str = Path(..., description="Registered Phone Number")) -> list[GroupEntry]:
    account = ensure_account(number)
    return [
        GroupEntry(
            id=group.identifier,
            name=group.name,
            description=group.description,
            members=sorted(group.members),
            admins=sorted(group.admins),
            group_link=group.group_link,
            expiration_time=group.expiration_time,
        )
        for group in account.groups.values()
    ]


@router.post("/{number}", response_model=CreateGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    number: str = Path(..., description="Registered Phone Number"),
    data: CreateGroupRequest = Body(..., description="Input Data"),
) -> CreateGroupResponse:
    account = ensure_account(number)
    group_id = state.next_group_id()
    group = Group(identifier=group_id, name=data.name, description=data.description, avatar=placeholder_image(group_id))
    group.members.add(number)
    add_members(group.members, data.members)
    group.admins.add(number)
    group.group_link = data.group_link
    group.expiration_time = data.expiration_time
    if data.permissions:
        payload = data.permissions.dict(exclude_none=True)
        group.permissions = GroupPermissions(**payload)
    account.groups[group_id] = group
    return CreateGroupResponse(id=group_id)


@router.get("/{number}/{groupid}", response_model=GroupEntry)
async def get_group(
    number: str = Path(..., description="Registered Phone Number"),
    groupid: str = Path(..., description="Group ID"),
) -> GroupEntry:
    group = _fetch_group(number, groupid)
    return GroupEntry(
        id=group.identifier,
        name=group.name,
        description=group.description,
        members=sorted(group.members),
        admins=sorted(group.admins),
        group_link=group.group_link,
        expiration_time=group.expiration_time,
    )


@router.put("/{number}/{groupid}", status_code=status.HTTP_204_NO_CONTENT)
async def update_group(
    number: str = Path(..., description="Registered Phone Number"),
    groupid: str = Path(..., description="Group ID"),
    data: UpdateGroupRequest = Body(..., description="Input Data"),
) -> Response:
    group = _fetch_group(number, groupid)
    if data.name is not None:
        group.name = data.name
    if data.description is not None:
        group.description = data.description
    if data.base64_avatar is not None:
        group.avatar = data.base64_avatar
    if data.group_link is not None:
        group.group_link = data.group_link
    if data.expiration_time is not None:
        group.expiration_time = data.expiration_time
    if data.permissions:
        payload = data.permissions.dict(exclude_none=True)
        group.permissions = GroupPermissions(**payload)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{number}/{groupid}")
async def delete_group(
    number: str = Path(..., description="Registered Phone Number"),
    groupid: str = Path(..., description="Group ID"),
) -> dict:
    account = ensure_account(number)
    if account.groups.pop(groupid, None) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return {"message": "Group deleted successfully"}


@router.post("/{number}/{groupid}/admins", status_code=status.HTTP_204_NO_CONTENT)
async def add_group_admins(
    number: str = Path(..., description="Registered Phone Number"),
    groupid: str = Path(..., description="Group ID"),
    data: ChangeGroupAdminsRequest = Body(..., description="Admins"),
) -> Response:
    group = _fetch_group(number, groupid)
    add_members(group.admins, data.admins)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{number}/{groupid}/admins", status_code=status.HTTP_204_NO_CONTENT)
async def remove_group_admins(
    number: str = Path(..., description="Registered Phone Number"),
    groupid: str = Path(..., description="Group ID"),
    data: ChangeGroupAdminsRequest = Body(..., description="Admins"),
) -> Response:
    group = _fetch_group(number, groupid)
    for admin in data.admins:
        group.admins.discard(admin)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{number}/{groupid}/avatar")
async def get_group_avatar(
    number: str = Path(..., description="Registered Phone Number"),
    groupid: str = Path(..., description="Group ID"),
) -> dict:
    group = _fetch_group(number, groupid)
    return {"avatar": group.avatar or placeholder_image(groupid), "content_type": "image/png"}


@router.post("/{number}/{groupid}/block", status_code=status.HTTP_204_NO_CONTENT)
async def block_group(
    number: str = Path(..., description="Registered Phone Number"),
    groupid: str = Path(..., description="Group ID"),
) -> Response:
    group = _fetch_group(number, groupid)
    group.blocked = True
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{number}/{groupid}/join", status_code=status.HTTP_204_NO_CONTENT)
async def join_group(
    number: str = Path(..., description="Registered Phone Number"),
    groupid: str = Path(..., description="Group ID"),
) -> Response:
    group = _fetch_group(number, groupid)
    group.members.add(number)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{number}/{groupid}/members", status_code=status.HTTP_204_NO_CONTENT)
async def add_group_members(
    number: str = Path(..., description="Registered Phone Number"),
    groupid: str = Path(..., description="Group ID"),
    data: ChangeGroupMembersRequest = Body(..., description="Members"),
) -> Response:
    group = _fetch_group(number, groupid)
    add_members(group.members, data.members)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{number}/{groupid}/members", status_code=status.HTTP_204_NO_CONTENT)
async def remove_group_members(
    number: str = Path(..., description="Registered Phone Number"),
    groupid: str = Path(..., description="Group ID"),
    data: ChangeGroupMembersRequest = Body(..., description="Members"),
) -> Response:
    group = _fetch_group(number, groupid)
    for member in data.members:
        group.members.discard(member)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{number}/{groupid}/quit", status_code=status.HTTP_204_NO_CONTENT)
async def quit_group(
    number: str = Path(..., description="Registered Phone Number"),
    groupid: str = Path(..., description="Group ID"),
) -> Response:
    group = _fetch_group(number, groupid)
    group.members.discard(number)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
