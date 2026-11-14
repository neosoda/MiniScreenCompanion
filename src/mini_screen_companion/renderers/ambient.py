"""Independent ambient cat animation for the 80px cozy room.

Sprites are deliberately tiny, transparent and deterministic for GIF previews.
They do not require or modify the device firmware.
"""
from PIL import Image, ImageDraw


def create_ambient_cat(frame_idx: int, sleeping: bool = False) -> Image.Image:
    image = Image.new("RGBA", (30, 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    phase = frame_idx % 8
    orange = (237, 145, 76, 255)
    shadow = (190, 92, 45, 255)
    eye = (57, 40, 37, 255)

    # Subtle breathing; the tail sways separately from the avatar animation.
    bob = 1 if sleeping and phase in (2, 3, 4, 5) else 0
    draw.ellipse((7, 11 - bob, 25, 18), fill=orange)
    draw.line((24, 14 - bob, 27, (5, 7, 10, 13, 13, 10, 7, 5)[phase]),
              fill=orange, width=3)
    draw.ellipse((3, 8 - bob, 14, 17), fill=orange)
    draw.polygon(((3, 10 - bob), (4, 4 - bob), (9, 9 - bob)), fill=orange)
    draw.polygon(((10, 9 - bob), (14, 4 - bob), (14, 12 - bob)), fill=orange)
    draw.line((15, 13 - bob, 17, 15 - bob), fill=shadow, width=1)
    draw.line((20, 13 - bob, 21, 16 - bob), fill=shadow, width=1)

    if sleeping or phase == 5:
        draw.line((6, 12 - bob, 8, 12 - bob), fill=eye)
        draw.line((11, 12 - bob, 13, 12 - bob), fill=eye)
    else:
        draw.point((7, 12 - bob), fill=eye)
        draw.point((12, 12 - bob), fill=eye)
    draw.point((10, 14 - bob), fill=(251, 210, 207, 255))
    return image
