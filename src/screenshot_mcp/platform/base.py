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
