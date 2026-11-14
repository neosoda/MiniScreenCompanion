import hashlib
import logging
from pathlib import Path
from typing import Optional
from .base import BaseScreen

logger = logging.getLogger(__name__)

class LocalFileScreen(BaseScreen):
    """
    Virtual screen target that writes frames to a local JPEG/PNG file.
    Ideal for testing, headless runners, and integrations.
    """
    def __init__(self, output_path: str = "preview.jpg"):
        self.output_path = Path(output_path)
        self._last_frame_hash: Optional[str] = None

    def is_reachable(self) -> bool:
        return True

    def set_brightness(self, level: int) -> bool:
        return True

    def upload_frame(self, image_bytes: bytes, force: bool = False) -> bool:
        current_hash = hashlib.sha256(image_bytes).hexdigest()
        if not force and current_hash == self._last_frame_hash and self.output_path.exists():
            return True

        try:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            self.output_path.write_bytes(image_bytes)
            self._last_frame_hash = current_hash
            logger.info(f"Dashboard frame saved to {self.output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to write local frame to {self.output_path}: {e}")
            return False
