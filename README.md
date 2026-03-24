# Screenshot MCP Server

> An MCP (Model Context Protocol) server that enables AI agents to capture screenshots of running application windows on Linux systems. Supports X11 and Wayland/KDE Plasma 6.

[![GitHub stars](https://img.shields.io/github/stars/adityachauhan0/screenshot-mcp)](https://github.com/adityachauhan0/screenshot-mcp/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/adityachauhan0/screenshot-mcp)](https://github.com/adityachauhan0/screenshot-mcp/network)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This MCP server provides AI agents with the ability to list all running application windows and capture screenshots of specific windows. It's designed for use with Claude, Cursor, and other MCP-compatible AI assistants.

**Key Features:**
- Lists all visible application windows with titles and process IDs
- Captures screenshots of any running window by ID
- Automatic platform detection (X11 or Wayland/KDE)
- Returns file paths for easy integration with AI workflows
- Graceful error handling with helpful install hints

## Requirements

### X11 Systems
```bash
# Arch Linux
sudo pacman -S xdotool imagemagick

# Ubuntu/Debian
sudo apt install xdotool imagemagick

# Fedora
sudo dnf install xdotool ImageMagick
```

### Wayland/KDE Plasma Systems
```bash
# Arch Linux
sudo pacman -S grim xdotool  # xdotool for fallback window listing

# Ubuntu/Debian
sudo apt install grim wl-clipboard

# Fedora
sudo dnf install grim
```

### Python
- Python 3.10 or higher
- MCP SDK (`mcp>=1.0.0`)

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/adityachauhan0/screenshot-mcp.git
cd screenshot-mcp

# Install in development mode
pip install -e .

# Or install dependencies only
pip install -r requirements.txt
```

### Configure MCP Client

Add to your MCP client configuration (e.g., Claude Desktop, Cursor):

```json
{
  "mcpServers": {
    "screenshot": {
      "command": "screenshot-mcp"
    }
  }
}
```

## Usage

### Available Tools

#### `list_windows`
Returns a list of all visible application windows.

**Returns:**
```json
{
  "windows": [
    {
      "id": "1234567890",
      "title": "Firefox - MCP Server Documentation",
      "pid": 1234,
      "is_active": true
    }
  ]
}
```

#### `capture_window`
Captures a screenshot of the specified window.

**Input:**
- `window_id` (string, required): The window ID to capture

**Returns:**
```json
{
  "path": "/tmp/screenshot_mcp_20260325_143022.png",
  "success": true
}
```

### Example AI Agent Conversation

```
Agent: List all open windows
User: [
  {id: "12345", title: "Terminal", pid: 1000, is_active: true},
  {id: "67890", title: "Firefox", pid: 2000, is_active: false}
]

Agent: Take a screenshot of the Firefox window
User: {path: "/tmp/screenshot_mcp_20260325_143022.png", success: true}
```

## Platform Detection

The server automatically detects your display server:

| Environment Variable | Platform |
|---------------------|----------|
| `WAYLAND_DISPLAY` set | Wayland/KDE Plasma |
| `DISPLAY` set | X11 |
| Neither set | X11 (default) |

## Error Handling

The server provides clear error messages with install hints:

| Error | Cause | Solution |
|-------|-------|----------|
| "Screenshot tool not installed" | Missing dependency | Run install command for your distro |
| "Window not found" | Invalid window_id | Run `list_windows` to get valid IDs |
| "Permission denied" | Window access issue | Check window permissions |

## Development

```bash
# Clone and setup
git clone https://github.com/adityachauhan0/screenshot-mcp.git
cd screenshot-mcp
pip install -e .

# Run tests
pytest tests/ -v

# Install dev dependencies
pip install pytest pytest-asyncio
```

## Project Structure

```
screenshot_mcp/
├── src/screenshot_mcp/
│   ├── server.py          # MCP server implementation
│   ├── platform/
│   │   ├── base.py       # Abstract base class
│   │   ├── x11.py        # X11 window capture
│   │   └── wayland.py    # Wayland/KDE window capture
│   └── utils.py           # Utilities
├── tests/                 # Unit tests
├── LICENSE
└── README.md
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Related

- [MCP SDK](https://github.com/modelcontextprotocol/sdk) - Official MCP Python SDK
- [xdotool](https://github.com/jordansissel/xdotool) - X11 window tool
- [grim](https://sr.ht/~emersion/grim/) - Wayland screenshot tool
