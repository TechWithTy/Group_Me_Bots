"""
Pydantic models for Discord API.

This module contains all the request and response models used by the Discord API endpoints.
Based on Discord API v10 specification.
"""
from typing import List, Optional, Union, Dict, Any
from enum import Enum
from datetime import datetime

from pydantic import BaseModel, Field, validator

# Common Snowflake type (Discord IDs)
SnowflakeType = int

class ChannelType(str, Enum):
    """Discord channel types."""
    GUILD_TEXT = "GUILD_TEXT"
    DM = "DM"
    GUILD_VOICE = "GUILD_VOICE"
    GROUP_DM = "GROUP_DM"
    GUILD_CATEGORY = "GUILD_CATEGORY"
    GUILD_ANNOUNCEMENT = "GUILD_ANNOUNCEMENT"
    ANNOUNCEMENT_THREAD = "ANNOUNCEMENT_THREAD"
    PUBLIC_THREAD = "PUBLIC_THREAD"
    PRIVATE_THREAD = "PRIVATE_THREAD"
    GUILD_STAGE_VOICE = "GUILD_STAGE_VOICE"
    GUILD_DIRECTORY = "GUILD_DIRECTORY"
    GUILD_FORUM = "GUILD_FORUM"

class MessageType(str, Enum):
    """Discord message types."""
    DEFAULT = "DEFAULT"
    RECIPIENT_ADD = "RECIPIENT_ADD"
    RECIPIENT_REMOVE = "RECIPIENT_REMOVE"
    CALL = "CALL"
    CHANNEL_NAME_CHANGE = "CHANNEL_NAME_CHANGE"
    CHANNEL_ICON_CHANGE = "CHANNEL_ICON_CHANGE"
    CHANNEL_PINNED_MESSAGE = "CHANNEL_PINNED_MESSAGE"
    GUILD_MEMBER_JOIN = "GUILD_MEMBER_JOIN"
    USER_PREMIUM_GUILD_SUBSCRIPTION = "USER_PREMIUM_GUILD_SUBSCRIPTION"
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_1 = "USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_1"
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2 = "USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2"
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_3 = "USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_3"
    CHANNEL_FOLLOW_ADD = "CHANNEL_FOLLOW_ADD"
    GUILD_DISCOVERY_DISQUALIFIED = "GUILD_DISCOVERY_DISQUALIFIED"
    GUILD_DISCOVERY_REQUALIFIED = "GUILD_DISCOVERY_REQUALIFIED"
    GUILD_DISCOVERY_GRACE_PERIOD_INITIAL_WARNING = "GUILD_DISCOVERY_GRACE_PERIOD_INITIAL_WARNING"
    GUILD_DISCOVERY_GRACE_PERIOD_FINAL_WARNING = "GUILD_DISCOVERY_GRACE_PERIOD_FINAL_WARNING"
    THREAD_CREATED = "THREAD_CREATED"
    REPLY = "REPLY"
    APPLICATION_COMMAND = "APPLICATION_COMMAND"
    THREAD_STARTER_MESSAGE = "THREAD_STARTER_MESSAGE"
    GUILD_INVITE_REMINDER = "GUILD_INVITE_REMINDER"
    CONTEXT_MENU_COMMAND = "CONTEXT_MENU_COMMAND"

# Base response models
class DiscordObject(BaseModel):
    """Base model for all Discord objects with common fields."""
    id: SnowflakeType

class User(DiscordObject):
    """Discord user object."""
    username: str
    discriminator: str
    avatar: Optional[str] = None
    bot: Optional[bool] = False
    system: Optional[bool] = False
    mfa_enabled: Optional[bool] = False
    banner: Optional[str] = None
    accent_color: Optional[int] = None
    locale: Optional[str] = None
    verified: Optional[bool] = False
    email: Optional[str] = None
    flags: Optional[int] = 0
    premium_type: Optional[int] = 0
    public_flags: Optional[int] = 0

