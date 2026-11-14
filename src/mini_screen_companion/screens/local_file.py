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
            is_gif = image_bytes.startswith((b"GIF87a", b"GIF89a"))

            if is_gif:
                gif_path = self.output_path.with_suffix(".gif")
                jpg_path = self.output_path.with_suffix(".jpg")
                gif_path.write_bytes(image_bytes)

                # Also save first frame as JPEG for previewers expecting JPG
                try:
                    import io
                    from PIL import Image
                    with Image.open(io.BytesIO(image_bytes)) as im:
                        im.seek(0)
                        im.convert("RGB").save(jpg_path, format="JPEG", quality=92)
                except Exception as ex:
                    logger.debug(f"Could not write fallback JPEG: {ex}")

                logger.info(f"Dashboard frames saved to {gif_path} and {jpg_path}")
            else:
                self.output_path.write_bytes(image_bytes)
                logger.info(f"Dashboard frame saved to {self.output_path}")

            self._last_frame_hash = current_hash
            return True
        except Exception as e:
            logger.error(f"Failed to write local frame to {self.output_path}: {e}")
            return False
