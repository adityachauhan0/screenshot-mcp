import subprocess
from screenshot_mcp.platform.base import WindowCapture, WindowInfo
from screenshot_mcp.utils import get_temp_path


class X11Capture(WindowCapture):
    def list_windows(self) -> list[WindowInfo]:
        try:
            result = subprocess.run(
                ["xdotool", "search", "--onlyvisible", "--name", "."],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise RuntimeError(f"xdotool search failed: {result.stderr}")
        except FileNotFoundError:
            raise FileNotFoundError("xdotool not installed")

        window_ids = result.stdout.strip().split("\n")
        windows = []

        try:
            active_result = subprocess.run(
                ["xdotool", "getactivewindow"], capture_output=True, text=True
            )
            active_win = active_result.stdout.strip()
        except Exception:
            active_win = ""

        for wid in window_ids:
            if not wid:
                continue
            try:
                title_result = subprocess.run(
                    ["xdotool", "getwindowname", wid], capture_output=True, text=True
                )
                pid_result = subprocess.run(
                    ["xdotool", "getwindowpid", wid], capture_output=True, text=True
                )
                windows.append(
                    WindowInfo(
                        id=wid,
                        title=title_result.stdout.strip(),
                        pid=int(pid_result.stdout.strip())
                        if pid_result.stdout.strip().isdigit()
                        else 0,
                        is_active=(wid == active_win),
                    )
                )
            except Exception:
                continue
        return windows

    def capture_window(self, window_id: str) -> str:
        temp_path = get_temp_path()
        result = subprocess.run(
            ["import", "-window", window_id, temp_path], capture_output=True, text=True
        )
        if result.returncode != 0:
            if result.returncode == 127:
                raise FileNotFoundError(
                    "import command not found (imagemagick not installed)"
                )
            raise subprocess.CalledProcessError(
                result.returncode, "import", stderr=result.stderr
            )
        return temp_path
