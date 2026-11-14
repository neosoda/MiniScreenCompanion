from abc import ABC, abstractmethod

class BaseScreen(ABC):
    """Abstract interface for desktop display targets."""

    @abstractmethod
    def is_reachable(self) -> bool:
        """Check if the physical or virtual screen is online."""
        pass

    @abstractmethod
    def upload_frame(self, image_bytes: bytes) -> bool:
        """Upload a rendered JPEG/PNG frame to the screen."""
        pass

    @abstractmethod
    def set_brightness(self, level: int) -> bool:
        """Set screen brightness (2 to 99)."""
        pass
