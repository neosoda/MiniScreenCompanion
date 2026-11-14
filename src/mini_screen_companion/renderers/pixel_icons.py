from PIL import Image, ImageDraw

def create_claude_icon() -> Image.Image:
    """16x16 Anthropic coral 8-bit space invader / alien icon."""
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c_primary = (235, 115, 80, 255) # Coral orange
    c_highlight = (255, 145, 110, 255)

    pixels = [
        "  X      X  ",
        "   X    X   ",
        "  XXXXXXXX  ",
        " XX XXXX XX ",
        "XXXXXXXXXXXX",
        "X XXXXXXXX X",
        "X X      X X",
        "   XX  XX   "
    ]
    for y, row in enumerate(pixels):
        for x, ch in enumerate(row):
            if ch == "X":
                col = c_highlight if y in (2, 3) and 4 <= x <= 7 else c_primary
                d.point((x + 2, y + 4), fill=col)
    return im

def create_codex_icon() -> Image.Image:
    """16x16 Electric purple cloud with white '>_' terminal prompt."""
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c_cloud = (124, 77, 255, 255)      # Violet / purple
    c_cloud_top = (150, 105, 255, 255)  # Light highlight
    c_prompt = (255, 255, 255, 255)    # White terminal prompt

    # Rounded cloud body
    d.rounded_rectangle([2, 5, 14, 13], radius=4, fill=c_cloud)
    d.ellipse([3, 3, 9, 9], fill=c_cloud_top)
    d.ellipse([6, 2, 13, 8], fill=c_cloud_top)
    d.ellipse([10, 5, 14, 9], fill=c_cloud)

    # '>_' in white pixel font
    # '>'
    d.point((5, 8), fill=c_prompt)
    d.point((6, 9), fill=c_prompt)
    d.point((5, 10), fill=c_prompt)
    # '_'
    d.point((8, 10), fill=c_prompt)
    d.point((9, 10), fill=c_prompt)
    d.point((10, 10), fill=c_prompt)
    return im

def create_gemini_icon() -> Image.Image:
    """16x16 Google Cyan 4-point sparkle star."""
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c_cyan = (56, 189, 248, 255)
    c_bright = (186, 230, 253, 255)
    c_white = (255, 255, 255, 255)

    # Vertical ray
    d.line([7, 2, 7, 13], fill=c_cyan, width=2)
    # Horizontal ray
    d.line([2, 7, 13, 7], fill=c_cyan, width=2)
    # Inner bright ring
    d.point((7, 5), fill=c_bright)
    d.point((8, 5), fill=c_bright)
    d.point((7, 10), fill=c_bright)
    d.point((8, 10), fill=c_bright)
    d.point((5, 7), fill=c_bright)
    d.point((5, 8), fill=c_bright)
    d.point((10, 7), fill=c_bright)
    d.point((10, 8), fill=c_bright)
    # Center white sparkle
    d.rectangle([7, 7, 8, 8], fill=c_white)
    return im

def create_default_icon() -> Image.Image:
    """16x16 Generic 8-bit AI chip icon."""
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c_chip = (74, 222, 128, 255)
    d.rounded_rectangle([3, 3, 12, 12], radius=2, fill=(30, 41, 59, 255), outline=c_chip)
    d.point((6, 6), fill=c_chip)
    d.point((9, 6), fill=c_chip)
    d.line([5, 9, 10, 9], fill=c_chip, width=1)
    return im

_ICON_CACHE = {}

def get_pixel_icon(provider_id: str) -> Image.Image:
    pid = provider_id.lower()
    if pid not in _ICON_CACHE:
        if "claude" in pid:
            _ICON_CACHE[pid] = create_claude_icon()
        elif "codex" in pid or "openai" in pid or "gpt" in pid:
            _ICON_CACHE[pid] = create_codex_icon()
        elif "gemini" in pid or "antigravity" in pid or "google" in pid:
            _ICON_CACHE[pid] = create_gemini_icon()
        else:
            _ICON_CACHE[pid] = create_default_icon()
    return _ICON_CACHE[pid]
