# Screenshot MCP Server Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an MCP server that lists running windows and captures screenshots on Arch Linux KDE Plasma 6 (X11 and Wayland).

**Architecture:** Python MCP server using stdio transport. Platform abstraction layer for X11 vs Wayland screenshot tools.

**Tech Stack:** Python 3, `mcp` library, `xdotool`/`import` (X11), `grim`/`kwinmsg` (Wayland)

---

## File Structure

```
screenshot_mcp/
├── src/screenshot_mcp/
│   ├── __init__.py
│   ├── server.py              # MCP server + tool handlers
│   ├── platform/
│   │   ├── __init__.py
│   │   ├── base.py            # WindowCapture ABC
│   │   ├── x11.py             # X11 implementation
│   │   └── wayland.py         # Wayland/KDE implementation
│   └── utils.py               # Platform detection, temp file
├── tests/
│   ├── __init__.py
│   ├── test_platform_detection.py
│   ├── test_x11.py
│   └── test_wayland.py
├── pyproject.toml
└── requirements.txt
```

---

## Task 1: Project Setup

**Files:**
- Create: `pyproject.toml`
- Create: `requirements.txt`
- Create: `src/screenshot_mcp/__init__.py`
- Create: `src/screenshot_mcp/platform/__init__.py`

- [ ] **Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "screenshot-mcp"
version = "0.1.0"
description = "MCP server for screenshots on Linux"
requires-python = ">=3.10"
dependencies = [
    "mcp>=1.0.0",
]

[project.scripts]
screenshot-mcp = "screenshot_mcp.server:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create requirements.txt**

```
mcp>=1.0.0
```

- [ ] **Step 3: Create __init__.py files (empty)**

```python
# src/screenshot_mcp/__init__.py
# src/screenshot_mcp/platform/__init__.py
```

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml requirements.txt src/
git commit -m "feat: project setup"
```

---

## Task 2: Platform Abstraction Base

**Files:**
- Create: `src/screenshot_mcp/platform/base.py`
- Create: `src/screenshot_mcp/utils.py`

- [ ] **Step 1: Write failing test for platform detection**

```python
# tests/test_platform_detection.py
import os
from screenshot_mcp.utils import detect_platform

def test_detect_x11():
    os.environ.pop('WAYLAND_DISPLAY', None)
    os.environ['DISPLAY'] = ':0'
    assert detect_platform() == 'x11'

def test_detect_wayland():
    os.environ['WAYLAND_DISPLAY'] = 'wayland-0'
    os.environ.pop('DISPLAY', None)
    assert detect_platform() == 'wayland'
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_platform_detection.py -v`
Expected: FAIL with "detect_platform not defined"

- [ ] **Step 3: Write platform detection in utils.py**

```python
# src/screenshot_mcp/utils.py
from enum import Enum

class Platform(Enum):
    X11 = "x11"
    WAYLAND = "wayland"

def detect_platform() -> str:
    wayland = os.environ.get('WAYLAND_DISPLAY')
    x11 = os.environ.get('DISPLAY')
    if wayland:
        return "wayland"
    elif x11:
        return "x11"
    return "x11"  # default assumption
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_platform_detection.py -v`
Expected: PASS

- [ ] **Step 5: Write base abstract class**

```python
# src/screenshot_mcp/platform/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class WindowInfo:
    id: str
    title: str
    pid: int
    is_active: bool

class WindowCapture(ABC):
    @abstractmethod
    def list_windows(self) -> list[WindowInfo]:
        pass

    @abstractmethod
    def capture_window(self, window_id: str) -> str:
        """Capture window, return path to screenshot file."""
        pass
```

- [ ] **Step 6: Commit**

```bash
git add tests/test_platform_detection.py src/screenshot_mcp/utils.py src/screenshot_mcp/platform/base.py
git commit -m "feat: platform abstraction base"
```

---

## Task 3: X11 Implementation

**Files:**
- Create: `src/screenshot_mcp/platform/x11.py`
- Create: `tests/test_x11.py`

- [ ] **Step 1: Write failing test for X11 list_windows**

```python
# tests/test_x11.py
from screenshot_mcp.platform.x11 import X11Capture

def test_list_windows_parses_xdotool_output():
    capture = X11Capture()
    # Mock subprocess to return xdotool output
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_x11.py -v`
Expected: FAIL

- [ ] **Step 3: Write X11 implementation with error handling**

```python
# src/screenshot_mcp/platform/x11.py
import subprocess
from screenshot_mcp.platform.base import WindowCapture, WindowInfo
from screenshot_mcp.utils import get_temp_path

