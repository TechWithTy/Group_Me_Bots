from typing import List, Optional, Union, Dict
from pydantic import BaseModel

# Envelope / meta

class Meta(BaseModel):
    code: int
    errors: Optional[List[str]] = None

class Envelope(BaseModel):
    meta: Meta
    response: Optional[Union[Dict, List[Dict]]] = None

# Attachments

class AttachmentBase(BaseModel):
    type: str

class ImageAttachment(AttachmentBase):
    type: str = "image"
    url: str

class LocationAttachment(AttachmentBase):
    type: str = "location"
    lat: str
    lng: str
    name: str

class SplitAttachment(AttachmentBase):
    type: str = "split"
    token: str

class EmojiAttachment(AttachmentBase):
    type: str = "emoji"
    placeholder: str
    charmap: List[List[int]]

Attachment = Union[
    ImageAttachment,
    LocationAttachment,
    SplitAttachment,
    EmojiAttachment,
]

# Message

class Message(BaseModel):
    id: str
    source_guid: Optional[str] = None
    created_at: int
    user_id: Optional[str] = None
    group_id: Optional[str] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    text: Optional[str] = None
    system: Optional[bool] = None
    favorited_by: Optional[List[str]] = None
    attachments: Optional[List[Attachment]] = None

class MessagesResponse(BaseModel):
    count: int
    messages: List[Message]

# Member / Group

class Member(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    nickname: Optional[str] = None
    muted: Optional[bool] = None
    image_url: Optional[str] = None
    autokicked: Optional[bool] = None
    app_installed: Optional[bool] = None
    guid: Optional[str] = None

class MessagePreview(BaseModel):
    nickname: str
    text: Optional[str] = None
    image_url: Optional[str] = None
    attachments: Optional[List[Attachment]] = None

class GroupMessagesSummary(BaseModel):
    count: int
    last_message_id: Optional[str] = None
    last_message_created_at: Optional[int] = None
    preview: Optional[MessagePreview] = None

class Group(BaseModel):
    id: str
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    creator_user_id: Optional[str] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    members: Optional[List[Member]] = None
    share_url: Optional[str] = None
    messages: Optional[GroupMessagesSummary] = None

# Chat (Direct messages)

class ChatLastMessage(BaseModel):
    attachments: Optional[List[Attachment]] = None
    avatar_url: Optional[str] = None
    conversation_id: Optional[str] = None
    created_at: Optional[int] = None
    favorited_by: Optional[List[str]] = None
    id: Optional[str] = None
    name: Optional[str] = None
    recipient_id: Optional[str] = None
    sender_id: Optional[str] = None
    sender_type: Optional[str] = None
    source_guid: Optional[str] = None
    text: Optional[str] = None
    user_id: Optional[str] = None

class Chat(BaseModel):
    created_at: int
    updated_at: int
    last_message: ChatLastMessage
    messages_count: int
    other_user: Dict[str, Optional[Union[str,int]]]  # e.g. { "id": "...", "name": "...", "avatar_url": "..." }

# Bot, User, Blocks, Polls

class Bot(BaseModel):
    bot_id: str
    group_id: str
    name: str
    avatar_url: Optional[str] = None
    callback_url: Optional[str] = None
    dm_notification: Optional[bool] = None
    active: bool

class User(BaseModel):
    id: str
    phone_number: Optional[str] = None
    image_url: Optional[str] = None
    name: Optional[str] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    email: Optional[str] = None
    sms: Optional[bool] = None

class Block(BaseModel):
    user_id: str
    blocked_user_id: str
    created_at: int

class BlocksResponse(BaseModel):
    blocks: List[Block]

class BlockBetweenResponse(BaseModel):
    between: bool

# Request models

class MembershipUpdateReq(BaseModel):
    membership: Dict[str, str]  # e.g. { "nickname": "NewNick" }

class BotCreateReq(BaseModel):
    bot: Dict[str, Union[str, bool]]

class BotPostReq(BaseModel):
    bot_id: str
    text: str
    picture_url: Optional[str] = None
    attachments: Optional[List[Attachment]] = None

class UserUpdateReq(BaseModel):
    avatar_url: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    zip_code: Optional[str] = None

class MemberAddRequest(BaseModel):
    members: List[Dict[str, str]]  # each dict: nickname, email, guid

class PollOption(BaseModel):
    title: str

class PollCreateReq(BaseModel):
    subject: str
    options: List[PollOption]
    expiration: int
    type: str  # "single" or "multi"
    visibility: str  # "public" or "anonymous"

class PollData(BaseModel):
    id: Optional[str] = None
    subject: Optional[str] = None
    owner_id: Optional[str] = None
    conversation_id: Optional[str] = None
    created_at: Optional[int] = None
    expiration: Optional[int] = None
    status: Optional[str] = None
    options: Optional[List[Dict[str, str]]] = None
    last_modified: Optional[int] = None
    type: Optional[str] = None
    visibility: Optional[str] = None

class PollCreateResponse(BaseModel):
    poll: Dict[str, PollData]
    message: Message
