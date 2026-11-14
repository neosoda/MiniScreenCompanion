from __future__ import annotations

import os
from typing import Dict, Tuple
from PIL import ImageFont


class FontManager:
    _cache: Dict[Tuple[str, int], ImageFont.FreeTypeFont | ImageFont.ImageFont] = {}

    FONT_CANDIDATES = [
        r"C:\Windows\Fonts\bahnschrift.ttf",
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]

    @classmethod
    def get_font(cls, size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        key = ("bold" if bold else "normal", size)
        if key in cls._cache:
            return cls._cache[key]

        font_path = None
        for candidate in cls.FONT_CANDIDATES:
            if os.path.exists(candidate):
                font_path = candidate
                break

        if font_path:
            try:
                font = ImageFont.truetype(font_path, size)
                cls._cache[key] = font
                return font
            except Exception:
                pass

        default_font = ImageFont.load_default()
        cls._cache[key] = default_font
        return default_font