class X11Capture(WindowCapture):
    def list_windows(self) -> list[WindowInfo]:
        result = subprocess.run(
            ['xdotool', 'search', '--onlyvisible', '--name', '.'],
            capture_output=True, text=True
        )
        window_ids = result.stdout.strip().split('\n')
        windows = []
        active_win = subprocess.run(
            ['xdotool', 'getactivewindow'],
            capture_output=True, text=True
        ).stdout.strip()
        
        for wid in window_ids:
            if not wid:
                continue
            title_result = subprocess.run(
                ['xdotool', 'getwindowname', wid],
                capture_output=True, text=True
            )
            pid_result = subprocess.run(
                ['xdotool', 'getwindowpid', wid],
                capture_output=True, text=True
            )
            windows.append(WindowInfo(
                id=wid,
                title=title_result.stdout.strip(),
                pid=int(pid_result.stdout.strip()) if pid_result.stdout.strip().isdigit() else 0,
                is_active=(wid == active_win)
            ))
        return windows

    def capture_window(self, window_id: str) -> str:
        temp_path = get_temp_path()
        result = subprocess.run(
            ['import', '-window', window_id, temp_path],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            if result.returncode == 127:
                raise FileNotFoundError("import command not found (imagemagick not installed)")
            raise subprocess.CalledProcessError(result.returncode, 'import', result.stderr)
        return temp_path
```

- [ ] **Step 4: Add tests for capture_window**

```python
# tests/test_x11.py
from screenshot_mcp.platform.x11 import X11Capture
from unittest.mock import patch, MagicMock

def test_capture_window_success():
    capture = X11Capture()
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        path = capture.capture_window('12345')
        assert path.startswith('/tmp/screenshot_mcp_')
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == 'import'
        assert args[1] == '-window'
        assert args[2] == '12345'

def test_capture_window_missing_tool():
    capture = X11Capture()
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=127)
        try:
            capture.capture_window('12345')
            assert False, "Should raise FileNotFoundError"
        except FileNotFoundError:
            pass  # Expected
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_x11.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/screenshot_mcp/platform/x11.py tests/test_x11.py
git commit -m "feat: X11 window capture implementation"
```

---

## Task 4: Wayland Implementation

**Files:**
- Create: `src/screenshot_mcp/platform/wayland.py`
- Create: `tests/test_wayland.py`

- [ ] **Step 1: Write failing test for Wayland list_windows**

```python
# tests/test_wayland.py
from screenshot_mcp.platform.wayland import WaylandCapture
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_wayland.py -v`
Expected: FAIL

- [ ] **Step 3: Write Wayland implementation using qdbus/grim**

```python
# src/screenshot_mcp/platform/wayland.py
import json
import subprocess
from screenshot_mcp.platform.base import WindowCapture, WindowInfo
from screenshot_mcp.utils import get_temp_path

class WaylandCapture(WindowCapture):
    def list_windows(self) -> list[WindowInfo]:
        # Use qdbus to query KWin for window list
        result = subprocess.run(
            ['qdbus', 'org.kde.KWin', '/KWin', 'org.kde.KWin.WindowManager'],
            capture_output=True, text=True
        )
        windows = []
        # Parse KWin window info - get active window via qdbus
        active_result = subprocess.run(
            ['qdbus', 'org.kde.KWin', '/KWin', 'org.kde.KWin.WindowManager', 'activeWindow'],
            capture_output=True, text=True
        )
        active_id = active_result.stdout.strip()
        
        # Get window list via KWin scripting interface
        script = '''
        var windows = [];
        var clients = KWin.windowList();
        for (var i = 0; i < clients.length; i++) {
            var c = clients[i];
            windows.push({
                id: c.windowId,
                title: c.caption,
                pid: c.pid,
                is_active: c.windowId == activeWindow
            });
        }
        JSON.stringify(windows);
        '''
        result = subprocess.run(
            ['qdbus', 'org.kde.KWin', '/KWin', 'org.kde.KWin.Scripting', 'evaluateScript', script],
            capture_output=True, text=True
        )
        if result.stdout.strip():
            windows_data = json.loads(result.stdout.strip())
            return [WindowInfo(**w) for w in windows_data]
        
        # Fallback using xdotool if available (some KDE setups)
        try:
            xdotool_result = subprocess.run(
                ['xdotool', 'search', '--onlyvisible', '--name', '.'],
                capture_output=True, text=True
            )
            if xdotool_result.returncode == 0:
                window_ids = xdotool_result.stdout.strip().split('\n')
                for wid in window_ids:
                    if not wid:
                        continue
                    title_result = subprocess.run(
                        ['xdotool', 'getwindowname', wid],
                        capture_output=True, text=True
                    )
                    pid_result = subprocess.run(
                        ['xdotool', 'getwindowpid', wid],
                        capture_output=True, text=True
                    )
                    windows.append(WindowInfo(
                        id=wid,
                        title=title_result.stdout.strip(),
                        pid=int(pid_result.stdout.strip()) if pid_result.stdout.strip().isdigit() else 0,
                        is_active=(wid == active_id)
                    ))
        except FileNotFoundError:
            pass
        return windows
    
    def capture_window(self, window_id: str) -> str:
        temp_path = get_temp_path()
        # For Wayland, get window geometry via KWin then grim
        subprocess.run(
            ['grim', '-g', f'@{window_id}', temp_path],
            check=True
        )
        return temp_path
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_wayland.py -v`
Expected: PASS

- [ ] **Step 5: Add tests for capture_window**

```python
# tests/test_wayland.py
from screenshot_mcp.platform.wayland import WaylandCapture
from unittest.mock import patch, MagicMock

