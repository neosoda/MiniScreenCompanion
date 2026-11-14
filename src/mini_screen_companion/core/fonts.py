import os
import sys
from pathlib import Path
from typing import Dict, Any
from PIL import ImageFont

def get_font_paths():
    """Locate candidate TrueType fonts across operating systems."""
    candidates = []

    # 1. Bundled package/project assets
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    local_asset_fonts = base_dir / "assets" / "fonts"
    if local_asset_fonts.is_dir():
        for f in local_asset_fonts.glob("*.ttf"):
            candidates.append(str(f))

    # 2. OS-specific system fonts
    if sys.platform.startswith("win"):
        candidates.extend([
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/calibrib.ttf",
        ])
    elif sys.platform == "darwin":
        candidates.extend([
            "/System/Library/Fonts/SFNS.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial Bold.ttf",
        ])
    else: # Linux / BSD
        candidates.extend([
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        ])

    return [p for p in candidates if os.path.isfile(p)]

def load_fonts() -> Dict[str, Any]:
    """Load optimized typography hierarchy with graceful fallback."""
    font_paths = get_font_paths()
    primary_font = font_paths[0] if font_paths else None

    if primary_font:
        try:
            return {
                "badge": ImageFont.truetype(primary_font, 10),
                "header": ImageFont.truetype(primary_font, 11),
                "reset": ImageFont.truetype(primary_font, 12),
                "clock": ImageFont.truetype(primary_font, 13),
                "pct": ImageFont.truetype(primary_font, 14),
                "title": ImageFont.truetype(primary_font, 15),
                "lg_b": ImageFont.truetype(primary_font, 18),
                "xl_b": ImageFont.truetype(primary_font, 24),
                "sm": ImageFont.truetype(primary_font, 11),
                "xs": ImageFont.truetype(primary_font, 10),
            }
        except Exception:
            pass

    # Fallback to Pillow standard bitmap font
    df = ImageFont.load_default()
    return {
        "badge": df,
        "header": df,
        "reset": df,
        "clock": df,
        "pct": df,
        "title": df,
        "lg_b": df,
        "xl_b": df,
        "sm": df,
        "xs": df,
    }
