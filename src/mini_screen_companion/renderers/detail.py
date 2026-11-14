import io
from datetime import datetime
from typing import Optional
from PIL import Image, ImageDraw
from ..core.models import ProviderQuota
from ..core.fonts import load_fonts
from .theme import Theme, DEFAULT_THEME
from .summary import draw_bar

FONTS = load_fonts()

def render_detail(
    provider: ProviderQuota,
    page_idx: int = 1,
    total_pages: int = 1,
    theme: Theme = DEFAULT_THEME,
    time_str: Optional[str] = None
) -> bytes:
    """
    Renders a single provider full-screen with giant fonts.
    Ideal for carousel mode or dedicated focus.
    """
    img = Image.new("RGB", (240, 240), color=theme.bg)
    draw = ImageDraw.Draw(img)

    if not time_str:
        time_str = datetime.now().strftime("%H:%M")

    brand_map = {
        "claude": ("CLAUDE CODE", theme.color_claude),
        "codex": ("OPENAI CODEX", theme.color_codex),
        "gemini": ("GOOGLE GEMINI", theme.color_gemini),
    }
    title, bcolor = brand_map.get(provider.provider_id, (provider.display_name.upper(), theme.color_default))

    # Top banner
    draw.rectangle([0, 0, 240, 30], fill=theme.header_bg)
    draw.line([0, 30, 240, 30], fill=theme.header_border, width=1)
    draw.ellipse([10, 11, 18, 19], fill=bcolor)
    draw.text((24, 5), title, fill=theme.text_white, font=FONTS["lg_b"])
    draw.text((195, 7), time_str, fill=theme.text_muted, font=FONTS["clock"])

    if not provider.available:
        draw.rounded_rectangle([10, 45, 230, 190], radius=6, fill=theme.card_bg, outline=theme.card_border)
        draw.text((20, 65), "Service non disponible", fill=theme.color_danger, font=FONTS["title"])
        draw.text((20, 95), provider.error_message or "Erreur inconnue", fill=theme.text_muted, font=FONTS["sm"])
    else:
        # 1. Session 5H Card (Dominant)
        draw.rounded_rectangle([8, 38, 232, 122], radius=6, fill=theme.card_bg, outline=theme.card_border)
        draw.text((16, 44), "QUOTA RESTANT (5 HEURES)", fill=theme.text_muted, font=FONTS["badge"])
        
        rem_5h = provider.session_5h.remaining_pct if provider.session_5h else 0.0
        col_5h = theme.get_gauge_color(rem_5h, bcolor)
        r5_str = provider.session_5h.format_countdown() if provider.session_5h else "--"

        draw.text((16, 56), f"{int(round(rem_5h))}%", fill=col_5h, font=FONTS["xl_b"])
        draw.text((115, 62), "Reset dans", fill=theme.text_muted, font=FONTS["xs"])
        draw.text((115, 74), r5_str, fill=theme.text_white, font=FONTS["title"])

        draw_bar(draw, 16, 98, 200, 14, rem_5h, col_5h, theme.bar_track)

        # 2. Weekly 7D Card
        draw.rounded_rectangle([8, 130, 232, 214], radius=6, fill=theme.card_bg, outline=theme.card_border)
        draw.text((16, 136), "QUOTA HEBDOMADAIRE (7 JOURS)", fill=theme.text_muted, font=FONTS["badge"])
        
        rem_7d = provider.weekly_7d.remaining_pct if provider.weekly_7d else 0.0
        col_7d = theme.get_gauge_color(rem_7d, bcolor)
        r7_str = provider.weekly_7d.format_countdown() if provider.weekly_7d else "--"

        draw.text((16, 148), f"{int(round(rem_7d))}%", fill=col_7d, font=FONTS["xl_b"])
        draw.text((115, 154), "Reset dans", fill=theme.text_muted, font=FONTS["xs"])
        draw.text((115, 166), r7_str, fill=theme.text_white, font=FONTS["title"])

        draw_bar(draw, 16, 190, 200, 14, rem_7d, col_7d, theme.bar_track)

    # Footer
    draw.rectangle([0, 222, 240, 240], fill=theme.header_bg)
    draw.line([0, 222, 240, 222], fill=theme.header_border, width=1)
    draw.text((10, 225), "Vue détaillée", fill=theme.text_muted, font=FONTS["xs"])
    draw.text((195, 225), f"{page_idx}/{total_pages}", fill=theme.text_white, font=FONTS["xs"])

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    return buf.getvalue()
