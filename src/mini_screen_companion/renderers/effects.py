"""Tiny, deterministic atmospheric micro-animations for the 240x80 room.

All effects are kept in the top 80 pixels. No device writes or timers here.
"""
from PIL import Image, ImageDraw


def draw_atmosphere(frame: Image.Image, scene: str, phase: int,
                    action: str, enabled: bool = True) -> None:
    if not enabled:
        return
    draw = ImageDraw.Draw(frame)
    phase %= 8

    if scene == "rain":
        # Moving rain is clipped to the window interior (x=174..210, y=10..36).
        for index, x in enumerate((177, 183, 189, 197, 203, 209)):
            y = 11 + ((phase * 4 + index * 7) % 21)
            draw.line((x, y, x - 1, min(y + 3, 36)), fill=(184, 226, 245, 255), width=1)
    elif scene == "night":
        for index, (x, y) in enumerate(((177, 30), (201, 14), (204, 27))):
            if (phase + index * 2) % 4 != 0:
                draw.point((x, y), fill=(255, 235, 181, 255))
    else:
        # A slow sun shimmer, rather than a whole-room strobe.
        if phase in (1, 2, 5, 6):
            draw.point((178, 33), fill=(255, 254, 223, 255))

    if action == "desk" and phase in (0, 3, 6):
        # Small code activity glint near the laptop.
        draw.point((124, 45), fill=(105, 226, 249, 255))