class Channel(DiscordObject):
    """Discord channel object."""
    type: ChannelType
    name: Optional[str] = None
    position: Optional[int] = None
    parent_id: Optional[SnowflakeType] = None
    topic: Optional[str] = None
    nsfw: Optional[bool] = False
    bitrate: Optional[int] = None
    user_limit: Optional[int] = None
    rate_limit_per_user: Optional[int] = None
    rtc_region: Optional[str] = None
    video_quality_mode: Optional[int] = None
    guild_id: Optional[SnowflakeType] = None
    last_message_id: Optional[SnowflakeType] = None
    last_pin_timestamp: Optional[datetime] = None
    default_auto_archive_duration: Optional[int] = None
    permission_overwrites: Optional[List[Dict[str, Any]]] = None
    flags: Optional[int] = 0

class Message(DiscordObject):
    """Discord message object."""
    channel_id: SnowflakeType
    author: User
    content: str
    timestamp: datetime
    edited_timestamp: Optional[datetime] = None
    tts: bool = False
    mention_everyone: bool = False
    mentions: List[User] = Field(default_factory=list)
    mention_roles: List[SnowflakeType] = Field(default_factory=list)
    mention_channels: Optional[List[Channel]] = Field(default_factory=list)
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    embeds: List[Dict[str, Any]] = Field(default_factory=list)
    reactions: List[Dict[str, Any]] = Field(default_factory=list)
    nonce: Optional[Union[int, str]] = None
    pinned: bool = False
    webhook_id: Optional[SnowflakeType] = None
    type: MessageType = MessageType.DEFAULT
    activity: Optional[Dict[str, Any]] = None
    application: Optional[Dict[str, Any]] = None
    application_id: Optional[SnowflakeType] = None
    message_reference: Optional[Dict[str, Any]] = None
    flags: Optional[int] = 0
    referenced_message: Optional['Message'] = None
    interaction: Optional[Dict[str, Any]] = None
    thread: Optional[Channel] = None
    components: List[Dict[str, Any]] = Field(default_factory=list)
    sticker_items: List[Dict[str, Any]] = Field(default_factory=list)
    stickers: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    position: Optional[int] = None
    role_subscription_data: Optional[Dict[str, Any]] = None

class Guild(DiscordObject):
    """Discord guild object."""
    name: str
    icon: Optional[str] = None
    icon_hash: Optional[str] = None
    splash: Optional[str] = None
    discovery_splash: Optional[str] = None
    owner: Optional[bool] = False
    owner_id: SnowflakeType
    permissions: Optional[str] = None
    region: Optional[str] = None
    afk_channel_id: Optional[SnowflakeType] = None
    afk_timeout: int = 300
    widget_enabled: Optional[bool] = False
    widget_channel_id: Optional[SnowflakeType] = None
    verification_level: int = 0
    default_message_notifications: int = 0
    explicit_content_filter: int = 0
    roles: List[Dict[str, Any]] = Field(default_factory=list)
    emojis: List[Dict[str, Any]] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    mfa_level: int = 0
    application_id: Optional[SnowflakeType] = None
    system_channel_id: Optional[SnowflakeType] = None
    system_channel_flags: int = 0
    rules_channel_id: Optional[SnowflakeType] = None
    max_presences: Optional[int] = 25000
    max_members: Optional[int] = None
    vanity_url_code: Optional[str] = None
    description: Optional[str] = None
    banner: Optional[str] = None
    premium_tier: int = 0
    premium_subscription_count: Optional[int] = 0
    preferred_locale: str = "en-US"
    public_updates_channel_id: Optional[SnowflakeType] = None
    max_video_channel_users: Optional[int] = 25
    max_stage_video_channel_users: Optional[int] = 50
    approximate_member_count: Optional[int] = None
    approximate_presence_count: Optional[int] = None
    welcome_screen: Optional[Dict[str, Any]] = None
    nsfw_level: int = 0
    stickers: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    premium_progress_bar_enabled: bool = False
    safety_alerts_channel_id: Optional[SnowflakeType] = None

