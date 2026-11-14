import io
from datetime import datetime
from typing import Optional
from PIL import Image, ImageDraw
from ..core.models import DashboardSnapshot
from ..core.fonts import load_fonts
from .theme import Theme, DEFAULT_THEME

FONTS = load_fonts()

def draw_bar(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, pct: float, fill_color: tuple, bg_color: tuple):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=bg_color)
    clamped = max(0.0, min(100.0, pct))
    fw = int(w * (clamped / 100.0))
    if fw > 0:
        draw.rounded_rectangle([x, y, x + fw, y + h], radius=3, fill=fill_color)

def render_summary(
    snapshot: DashboardSnapshot,
    theme: Theme = DEFAULT_THEME,
    time_str: Optional[str] = None
) -> bytes:
    """
    Renders an immutable 240x240 JPEG frame optimized for micro-displays.
    Pure deterministic function: output depends strictly on inputs.
    """
    img = Image.new("RGB", (240, 240), color=theme.bg)
    draw = ImageDraw.Draw(img)

    if not time_str:
        time_str = datetime.now().strftime("%H:%M")

    # Header (Compact & High Contrast, y=0 to 22)
    draw.rectangle([0, 0, 240, 22], fill=theme.header_bg)
    draw.line([0, 22, 240, 22], fill=theme.header_border, width=1)
    draw.ellipse([8, 8, 14, 14], fill=theme.color_ok)
    draw.text((20, 4), "QUOTAS RESTANTS", fill=theme.text_header, font=FONTS["header"])
    draw.text((195, 3), time_str, fill=theme.text_white, font=FONTS["clock"])

    brand_map = {
        "claude": ("CLAUDE", theme.color_claude),
        "claude_code": ("CLAUDE", theme.color_claude),
        "codex": ("CODEX", theme.color_codex),
        "gemini": ("GEMINI", theme.color_gemini),
        "antigravity": ("GEMINI", theme.color_gemini)
    }

    y = 25
    card_h = 68
    for p in snapshot.providers[:3]:  # Top 3 providers fit perfectly
        name, bcolor = brand_map.get(p.provider_id, (p.display_name.upper(), theme.color_default))
        draw.rounded_rectangle([4, y, 236, y + card_h], radius=6, fill=theme.card_bg, outline=theme.card_border, width=1)

        # Status disc + Provider Title
        draw.ellipse([11, y + 8, 17, y + 14], fill=bcolor)
        draw.text((23, y + 3), name, fill=theme.text_white, font=FONTS["title"])

        if not p.available:
            draw.text((23, y + 28), p.error_message or "Indisponible", fill=theme.color_warn, font=FONTS["sm"])
        else:
            # 1. 5H Session Quota
            rem_5h = p.session_5h.remaining_pct if p.session_5h else 0.0
            r5_str = p.session_5h.format_countdown() if p.session_5h else "--"
            col_5h = theme.get_gauge_color(rem_5h, bcolor)

            # Badge 5H
            draw.rounded_rectangle([10, y + 24, 27, y + 37], radius=3, fill=theme.badge_bg)
            draw.text((12, y + 24), "5H", fill=(180, 195, 215), font=FONTS["badge"])

            # Percentage
            draw.text((31, y + 22), f"{int(round(rem_5h))}%", fill=col_5h, font=FONTS["pct"])

            # Gauge (9px thickness)
            draw_bar(draw, 73, y + 26, 102, 9, rem_5h, col_5h, theme.bar_track)

            # Right-aligned Countdown
            bbox5 = FONTS["reset"].getbbox(r5_str)
            tw5 = bbox5[2] - bbox5[0]
            draw.text((230 - tw5, y + 23), r5_str, fill=theme.text_white, font=FONTS["reset"])

            # 2. 7D Weekly Quota
            rem_7d = p.weekly_7d.remaining_pct if p.weekly_7d else 0.0
            r7_str = p.weekly_7d.format_countdown() if p.weekly_7d else "--"
            col_7d = theme.get_gauge_color(rem_7d, bcolor)

            # Badge 7J
            draw.rounded_rectangle([10, y + 45, 27, y + 58], radius=3, fill=theme.badge_bg)
            draw.text((12, y + 45), "7J", fill=(210, 185, 120), font=FONTS["badge"])

            # Percentage
            draw.text((31, y + 43), f"{int(round(rem_7d))}%", fill=col_7d, font=FONTS["pct"])

            # Gauge
            draw_bar(draw, 73, y + 47, 102, 9, rem_7d, col_7d, theme.bar_track)

            # Right-aligned Countdown
            bbox7 = FONTS["reset"].getbbox(r7_str)
            tw7 = bbox7[2] - bbox7[0]
            draw.text((230 - tw7, y + 44), r7_str, fill=theme.text_white, font=FONTS["reset"])

        y += card_h + 3

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    return buf.getvalue()
