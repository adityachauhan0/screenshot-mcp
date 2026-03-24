import os
from enum import Enum
from datetime import datetime


class Platform(Enum):
    X11 = "x11"
    WAYLAND = "wayland"


def detect_platform() -> Platform:
    wayland = os.environ.get("WAYLAND_DISPLAY")
    x11 = os.environ.get("DISPLAY")
    if wayland:
        return Platform.WAYLAND
    elif x11:
        return Platform.X11
    return Platform.X11  # default assumption


def get_temp_path() -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"/tmp/screenshot_mcp_{timestamp}.png"
