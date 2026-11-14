from __future__ import annotations

from typing import Tuple
from PIL import ImageDraw


def draw_segmented_bar(
    draw: ImageDraw.ImageDraw,
    rect: Tuple[int, int, int, int],  # x1, y1, x2, y2
    percent: float,
    num_segments: int = 18,
    active_color: Tuple[int, int, int] = (16, 231, 117),
    track_color: Tuple[int, int, int] = (20, 30, 46),
    gap: int = 2,
    radius: int = 2,
):
    x1, y1, x2, y2 = rect
    w = x2 - x1
    h = y2 - y1

    pct = max(0.0, min(100.0, percent))
    num_segments = max(4, num_segments)

    seg_w = (w - (num_segments - 1) * gap) // num_segments
    active_count = int(round((pct / 100.0) * num_segments))

    for i in range(num_segments):
        sx1 = x1 + i * (seg_w + gap)
        sx2 = sx1 + seg_w
        col = active_color if i < active_count else track_color
        draw.rounded_rectangle([sx1, y1, sx2, y2], radius=radius, fill=col)
