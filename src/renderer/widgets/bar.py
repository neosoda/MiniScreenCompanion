from __future__ import annotations

from typing import Tuple
from PIL import ImageDraw


def draw_progress_bar(
    draw: ImageDraw.ImageDraw,
    rect: Tuple[int, int, int, int],  # x1, y1, x2, y2
    percent: float,
    fill_color: Tuple[int, int, int] = (0, 229, 255),
    track_color: Tuple[int, int, int] = (30, 41, 59),
    radius: int = 3,
):
    x1, y1, x2, y2 = rect
    w = x2 - x1
    h = y2 - y1

    pct = max(0.0, min(100.0, percent))

    # Background track
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=track_color)

    if pct > 0.5:
        fill_w = max(radius * 2, int(w * (pct / 100.0)))
        draw.rounded_rectangle([x1, y1, min(x2, x1 + fill_w), y2], radius=radius, fill=fill_color)
