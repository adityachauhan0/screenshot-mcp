# Screenshot MCP Server

MCP server for taking screenshots of running windows on Linux (X11/Wayland).

## Requirements

### X11
- xdotool
- imagemagick

### Wayland
- grim
- KWin (for window listing via qdbus)

## Installation

```bash
pip install -e .
```

## Usage

```bash
screenshot-mcp
```

## Tools

- `list_windows` - Returns list of visible windows
- `capture_window` - Captures screenshot of specified window by ID
