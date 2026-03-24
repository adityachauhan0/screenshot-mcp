# Screenshot MCP Server - Design Specification

## Overview

An MCP server that enables AI agents to list running application windows and capture screenshots of specific windows on Arch Linux KDE Plasma 6.

## Architecture

- **Transport**: stdio (standard MCP protocol over stdin/stdout)
- **Language**: Python 3
- **Platform Detection**: Auto-detects X11 vs Wayland session on startup

## Tools

### `list_windows`
Returns all visible application windows.

**Output Schema:**
```json
{
  "windows": [
    {
      "id": "string (platform-specific window ID)",
      "title": "string (window title)",
      "pid": "integer (process ID)",
      "is_active": "boolean (currently focused window)"
    }
  ]
}
```

**X11 Implementation**: `xdotool search --onlyvisible --name .`
**Wayland Implementation**: `kwinmsg --rectify` or `qdbus` to query KWin

### `capture_window`
Captures a screenshot of the specified window.

**Input:**
- `window_id` (string, required): Platform-specific window identifier

**Output Schema:**
```json
{
  "path": "/tmp/screenshot_mcp_<timestamp>.png",
  "success": true
}
```

**X11 Implementation**: `xwd -id <window_id> | convert png:-`
**Wayland Implementation**: `grim -g "$(kwinmsg ...)" -`

## Platform Detection

On startup, detect session type:
```python
import os
session_type = os.environ.get('XDG_SESSION_TYPE', 'x11')
```

Fallback: Check if `DISPLAY` env var is set (X11) vs `WAYLAND_DISPLAY` (Wayland).

## Screenshot Flow

1. Agent calls `list_windows` → receives window list
2. Agent calls `capture_window(window_id="...")`
3. Server captures window to temp file: `/tmp/screenshot_mcp_<timestamp>.png`
4. Server returns absolute file path

## Error Handling

| Error | Response |
|-------|----------|
| Invalid window ID | `{"error": "Window not found", "window_id": "..."}` |
| Screenshot tool missing | `{"error": "Screenshot tool not installed", "install_hint": "sudo pacman -S imagemagick"}` |
| Permission denied | `{"error": "Permission denied", "hint": "Check window permissions"}` |

## Dependencies

### X11
- `xdotool` - Window listing
- `imagemagick` - Screenshot capture (`import` command)

### Wayland
- `kwinmsg` or `qdbus` - Window listing (KDE KWin integration)
- `grim` - Screenshot capture (or KDE's `spectacle`)

## File Structure

```
screenshot_mcp/
├── docs/
│   └── specs/
│       └── 2026-03-25-screenshot-mcp-design.md
├── src/
│   └── screenshot_mcp/
│       ├── __init__.py
│       ├── server.py          # MCP server implementation
│       ├── platform/
│       │   ├── __init__.py
│       │   ├── base.py        # Abstract base class
│       │   ├── x11.py         # X11 implementation
│       │   └── wayland.py     # Wayland/KDE implementation
│       └── utils.py           # Shared utilities
├── pyproject.toml
├── README.md
└── requirements.txt
```

## Configuration

- Temp directory: `/tmp` (default, no configuration needed)
- Screenshot format: PNG (lossless, widely compatible)

## Testing

- Unit tests for platform detection
- Integration tests for each tool (mock shell commands)
- Mock window enumeration for CI
