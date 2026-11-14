from __future__ import annotations

from typing import List, Tuple
from PIL import Image, ImageDraw


def draw_sparkline(
    base_img: Image.Image,
    draw: ImageDraw.ImageDraw,
    rect: Tuple[int, int, int, int],  # x1, y1, x2, y2
    values: List[float],
    min_val: float = 0.0,
    max_val: float = 100.0,
    line_color: Tuple[int, int, int] = (0, 229, 255),
    fill_alpha: int = 40,
    grid_lines: bool = True,
):
    x1, y1, x2, y2 = rect
    w = x2 - x1
    h = y2 - y1

    if w <= 4 or h <= 4:
        return

    # Draw subtle background grid line (middle)
    if grid_lines:
        mid_y = y1 + h // 2
        draw.line([(x1, mid_y), (x2, mid_y)], fill=(28, 38, 55), width=1)

    if not values or len(values) < 2:
        draw.line([(x1, y2 - 2), (x2, y2 - 2)], fill=line_color, width=1)
        return

    span = max_val - min_val if max_val > min_val else 1.0

    points = []
    num_vals = len(values)
    step_x = w / (num_vals - 1)

    for i, v in enumerate(values):
        val = max(min_val, min(max_val, v))
        norm = (val - min_val) / span
        px = int(x1 + i * step_x)
        py = int(y2 - norm * (h - 4) - 2)
        points.append((px, py))

    # Translucent area fill
    if fill_alpha > 0 and len(points) >= 2:
        poly_points = [(x1, y2)] + points + [(points[-1][0], y2)]
        overlay = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        fill_rgba = (line_color[0], line_color[1], line_color[2], fill_alpha)
        overlay_draw.polygon(poly_points, fill=fill_rgba)
        base_img.alpha_composite(overlay)

    # Draw curve line
    draw.line(points, fill=line_color, width=2)
