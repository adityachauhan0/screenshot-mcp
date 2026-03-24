import subprocess
from screenshot_mcp.platform.x11 import X11Capture
from unittest.mock import patch, MagicMock


def test_list_windows_parses_xdotool_output():
    """Test that list_windows correctly parses xdotool output."""
    capture = X11Capture()
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = [
            MagicMock(stdout="12345\n67890", returncode=0),  # search
            MagicMock(stdout="67890", returncode=0),  # getactivewindow
            MagicMock(stdout="Window 1", returncode=0),  # getwindowname 12345
            MagicMock(stdout="1111", returncode=0),  # getwindowpid 12345
            MagicMock(stdout="Window 2", returncode=0),  # getwindowname 67890
            MagicMock(stdout="2222", returncode=0),  # getwindowpid 67890
        ]
        windows = capture.list_windows()
        assert len(windows) == 2
        assert windows[0].id == "12345"
        assert windows[0].title == "Window 1"
        assert windows[0].pid == 1111
        assert windows[0].is_active == False
        assert windows[1].id == "67890"
        assert windows[1].is_active == True  # active window


def test_capture_window_success():
    capture = X11Capture()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        path = capture.capture_window("12345")
        assert path.startswith("/tmp/screenshot_mcp_")
        assert path.endswith(".png")
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "import"
        assert args[1] == "-window"
        assert args[2] == "12345"


def test_capture_window_missing_tool():
    capture = X11Capture()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=127)  # command not found
        try:
            capture.capture_window("12345")
            assert False, "Should raise FileNotFoundError"
        except FileNotFoundError as e:
            assert "imagemagick not installed" in str(e)


def test_capture_window_failure():
    """Test that capture_window raises CalledProcessError on non-127 failures."""
    capture = X11Capture()
    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock(returncode=1, stderr="Unknown error")
        mock_run.return_value = mock_result
        try:
            capture.capture_window("12345")
            assert False, "Should raise CalledProcessError"
        except subprocess.CalledProcessError as e:
            assert e.returncode == 1
