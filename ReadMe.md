# 🤖 Multi-Platform Bot System

A comprehensive Python-based bot system supporting multiple messaging platforms including **Discord**, **GroupMe**, **Signal**, and **Telegram**. Features advanced workflow automation, API integrations, and intelligent message processing.

## 🌟 Features

### Multi-Platform Support
- **Discord Bots** - Advanced Discord bot with workflow automation
- **GroupMe Bots** - Original GroupMe bot functionality with scheduling
- **Signal Bots** - Signal messaging bot with API integration
- **Telegram Bots** - Telegram bot with comprehensive API support

### Advanced Workflows
- Message stitching and content echoing across groups
- Automated engagement and feedback systems
- Content quality assessment and moderation
- Emergency response handling
- Security monitoring and violation detection

### API Integrations
- **RESTful APIs** - Complete API implementations for all platforms
- **Modular Architecture** - Separate API modules for each platform
- **Signal API** - Full Signal REST API implementation
- **Error Handling** - Comprehensive error handling and logging

### Development Tools
- **UV Package Manager** - Fast Python dependency management
- **Testing Framework** - Comprehensive test suites
- **Code Quality** - Linting and formatting with Ruff and Biome
- **Type Safety** - Full type annotations with Pydantic models

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- UV package manager

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Group_Me_Bots
```

2. **Install dependencies with UV**
```bash
uv sync
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

4. **Run the application**
```bash
uv run python main.py
```

## 📦 Package Management with UV

This project uses [UV](https://github.com/astral-sh/uv) for fast and reliable Python package management:

```bash
# Install dependencies
uv sync

# Add new dependencies
uv add package-name

# Run with UV
uv run python script.py

# Enter UV shell
uv shell
```

## 🏗️ Project Structure

```
Group_Me_Bots/
├── app/                          # Main application modules
│   ├── discord/                  # Discord bot implementation
│   │   ├── api/                  # Discord API routes
│   │   ├── workflows/            # Discord workflow definitions
│   │   └── workers/              # Discord background workers
│   ├── group_me/                 # GroupMe bot implementation
│   │   ├── api/                  # GroupMe API routes
│   │   └── workers/              # GroupMe background workers
│   ├── signal/                   # Signal bot implementation
│   │   ├── api/                  # Signal API routes
│   │   ├── workflows/            # Signal workflow definitions
│   │   └── workers/              # Signal background workers
│   ├── telegram/                 # Telegram bot implementation
│   │   ├── api/                  # Telegram API routes
│   │   └── core/                 # Telegram core functionality
│   └── models.py                 # Shared data models
├── _docs/                        # Documentation
│   ├── platforms/                # Platform-specific docs
│   └── callbacks/                # API callback documentation
├── _schema/                      # Schema definitions
├── tests/                        # Test suites
├── requirements.txt              # Legacy requirements file
├── pyproject.toml               # UV project configuration
└── uv.lock                      # UV lock file
```

## 🎯 Platform-Specific Features

### Discord Bot
- Advanced workflow automation
- Message stitching across servers
- Engagement tracking and analytics
- Custom command handling

### GroupMe Bot
- Scheduled message posting
- Group management automation
- Push notification integration
- Error handling with retry logic

### Signal Bot
- Complete Signal REST API implementation
- Message encryption/decryption
- Group management
- Contact synchronization
- Device linking support

### Telegram Bot
- Bot API integration
- Inline keyboards and callbacks
- Media handling
- Channel management

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# General Settings
DEBUG=true
LOG_LEVEL=INFO

# Platform API Keys
DISCORD_TOKEN=your_discord_bot_token
GROUP_ME_TOKEN=your_groupme_token
SIGNAL_PHONE_NUMBER=your_signal_number
TELEGRAM_BOT_TOKEN=your_telegram_token

# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# Redis (for caching)
REDIS_URL=redis://localhost:6379

# External APIs
PUSHBULLET_API_KEY=your_pushbullet_key
```

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_signal_workflows.py

# Run with coverage
uv run pytest --cov=app
```

## 🔄 Workflows

### Message Stitching Workflow
Amplifies cross-group engagement by echoing high-signal messages across multiple groups.

**KPIs:**
- Qualified messages: ≥5 per run
- Echo success rate: ≥80%

### Auto-Like Feedback Workflow
Closes feedback loops by reacting to high-value messages.

**KPIs:**
- Reaction coverage: ≥80%
- Feedback engagement: ≥70%

### Content Quality Workflow
Assesses and promotes high-quality, relevant content.

**KPIs:**
- Quality detection rate: ≥90%
- Promotion effectiveness: ≥80%

### Emergency Response Workflow
Handles emergency situations with immediate response.

**KPIs:**
- Emergency detection rate: 100%
- Response time: <120 seconds

## 🚨 API Reference

### Signal REST API
Complete implementation of Signal's REST API:

- **Accounts** - PIN management, settings, usernames
- **Groups** - Creation, management, member administration
- **Messages** - Sending, receiving, reactions, receipts
- **Contacts** - Contact management and synchronization
- **Devices** - Registration, linking, device management
- **Attachments** - File handling and storage
- **Search** - Phone number registration checking
- **Profiles** - User profile management
- **Stickers** - Sticker pack management
- **Identities** - Identity verification and trust

## 📊 Monitoring & Observability

- **Structured Logging** - Comprehensive logging with levels
- **Health Checks** - API health monitoring endpoints
- **Metrics Collection** - Performance and usage metrics
- **Error Tracking** - Centralized error handling and reporting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Signal** for their excellent messaging platform and API
- **Discord.py** for the Discord API wrapper
- **Python-Telegram-Bot** for Telegram integration
- **UV** for fast Python package management
- **FastAPI** for the REST API framework

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the documentation in `_docs/` folder
- Review the API documentation in `_docs/platforms/` and `_docs/callbacks/`

---

**Built with ❤️ for the messaging bot community**