class Role(DiscordObject):
    """Discord role object."""
    name: str
    color: int = 0
    hoist: bool = False
    icon: Optional[str] = None
    unicode_emoji: Optional[str] = None
    position: int = 0
    permissions: str = "0"
    managed: bool = False
    mentionable: bool = False
    tags: Optional[Dict[str, Any]] = None
    flags: int = 0

class Webhook(DiscordObject):
    """Discord webhook object."""
    type: int = 1
    guild_id: Optional[SnowflakeType] = None
    channel_id: Optional[SnowflakeType] = None
    user: Optional[User] = None
    name: Optional[str] = None
    avatar: Optional[str] = None
    token: Optional[str] = None
    application_id: Optional[SnowflakeType] = None
    source_guild: Optional[Guild] = None
    source_channel: Optional[Channel] = None
    url: Optional[str] = None

# Request models
class CreateChannelRequest(BaseModel):
    """Request to create a channel."""
    name: str
    type: Optional[ChannelType] = ChannelType.GUILD_TEXT
    topic: Optional[str] = None
    bitrate: Optional[int] = None
    user_limit: Optional[int] = None
    rate_limit_per_user: Optional[int] = None
    position: Optional[int] = None
    permission_overwrites: Optional[List[Dict[str, Any]]] = None
    parent_id: Optional[SnowflakeType] = None
    nsfw: Optional[bool] = False

class UpdateChannelRequest(BaseModel):
    """Request to update a channel."""
    name: Optional[str] = None
    type: Optional[ChannelType] = None
    topic: Optional[str] = None
    bitrate: Optional[int] = None
    user_limit: Optional[int] = None
    rate_limit_per_user: Optional[int] = None
    position: Optional[int] = None
    permission_overwrites: Optional[List[Dict[str, Any]]] = None
    parent_id: Optional[SnowflakeType] = None
    nsfw: Optional[bool] = None

class CreateMessageRequest(BaseModel):
    """Request to create a message."""
    content: Optional[str] = None
    nonce: Optional[Union[int, str]] = None
    tts: Optional[bool] = False
    embeds: Optional[List[Dict[str, Any]]] = None
    embed: Optional[Dict[str, Any]] = None  # Deprecated, use embeds
    allowed_mentions: Optional[Dict[str, Any]] = None
    message_reference: Optional[Dict[str, Any]] = None
    components: Optional[List[Dict[str, Any]]] = None
    sticker_ids: Optional[List[SnowflakeType]] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    flags: Optional[int] = None

class EditMessageRequest(BaseModel):
    """Request to edit a message."""
    content: Optional[str] = None
    embeds: Optional[List[Dict[str, Any]]] = None
    flags: Optional[int] = None
    allowed_mentions: Optional[Dict[str, Any]] = None
    components: Optional[List[Dict[str, Any]]] = None
    attachments: Optional[List[Dict[str, Any]]] = None

class CreateGuildRequest(BaseModel):
    """Request to create a guild."""
    name: str
    region: Optional[str] = None
    icon: Optional[str] = None
    verification_level: Optional[int] = None
    default_message_notifications: Optional[int] = None
    explicit_content_filter: Optional[int] = None
    roles: Optional[List[Dict[str, Any]]] = None
    channels: Optional[List[Dict[str, Any]]] = None
    afk_channel_id: Optional[SnowflakeType] = None
    afk_timeout: Optional[int] = None
    system_channel_id: Optional[SnowflakeType] = None
    system_channel_flags: Optional[int] = None

class CreateRoleRequest(BaseModel):
    """Request to create a role."""
    name: Optional[str] = None
    permissions: Optional[str] = None
    color: Optional[int] = None
    hoist: Optional[bool] = None
    icon: Optional[str] = None
    unicode_emoji: Optional[str] = None
    mentionable: Optional[bool] = None

class UpdateRoleRequest(BaseModel):
    """Request to update a role."""
    name: Optional[str] = None
    permissions: Optional[str] = None
    color: Optional[int] = None
    hoist: Optional[bool] = None
    icon: Optional[str] = None
    unicode_emoji: Optional[str] = None
    mentionable: Optional[bool] = None

