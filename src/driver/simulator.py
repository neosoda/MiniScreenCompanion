from __future__ import annotations

import logging
from pathlib import Path
from PIL import Image

logger = logging.getLogger("SimulatorDriver")


class SimulatorDriver:
    def __init__(self, output_path: Path | str | None = None, width: int = 480, height: int = 320):
        if output_path is None:
            self.output_path = Path(__file__).resolve().parent.parent.parent / "preview.png"
        else:
            self.output_path = Path(output_path)
        self.width = width
        self.height = height

    def connect(self) -> bool:
        return True

    def display_pil_image(self, img: Image.Image) -> bool:
        try:
            if img.size != (self.width, self.height):
                img = img.resize((self.width, self.height), Image.Resampling.BILINEAR)
            self._current_img = img.copy()
            img.save(self.output_path, "PNG")
            return True
        except Exception as e:
            logger.error(f"Simulator failed to save preview: {e}")
            return False

    def display_partial(self, img: Image.Image, x: int, y: int) -> bool:
        try:
            if not hasattr(self, "_current_img") or self._current_img is None:
                self._current_img = Image.new("RGB", (self.width, self.height), (6, 9, 15))
            self._current_img.paste(img, (x, y))
            self._current_img.save(self.output_path, "PNG")
            return True
        except Exception as e:
            logger.error(f"Simulator partial error: {e}")
            return False