def test_capture_window_success():
    capture = WaylandCapture()
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        path = capture.capture_window('12345')
        assert path.startswith('/tmp/screenshot_mcp_')
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == 'grim'
        assert '-g' in args
        assert '@12345' in args

def test_capture_window_missing_tool():
    capture = WaylandCapture()
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=127)
        try:
            capture.capture_window('12345')
            assert False, "Should raise FileNotFoundError"
        except FileNotFoundError:
            pass  # Expected
```

- [ ] **Step 6: Commit**

```bash
git add src/screenshot_mcp/platform/wayland.py tests/test_wayland.py
git commit -m "feat: Wayland window capture implementation"
```

---

## Task 5: MCP Server

**Files:**
- Create: `src/screenshot_mcp/server.py`

- [ ] **Step 1: Write failing test for server**

```python
# tests/test_server.py
from screenshot_mcp.server import create_server

def test_server_has_list_windows_tool():
    server = create_server()
    tools = server.tool_manager.list_tools()
    assert 'list_windows' in [t.name for t in tools]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_server.py -v`
Expected: FAIL

- [ ] **Step 3: Write MCP server**

```python
# src/screenshot_mcp/server.py
import json
import subprocess
from mcp.server import Server
from mcp.types import Tool, TextContent
from screenshot_mcp.platform.x11 import X11Capture
from screenshot_mcp.platform.wayland import WaylandCapture
from screenshot_mcp.utils import detect_platform

app = Server("screenshot-mcp")

def get_capture():
    platform = detect_platform()
    if platform == "wayland":
        return WaylandCapture()
    return X11Capture()

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="list_windows",
            description="List all visible application windows",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="capture_window",
            description="Capture a screenshot of the specified window",
            inputSchema={
                "type": "object",
                "properties": {
                    "window_id": {
                        "type": "string",
                        "description": "The window ID to capture"
                    }
                },
                "required": ["window_id"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    capture = get_capture()
    
    if name == "list_windows":
        try:
            windows = capture.list_windows()
            return [TextContent(type="text", text=json.dumps([w.__dict__ for w in windows]))]
        except FileNotFoundError as e:
            return [TextContent(type="text", text=json.dumps({
                "error": "Screenshot tool not installed",
                "install_hint": f"sudo pacman -S {'imagemagick' if detect_platform() == 'x11' else 'grim'}",
                "details": str(e)
            }))]
    
    elif name == "capture_window":
        window_id = arguments.get("window_id")
        if not window_id:
            return [TextContent(type="text", text=json.dumps({
                "error": "window_id is required"
            }))]
        try:
            path = capture.capture_window(window_id)
            return [TextContent(type="text", text=json.dumps({"path": path, "success": True}))]
        except subprocess.CalledProcessError as e:
            if e.returncode == 127:
                return [TextContent(type="text", text=json.dumps({
                    "error": "Screenshot tool not installed",
                    "install_hint": f"sudo pacman -S {'imagemagick' if detect_platform() == 'x11' else 'grim'}"
                }))]
            return [TextContent(type="text", text=json.dumps({
                "error": "Failed to capture window",
                "window_id": window_id,
                "hint": "Check window permissions"
            }))]
        except ValueError as e:
            return [TextContent(type="text", text=json.dumps({
                "error": "Window not found",
                "window_id": window_id
            }))]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_server.py -v`
Expected: PASS

- [ ] **Step 5: Add main entry point**

```python
# Add to server.py
def main():
    app.run(transport="stdio")
```

- [ ] **Step 6: Commit**

```bash
git add src/screenshot_mcp/server.py tests/test_server.py
git commit -m "feat: MCP server with list_windows and capture_window tools"
```

---

## Task 6: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write README with installation instructions**

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README"
```

---

## Plan Review

After saving, dispatch plan-document-reviewer subagent for review.
