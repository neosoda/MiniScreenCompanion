from __future__ import annotations

import math
from typing import Tuple
from PIL import Image, ImageDraw


def draw_radial_tick_gauge(
    base_img: Image.Image,
    center: Tuple[int, int],
    radius: int,
    percent: float,
    active_color: Tuple[int, int, int] = (0, 240, 255),
    track_color: Tuple[int, int, int] = (24, 34, 52),
    start_deg: float = 140.0,
    total_deg: float = 260.0,
    num_ticks: int = 26,
    tick_length: int = 10,
    major_tick_length: int = 14,
    major_step: int = 5,
):
    """
    Renders an anti-aliased radial tick speedometer gauge using 2x supersampling.
    """
    cx, cy = center
    pct = max(0.0, min(100.0, percent))

    # Render at 2x on local scratch patch
    pad = radius + major_tick_length + 6
    patch_size = pad * 2
    patch_2x = Image.new("RGBA", (patch_size * 2, patch_size * 2), (0, 0, 0, 0))
    d2x = ImageDraw.Draw(patch_2x)

    c2x = patch_size
    r2x = radius * 2
    t_len_2x = tick_length * 2
    maj_len_2x = major_tick_length * 2

    # Draw subtle circular baseline arc under the ticks
    base_r2x = r2x - maj_len_2x - 4
    bbox_base = [c2x - base_r2x, c2x - base_r2x, c2x + base_r2x, c2x + base_r2x]
    d2x.arc(bbox_base, start=start_deg, end=start_deg + total_deg, fill=track_color, width=3)
    if pct > 1.0:
        fill_deg = start_deg + (pct / 100.0) * total_deg
        d2x.arc(bbox_base, start=start_deg, end=fill_deg, fill=active_color, width=4)

    for i in range(num_ticks):
        deg = start_deg + i * (total_deg / (num_ticks - 1))
        rad = math.radians(deg)
        is_active = (i / (num_ticks - 1)) <= (pct / 100.0)

        col = active_color if is_active else track_color
        is_major = (i % major_step == 0) or (i == num_ticks - 1)
        cur_len = maj_len_2x if is_major else t_len_2x

        x1 = c2x + (r2x - cur_len) * math.cos(rad)
        y1 = c2x + (r2x - cur_len) * math.sin(rad)
        x2 = c2x + r2x * math.cos(rad)
        y2 = c2x + r2x * math.sin(rad)

        width_2x = 5 if is_active else 3
        d2x.line([(x1, y1), (x2, y2)], fill=col, width=width_2x)

    # Downsample with high-quality resampling
    smooth_patch = patch_2x.resize((patch_size, patch_size), Image.Resampling.LANCZOS)

    # Paste onto base_img with alpha mask
    dest_x = cx - pad
    dest_y = cy - pad
    base_img.alpha_composite(smooth_patch, (dest_x, dest_y))
