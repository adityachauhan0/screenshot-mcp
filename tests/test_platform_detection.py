import os
import pytest
from screenshot_mcp.utils import detect_platform, Platform


@pytest.fixture(autouse=True)
def clean_env():
    """Clean environment before and after each test."""
    orig_display = os.environ.get("DISPLAY")
    orig_wayland = os.environ.get("WAYLAND_DISPLAY")
    yield
    # Restore
    if orig_display is not None:
        os.environ["DISPLAY"] = orig_display
    elif "DISPLAY" in os.environ:
        del os.environ["DISPLAY"]
    if orig_wayland is not None:
        os.environ["WAYLAND_DISPLAY"] = orig_wayland
    elif "WAYLAND_DISPLAY" in os.environ:
        del os.environ["WAYLAND_DISPLAY"]


def test_detect_x11(clean_env):
    os.environ["DISPLAY"] = ":0"
    os.environ.pop("WAYLAND_DISPLAY", None)
    assert detect_platform() == Platform.X11


def test_detect_wayland(clean_env):
    os.environ["WAYLAND_DISPLAY"] = "wayland-0"
    os.environ.pop("DISPLAY", None)
    assert detect_platform() == Platform.WAYLAND


def test_detect_default(clean_env):
    os.environ.pop("DISPLAY", None)
    os.environ.pop("WAYLAND_DISPLAY", None)
    assert detect_platform() == Platform.X11


def test_get_temp_path():
    from screenshot_mcp.utils import get_temp_path

    path = get_temp_path()
    assert path.startswith("/tmp/screenshot_mcp_")
    assert path.endswith(".png")
