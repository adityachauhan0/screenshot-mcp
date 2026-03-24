import subprocess
from screenshot_mcp.platform.wayland import WaylandCapture
from unittest.mock import patch, MagicMock


def test_list_windows_parses_kwin_output():
    """Test that list_windows correctly parses KWin output via qdbus."""
    capture = WaylandCapture()
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = [
            MagicMock(stdout="67890", returncode=0),  # activeWindow
            MagicMock(
                stdout='[{"id":"12345","title":"Window 1","pid":1111,"is_active":false},{"id":"67890","title":"Window 2","pid":2222,"is_active":true}]',
                returncode=0,
            ),  # evaluateScript
        ]
        windows = capture.list_windows()
        assert len(windows) == 2
        assert windows[0].id == "12345"
        assert windows[0].title == "Window 1"
        assert windows[0].pid == 1111
        assert windows[0].is_active == False
        assert windows[1].id == "67890"
        assert windows[1].is_active == True


def test_list_windows_falls_back_to_xdotool():
    """Test that list_windows falls back to xdotool when KWin fails."""
    capture = WaylandCapture()
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = [
            MagicMock(stdout="", returncode=0),  # activeWindow (empty)
            MagicMock(returncode=1, stdout=""),  # evaluateScript fails
            MagicMock(
                stdout="12345\n67890\n",
                returncode=0,
            ),  # xdotool search
            MagicMock(stdout="Window 1", returncode=0),  # getwindowname
            MagicMock(stdout="1111", returncode=0),  # getwindowpid
            MagicMock(stdout="Window 2", returncode=0),  # getwindowname
            MagicMock(stdout="2222", returncode=0),  # getwindowpid
        ]
        windows = capture.list_windows()
        assert len(windows) == 2
        assert windows[0].id == "12345"
        assert windows[0].title == "Window 1"
        assert windows[0].pid == 1111
        assert windows[1].id == "67890"
        assert windows[1].title == "Window 2"
        assert windows[1].pid == 2222


def test_list_windows_handles_json_decode_error():
    """Test that list_windows falls back to xdotool on JSON decode error."""
    capture = WaylandCapture()
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = [
            MagicMock(stdout="", returncode=0),  # activeWindow
            MagicMock(
                stdout="invalid json", returncode=0
            ),  # evaluateScript returns invalid JSON
            MagicMock(
                stdout="12345\n",
                returncode=0,
            ),  # xdotool search
            MagicMock(stdout="Window 1", returncode=0),  # getwindowname
            MagicMock(stdout="1111", returncode=0),  # getwindowpid
        ]
        windows = capture.list_windows()
        assert len(windows) == 1
        assert windows[0].id == "12345"
        assert windows[0].title == "Window 1"


def test_capture_window_success():
    capture = WaylandCapture()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        path = capture.capture_window("12345")
        assert path.startswith("/tmp/screenshot_mcp_")
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "grim"
        assert "-g" in args
        assert "@12345" in args


def test_capture_window_missing_tool():
    capture = WaylandCapture()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=127)
        try:
            capture.capture_window("12345")
            assert False, "Should raise FileNotFoundError"
        except FileNotFoundError:
            pass


def test_capture_window_failure():
    """Test that capture_window raises CalledProcessError on non-127 failures."""
    capture = WaylandCapture()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stderr="Unknown error")
        try:
            capture.capture_window("12345")
            assert False, "Should raise CalledProcessError"
        except subprocess.CalledProcessError as e:
            assert e.returncode == 1
