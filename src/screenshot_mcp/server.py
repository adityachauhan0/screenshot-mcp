import json
import subprocess
from mcp.server import Server
from mcp.types import Tool, TextContent
from screenshot_mcp.platform.x11 import X11Capture
from screenshot_mcp.platform.wayland import WaylandCapture
from screenshot_mcp.utils import detect_platform, Platform

app = Server("screenshot-mcp")

_cached_capture = None
_cached_platform = None


def get_capture():
    global _cached_capture, _cached_platform
    if _cached_capture is None:
        _cached_platform = detect_platform()
        if _cached_platform == Platform.WAYLAND:
            _cached_capture = WaylandCapture()
        else:
            _cached_capture = X11Capture()
    return _cached_capture


def get_platform():
    global _cached_platform
    if _cached_platform is None:
        _cached_platform = detect_platform()
    return _cached_platform


@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="list_windows",
            description="List all visible application windows",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="capture_window",
            description="Capture a screenshot of the specified window",
            inputSchema={
                "type": "object",
                "properties": {
                    "window_id": {
                        "type": "string",
                        "description": "The window ID to capture",
                    }
                },
                "required": ["window_id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    capture = get_capture()
    platform = get_platform()
    install_hint = (
        "sudo pacman -S imagemagick"
        if platform == Platform.X11
        else "sudo pacman -S grim"
    )

    if name == "list_windows":
        try:
            windows = capture.list_windows()
            return [
                TextContent(type="text", text=json.dumps([w.__dict__ for w in windows]))
            ]
        except FileNotFoundError as e:
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "error": "Screenshot tool not installed",
                            "install_hint": install_hint,
                            "details": str(e),
                        }
                    ),
                )
            ]

    elif name == "capture_window":
        window_id = arguments.get("window_id")
        if not window_id:
            return [
                TextContent(
                    type="text", text=json.dumps({"error": "window_id is required"})
                )
            ]
        try:
            path = capture.capture_window(window_id)
            return [
                TextContent(
                    type="text", text=json.dumps({"path": path, "success": True})
                )
            ]
        except subprocess.CalledProcessError as e:
            if e.returncode == 127:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "error": "Screenshot tool not installed",
                                "install_hint": install_hint,
                            }
                        ),
                    )
                ]
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "error": "Failed to capture window",
                            "window_id": window_id,
                            "hint": "Check window permissions",
                        }
                    ),
                )
            ]
        except ValueError as e:
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {"error": "Window not found", "window_id": window_id}
                    ),
                )
            ]


def main():
    app.run(transport="stdio")
