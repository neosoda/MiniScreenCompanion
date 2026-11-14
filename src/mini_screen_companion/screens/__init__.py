from .base import BaseScreen
from .geekmagic import GeekMagicScreen
from .local_file import LocalFileScreen
from ..core.config import ScreenConfig

def get_screen_client(config: ScreenConfig) -> BaseScreen:
    """Factory to create display clients based on configuration."""
    screen_type = (config.type or "geekmagic").lower()

    if screen_type in ("file", "local", "preview"):
        return LocalFileScreen(output_path=config.host if config.host.endswith(".jpg") else "preview.jpg")

    return GeekMagicScreen(
        host=config.host,
        port=config.port,
        timeout=config.timeout,
        min_upload_interval_seconds=config.min_upload_interval_seconds
    )

__all__ = ["BaseScreen", "GeekMagicScreen", "LocalFileScreen", "get_screen_client"]
