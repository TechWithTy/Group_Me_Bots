# Discord API

This module provides a FastAPI-based API for interacting with Discord using the discord.py library.

## Setup

1. Install dependencies:
   ```bash
   pip install fastapi discord.py uvicorn pydantic
   ```

2. Set environment variable:
   ```bash
   export DISCORD_BOT_TOKEN="your_bot_token_here"
   ```

3. Run the API server:
   ```bash
   uvicorn app.discord.api:app --reload
   ```

## Endpoints

### GET /
Returns API status.

**Response:**
```json
{"message": "Discord API is running"}
```

### GET /channels/{channel_id}
Get information about a specific channel.

**Parameters:**
- `channel_id` (int): The ID of the channel

**Response:**
```json
{
  "id": 12345,
  "name": "general",
  "type": "text"
}
```

### GET /channels?guild_id={guild_id}
List all channels in a guild.

**Parameters:**
- `guild_id` (int): The ID of the guild

**Response:**
```json
[
  {
    "id": 12345,
    "name": "general",
    "type": "text"
  }
]
```

### POST /messages
Send a message to a channel.

**Request:**
```json
{
  "channel_id": 12345,
  "content": "Hello, world!"
}
```

**Response:**
```json
{
  "id": 67890,
  "content": "Hello, world!",
  "author": "BotName",
  "channel_id": 12345
}
```

### GET /messages/{channel_id}?limit={limit}
Get recent messages from a channel.

**Parameters:**
- `channel_id` (int): The ID of the channel
- `limit` (int, optional): Number of messages to retrieve (default: 10)

**Response:**
```json
[
  {
    "id": 67890,
    "content": "Hello!",
    "author": "UserName",
    "channel_id": 12345
  }
]
```

## Error Handling

- 404: Resource not found (channel, guild)
- 500: Internal server error

## Development

Run tests:
```bash
pytest app/discord/tests/
```
