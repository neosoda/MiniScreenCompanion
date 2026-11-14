from .base import BaseScreen
from .geekmagic import GeekMagicScreen
from .geekmagic_serial import GeekMagicSerialScreen
from .local_file import LocalFileScreen
from ..core.config import ScreenConfig

def get_screen_client(config: ScreenConfig) -> BaseScreen:
    """Factory to create display clients based on configuration."""
    screen_type = (config.type or "geekmagic").lower()

    if screen_type in ("file", "local", "preview"):
        return LocalFileScreen(output_path=config.host if config.host.endswith(".jpg") else "preview.jpg")

    if screen_type in ("serial", "usb", "com") or config.host.upper().startswith("COM"):
        return GeekMagicSerialScreen(
            port=config.host if config.host.upper().startswith("COM") else "COM7",
            baudrate=config.port if config.port > 1000 else 115200,
            timeout=config.timeout
        )

    return GeekMagicScreen(
        host=config.host,
        port=config.port,
        timeout=config.timeout
    )

__all__ = ["BaseScreen", "GeekMagicScreen", "GeekMagicSerialScreen", "LocalFileScreen", "get_screen_client"]