class CreateWebhookRequest(BaseModel):
    """Request to create a webhook."""
    name: str
    avatar: Optional[str] = None

class UpdateWebhookRequest(BaseModel):
    """Request to update a webhook."""
    name: Optional[str] = None
    avatar: Optional[str] = None
    channel_id: Optional[SnowflakeType] = None

class ExecuteWebhookRequest(BaseModel):
    """Request to execute a webhook."""
    content: Optional[str] = None
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    tts: Optional[bool] = False
    embeds: Optional[List[Dict[str, Any]]] = None
    allowed_mentions: Optional[Dict[str, Any]] = None
    components: Optional[List[Dict[str, Any]]] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    flags: Optional[int] = None
    thread_name: Optional[str] = None
    thread_id: Optional[SnowflakeType] = None

# Application command models
class ApplicationCommand(BaseModel):
    """Application command object."""
    id: SnowflakeType
    type: int
    application_id: SnowflakeType
    guild_id: Optional[SnowflakeType] = None
    name: str
    name_localizations: Optional[Dict[str, str]] = None
    description: str
    description_localizations: Optional[Dict[str, str]] = None
    options: Optional[List[Dict[str, Any]]] = None
    default_member_permissions: Optional[str] = None
    dm_permission: Optional[bool] = True
    default_permission: Optional[bool] = True  # Deprecated
    nsfw: Optional[bool] = False
    version: SnowflakeType

class ApplicationCommandCreateRequest(BaseModel):
    """Request to create an application command."""
    name: str
    description: Optional[str] = None
    options: Optional[List[Dict[str, Any]]] = None
    default_member_permissions: Optional[str] = None
    dm_permission: Optional[bool] = True
    default_permission: Optional[bool] = True  # Deprecated
    type: Optional[int] = 1
    nsfw: Optional[bool] = False

class ApplicationCommandUpdateRequest(BaseModel):
    """Request to update application commands."""
    name: Optional[str] = None
    description: Optional[str] = None
    options: Optional[List[Dict[str, Any]]] = None
    default_member_permissions: Optional[str] = None
    dm_permission: Optional[bool] = None

# Emoji models
class Emoji(BaseModel):
    """Discord emoji object."""
    id: Optional[SnowflakeType] = None
    name: Optional[str] = None
    roles: Optional[List[SnowflakeType]] = None
    user: Optional[User] = None
    require_colons: Optional[bool] = True
    managed: Optional[bool] = False
    animated: Optional[bool] = False
    available: Optional[bool] = True

class CreateApplicationEmojiRequest(BaseModel):
    """Request to create an application emoji."""
    name: str
    image: str  # Base64 encoded image data

class UpdateApplicationEmojiRequest(BaseModel):
    """Request to update an application emoji."""
    name: Optional[str] = None

# Entitlement models
class Entitlement(BaseModel):
    """Discord entitlement object."""
    id: SnowflakeType
    sku_id: SnowflakeType
    application_id: SnowflakeType
    user_id: Optional[SnowflakeType] = None
    guild_id: Optional[SnowflakeType] = None
    type: int
    deleted: bool = False
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None

class CreateEntitlementRequest(BaseModel):
    """Request to create an entitlement."""
    sku_id: SnowflakeType
    user_id: Optional[SnowflakeType] = None
    guild_id: Optional[SnowflakeType] = None

# Invite models
class Invite(BaseModel):
    """Discord invite object."""
    code: str
    guild: Optional[Guild] = None
    channel: Optional[Channel] = None
    inviter: Optional[User] = None
    target_type: Optional[int] = None
    target_user: Optional[User] = None
    target_application: Optional[Dict[str, Any]] = None
    approximate_presence_count: Optional[int] = None
    approximate_member_count: Optional[int] = None
    expires_at: Optional[datetime] = None
    stage_instance: Optional[Dict[str, Any]] = None
    guild_scheduled_event: Optional[Dict[str, Any]] = None
    uses: int = 0
    max_uses: int = 0
    max_age: int = 0
    temporary: bool = False
    created_at: datetime

