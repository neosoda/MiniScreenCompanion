from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class Theme:
    bg: Tuple[int, int, int] = (10, 12, 16)
    card_bg: Tuple[int, int, int] = (18, 22, 30)
    card_border: Tuple[int, int, int] = (45, 54, 68)
    header_bg: Tuple[int, int, int] = (16, 20, 28)
    header_border: Tuple[int, int, int] = (42, 50, 64)
    bar_track: Tuple[int, int, int] = (34, 40, 52)

    text_white: Tuple[int, int, int] = (255, 255, 255)
    text_header: Tuple[int, int, int] = (220, 228, 240)
    text_muted: Tuple[int, int, int] = (140, 155, 175)
    badge_bg: Tuple[int, int, int] = (28, 35, 48)

    # Provider brand colors
    color_claude: Tuple[int, int, int] = (235, 120, 85)     # Coral
    color_codex: Tuple[int, int, int] = (55, 145, 255)       # Electric Blue
    color_gemini: Tuple[int, int, int] = (0, 210, 175)       # Emerald / Teal
    color_default: Tuple[int, int, int] = (34, 197, 94)

    # State colors
    color_ok: Tuple[int, int, int] = (34, 197, 94)           # Green
    color_warn: Tuple[int, int, int] = (245, 158, 11)        # Amber (remaining <= 35%)
    color_danger: Tuple[int, int, int] = (239, 68, 68)       # Red (remaining <= 15%)

    def get_gauge_color(self, remaining_pct: float, brand_color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        if remaining_pct <= 15.0:
            return self.color_danger
        elif remaining_pct <= 35.0:
            return self.color_warn
        return brand_color

DEFAULT_THEME = Theme()
