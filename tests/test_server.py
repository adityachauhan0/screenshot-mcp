import json
import pytest
from unittest.mock import patch, MagicMock
from screenshot_mcp.server import get_capture, app
from screenshot_mcp.platform.base import WindowInfo


def test_server_has_list_windows_tool():
    """Test that list_windows tool is registered."""
    tools = app.list_tools()
    tool_names = [t.name for t in tools]
    assert "list_windows" in tool_names


def test_server_has_capture_window_tool():
    """Test that capture_window tool is registered."""
    tools = app.list_tools()
    tool_names = [t.name for t in tools]
    assert "capture_window" in tool_names


@pytest.mark.asyncio
async def test_list_windows_returns_json():
    """Test that list_windows returns properly formatted JSON."""
    windows = [WindowInfo(id="123", title="Test", pid=100, is_active=True)]
    with patch("screenshot_mcp.server.get_capture") as mock_get_capture:
        mock_capture = MagicMock()
        mock_capture.list_windows.return_value = windows
        mock_get_capture.return_value = mock_capture

        from screenshot_mcp.server import call_tool

        result = await call_tool("list_windows", {})
        assert len(result) == 1
        data = json.loads(result[0].text)
        assert len(data) == 1
        assert data[0]["id"] == "123"


@pytest.mark.asyncio
async def test_capture_window_returns_path():
    """Test that capture_window returns path on success."""
    with patch("screenshot_mcp.server.get_capture") as mock_get_capture:
        mock_capture = MagicMock()
        mock_capture.capture_window.return_value = "/tmp/screenshot_mcp_test.png"
        mock_get_capture.return_value = mock_capture

        from screenshot_mcp.server import call_tool

        result = await call_tool("capture_window", {"window_id": "123"})
        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["success"] == True
        assert "path" in data


@pytest.mark.asyncio
async def test_capture_window_requires_window_id():
    """Test that capture_window returns error when window_id is missing."""
    from screenshot_mcp.server import call_tool

    result = await call_tool("capture_window", {})
    data = json.loads(result[0].text)
    assert "error" in data
    assert "window_id is required" in data["error"]


@pytest.mark.asyncio
async def test_list_windows_handles_file_not_found():
    """Test that list_windows handles missing tool gracefully."""
    with patch("screenshot_mcp.server.get_capture") as mock_get_capture:
        mock_capture = MagicMock()
        mock_capture.list_windows.side_effect = FileNotFoundError("xdotool not found")
        mock_get_capture.return_value = mock_capture

        from screenshot_mcp.server import call_tool

        result = await call_tool("list_windows", {})
        data = json.loads(result[0].text)
        assert "error" in data
        assert "not installed" in data["error"]


@pytest.mark.asyncio
async def test_capture_window_handles_called_process_error():
    """Test that capture_window handles subprocess errors gracefully."""
    with patch("screenshot_mcp.server.get_capture") as mock_get_capture:
        mock_capture = MagicMock()
        import subprocess

        mock_capture.capture_window.side_effect = subprocess.CalledProcessError(
            1, "import", stderr="error"
        )
        mock_get_capture.return_value = mock_capture

        from screenshot_mcp.server import call_tool

        result = await call_tool("capture_window", {"window_id": "123"})
        data = json.loads(result[0].text)
        assert "error" in data
        assert "Failed to capture window" in data["error"]
