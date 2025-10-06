# NiceGUI Operations Dashboard - Getting Started

## Overview

The NiceGUI Operations Dashboard is a web-based interface for managing bots and operations within the Group_Me_Bots system. Built with [NiceGUI](https://nicegui.io/) (v1.4.20), it provides a modern, responsive UI for coordinating profiles, settings, automations, and credits.

## Prerequisites

### System Requirements
- **Python**: 3.12 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: At least 512MB RAM
- **Storage**: 100MB free space
- **Network**: Internet connection for initial setup

### Required Dependencies
The application depends on several Python packages. All dependencies are automatically installed when following the installation steps below.

## Installation

### 1. Navigate to the Project Directory
```bash
cd /path/to/Group_Me_Bots
```

### 2. Install Dependencies
The project uses `uv` for dependency management. Install all required packages:

```bash
# If you don't have uv installed, install it first:
pip install uv

# Install project dependencies
uv sync
```

Alternatively, you can use pip:
```bash
pip install -r requirements.txt
```

### 3. Verify Installation
Check that NiceGUI and other dependencies are properly installed:

```bash
python -c "import nicegui; print(f'NiceGUI version: {nicegui.__version__}')"
```

## Configuration

### Environment Variables

The application supports the following environment variables for configuration:

| Variable | Default | Description |
|----------|---------|-------------|
| `NICEGUI_PORT` | `8081` | Port number for the web server |
| `NICEGUI_HOST` | `127.0.0.1` | Host address to bind the server |

### Configuration Files

- **`pyproject.toml`**: Contains project metadata and dependencies
- **`nice-gui/main.py`**: Main application entry point
- **`nice-gui/app/`**: Application modules and components

## Running the Application

### Development Mode

To start the application in development mode:

```bash
cd nice-gui
python main.py
```

The application will start and be accessible at `http://127.0.0.1:8081` (or your configured host/port).

### Production Mode

For production deployment, use the following command:

```bash
cd nice-gui
NICEGUI_HOST=0.0.0.0 NICEGUI_PORT=8080 python main.py
```

This binds the server to all network interfaces on port 8080.

### Docker Deployment

You can also run the application using Docker:

```bash
# Build the image
docker build -t group-me-bots-nicegui .

# Run the container
docker run -p 8081:8081 group-me-bots-nicegui
```

## Application Features

Once running, the Operations Dashboard provides:

- **Bot Management**: View and manage connected bots
- **Authentication Panel**: User authentication controls
- **Profile Management**: User profile settings
- **Activity Log**: System activity monitoring
- **Settings Panel**: Application configuration
- **Credit Summary**: Credit usage tracking
- **Role-based Views**: Switch between User and Admin perspectives

### Role Management

The dashboard supports two viewing modes:
- **User Mode**: Standard operational view
- **Admin Mode**: Extended administrative controls

Click the "View as User" or "View as Admin" buttons to switch between modes.

## Development

### Project Structure

```
nice-gui/
├── main.py              # Application entry point
├── app/
│   ├── __init__.py      # Application bootstrap
│   ├── build.py         # UI construction (referenced but not found)
│   ├── components/      # Reusable UI components
│   ├── controllers.py   # Request handlers
│   ├── factories.py     # Component factories
│   ├── models/          # Data models
│   ├── pages/           # Page definitions
│   ├── services/        # Business logic
│   └── state.py         # Application state management
├── nicegui/             # Local NiceGUI modules
├── tests/               # Test files
└── _docs/               # This documentation
```

### Adding New Components

To add new dashboard components:

1. Create the component in `app/components/`
2. Import and use it in `app/pages/dashboard.py`
3. Update the `render_dashboard()` function to include the new component

### Code Quality

The project follows these coding standards:
- **Type Hints**: All functions should have proper type annotations
- **Documentation**: Functions should have docstrings
- **File Size**: Keep files under 250 lines when possible
- **Imports**: Standard library imports first, then third-party, then local

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using the port
netstat -ano | findstr :8081

# Use a different port
NICEGUI_PORT=8082 python main.py
```

#### Import Errors
```bash
# Ensure you're in the correct directory
cd /path/to/Group_Me_Bots

# Reinstall dependencies
pip install -r requirements.txt
```

#### Permission Errors (Linux/macOS)
```bash
# Use a port number above 1024
NICEGUI_PORT=8080 python main.py

# Or run with sudo (not recommended)
sudo python main.py
```

#### Module Not Found Errors
```bash
# Install missing modules
pip install nicegui==1.4.20

# Or update all dependencies
pip install -r requirements.txt --upgrade
```

### Logs and Debugging

The application logs to the console. To enable more detailed logging:

```python
import logging

# Add this before running the app
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

1. Check the [NiceGUI documentation](https://nicegui.io/documentation)
2. Review the existing code in `app/components/`
3. Check the test files in `tests/`
4. Look at the example code in `nice_to_know.md`

## API Reference

The application also exposes a REST API for programmatic control:

- **Base URL**: `http://localhost:8081/api/v1`
- **Components**: Manage UI elements dynamically
- **Actions**: Trigger notifications and JavaScript execution
- **App State**: Control global application settings

See `spec.yaml` for the complete OpenAPI specification.

## Performance Considerations

- **Memory Usage**: The application uses approximately 50-100MB of RAM
- **CPU Usage**: Minimal CPU usage during normal operation
- **Network**: WebSocket connections for real-time updates
- **Storage**: No persistent storage requirements

## Security Notes

- The application is designed for internal use
- No authentication is implemented by default
- Consider implementing proper authentication for production use
- The server binds to localhost by default for security

## Support

For issues specific to this Operations Dashboard:
1. Check the troubleshooting section above
2. Review the existing components for similar functionality
3. Consult the NiceGUI documentation for UI-related issues
4. Check the project repository for updates and issues
