# Signal MCP

An MCP integration for signal-cli that allows AI agents to send and receive Signal messages.

## Features
- Send messages to Signal users
- Send messages to Signal groups
- Receive and parse incoming messages
- Async support with timeout handling
- Detailed logging

## Prerequisites
This project requires signal-cli to be installed and configured on your system.

### Installing signal-cli
1. Install signal-cli: Follow the official installation instructions at [signal-cli GitHub](https://github.com/AsamK/signal-cli).
2. Register your Signal account:
   ```
   signal-cli -u YOUR_PHONE_NUMBER register
   ```
3. Verify your account with the code received via SMS:
   ```
   signal-cli -u YOUR_PHONE_NUMBER verify CODE_RECEIVED
   ```
   For more detailed setup instructions, see the [signal-cli documentation](https://github.com/AsamK/signal-cli/wiki).

## Installation
```bash
pip install -e .
# or use uv for faster installation
uv pip install -e .
```

## Usage
Run the MCP server:
```bash
./main.py --user-id YOUR_PHONE_NUMBER [--transport {sse|stdio}]
```

## API
### Tools Available
- `send_message_to_user`: Send a direct message to a Signal user
- `send_message_to_group`: Send a message to a Signal group
- `receive_message`: Wait for and receive messages with timeout support

## Development
This project uses:
- MCP for agent-API integration
- Modern Python async patterns
- Type annotations throughout

For more details, refer to the [repository](https://github.com/rymurr/signal-mcp).
