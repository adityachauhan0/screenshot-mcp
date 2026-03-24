import json
import subprocess
from screenshot_mcp.platform.base import WindowCapture, WindowInfo
from screenshot_mcp.utils import get_temp_path


class WaylandCapture(WindowCapture):
    def list_windows(self) -> list[WindowInfo]:
        windows = []

        active_id = ""
        try:
            active_result = subprocess.run(
                [
                    "qdbus",
                    "org.kde.KWin",
                    "/KWin",
                    "org.kde.KWin.WindowManager",
                    "activeWindow",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if active_result.returncode == 0:
                active_id = active_result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        script = """
        var windows = [];
        var clients = KWin.windowList();
        for (var i = 0; i < clients.length; i++) {
            var c = clients[i];
            windows.push({
                id: String(c.windowId),
                title: c.caption,
                pid: c.pid,
                is_active: c.windowId == activeWindow
            });
        }
        JSON.stringify(windows);
        """

        try:
            result = subprocess.run(
                [
                    "qdbus",
                    "org.kde.KWin",
                    "/KWin",
                    "org.kde.KWin.Scripting",
                    "evaluateScript",
                    script,
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                try:
                    windows_data = json.loads(result.stdout.strip())
                    return [WindowInfo(**w) for w in windows_data]
                except json.JSONDecodeError:
                    pass
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        try:
            xdotool_result = subprocess.run(
                ["xdotool", "search", "--onlyvisible", "--name", "."],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if xdotool_result.returncode == 0:
                window_ids = xdotool_result.stdout.strip().split("\n")
                for wid in window_ids:
                    if not wid:
                        continue
                    try:
                        title_result = subprocess.run(
                            ["xdotool", "getwindowname", wid],
                            capture_output=True,
                            text=True,
                            timeout=2,
                        )
                        pid_result = subprocess.run(
                            ["xdotool", "getwindowpid", wid],
                            capture_output=True,
                            text=True,
                            timeout=2,
                        )
                        windows.append(
                            WindowInfo(
                                id=wid,
                                title=title_result.stdout.strip(),
                                pid=int(pid_result.stdout.strip())
                                if pid_result.stdout.strip().isdigit()
                                else 0,
                                is_active=(wid == active_id),
                            )
                        )
                    except (subprocess.TimeoutExpired, ValueError):
                        continue
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return windows

    def capture_window(self, window_id: str) -> str:
        temp_path = get_temp_path()
        result = subprocess.run(
            ["grim", "-g", f"@{window_id}", temp_path], capture_output=True, text=True
        )
        if result.returncode != 0:
            if result.returncode == 127:
                raise FileNotFoundError("grim not installed")
            raise subprocess.CalledProcessError(
                result.returncode, "grim", stderr=result.stderr
            )
        return temp_path