class CreateChannelInviteRequest(BaseModel):
    """Request to create a channel invite."""
    max_age: int = 86400
    max_uses: int = 0
    temporary: bool = False
    unique: bool = False
    target_type: Optional[int] = None
    target_user_id: Optional[SnowflakeType] = None
    target_application_id: Optional[SnowflakeType] = None

# Voice models
class VoiceState(BaseModel):
    """Discord voice state object."""
    channel_id: Optional[SnowflakeType] = None
    user_id: SnowflakeType
    session_id: str
    deaf: bool = False
    mute: bool = False
    self_deaf: bool = False
    self_mute: bool = False
    self_stream: Optional[bool] = False
    self_video: bool = False
    suppress: bool = False
    request_to_speak_timestamp: Optional[datetime] = None

class VoiceRegion(BaseModel):
    """Discord voice region object."""
    id: str
    name: str
    optimal: bool = False
    deprecated: bool = False
    custom: bool = False

# Permission models
class PermissionOverwrite(BaseModel):
    """Discord permission overwrite object."""
    id: SnowflakeType
    type: int  # 0 for role, 1 for member
    allow: str = "0"
    deny: str = "0"

class RoleConnection(BaseModel):
    """Discord role connection object."""
    platform_name: Optional[str] = None
    platform_username: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Response models (for specific endpoints)
class GatewayBotResponse(BaseModel):
    """Response for gateway bot information."""
    url: str
    shards: int
    session_start_limit: Dict[str, Any]

class ApplicationResponse(BaseModel):
    """Response for application information."""
    id: SnowflakeType
    name: str
    icon: Optional[str] = None
    description: str
    rpc_origins: Optional[List[str]] = None
    bot_public: bool = True
    bot_require_code_grant: bool = False
    bot: Optional[User] = None
    terms_of_service_url: Optional[str] = None
    privacy_policy_url: Optional[str] = None
    owner: Optional[User] = None
    summary: str = ""
    verify_key: str
    team: Optional[Dict[str, Any]] = None
    guild_id: Optional[SnowflakeType] = None
    primary_sku_id: Optional[SnowflakeType] = None
    slug: Optional[str] = None
    cover_image: Optional[str] = None
    flags: Optional[int] = 0
    tags: Optional[List[str]] = None
    install_params: Optional[Dict[str, Any]] = None
    custom_install_url: Optional[str] = None
    role_connections_verification_entry: Optional[Dict[str, Any]] = None

# Utility functions for model conversion
def discord_user_to_user(discord_user) -> User:
    """Convert discord.py User to API User model."""
    return User(
        id=discord_user.id,
        username=discord_user.name,
        discriminator=discord_user.discriminator,
        avatar=discord_user.avatar,
        bot=getattr(discord_user, 'bot', False),
        system=getattr(discord_user, 'system', False)
    )

def discord_channel_to_channel(discord_channel) -> Channel:
    """Convert discord.py Channel to API Channel model."""
    return Channel(
        id=discord_channel.id,
        type=ChannelType(discord_channel.type.name),
        name=getattr(discord_channel, 'name', None),
        position=getattr(discord_channel, 'position', None),
        guild_id=getattr(discord_channel, 'guild', None).id if hasattr(discord_channel, 'guild') and discord_channel.guild else None
    )

def discord_message_to_message(discord_message) -> Message:
    """Convert discord.py Message to API Message model."""
    return Message(
        id=discord_message.id,
        channel_id=discord_message.channel.id,
        author=discord_user_to_user(discord_message.author),
        content=discord_message.content,
        timestamp=discord_message.created_at,
        edited_timestamp=discord_message.edited_at,
        tts=discord_message.tts,
        mention_everyone=discord_message.mention_everyone,
        type=MessageType(str(discord_message.type))
    )
