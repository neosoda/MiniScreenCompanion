import io
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple
from PIL import Image, ImageDraw, ImageFont

from ..core.models import DashboardSnapshot, ProviderQuota
from ..core.config import AvatarConfig
from .pixel_icons import get_pixel_icon
from .avatar_sprites import (
    get_auto_mood,
    render_room_1_3_background,
    create_runner_avatar,
    create_desk_avatar,
    create_coffee_avatar,
    create_pet_avatar,
    create_sleep_avatar,
    load_custom_frames
)
from .ambient import create_ambient_cat
from .effects import draw_atmosphere

def _load_retro_fonts():
    """Load crisp typography for 1/3 - 2/3 layout."""
    candidates_mono = []
    candidates_ui = []

    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    local_fonts = base_dir / "assets" / "fonts"
    if local_fonts.is_dir():
        for f in local_fonts.glob("*.ttf"):
            candidates_mono.append(str(f))
            candidates_ui.append(str(f))

    if sys.platform.startswith("win"):
        candidates_mono.extend(["C:/Windows/Fonts/consolab.ttf", "C:/Windows/Fonts/consola.ttf"])
        candidates_ui.extend(["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"])
    elif sys.platform == "darwin":
        candidates_mono.extend(["/System/Library/Fonts/Menlo.ttc", "/Library/Fonts/Courier New Bold.ttf"])
        candidates_ui.extend(["/System/Library/Fonts/SFNS.ttf", "/Library/Fonts/Helvetica.ttc"])
    else:
        candidates_mono.extend([
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"
        ])
        candidates_ui.extend([
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
        ])

    mono_path = next((p for p in candidates_mono if Path(p).is_file()), None)
    ui_path = next((p for p in candidates_ui if Path(p).is_file()), None)

    if mono_path and ui_path:
        try:
            return {
                "title": ImageFont.truetype(mono_path, 13),
                "mono_sm": ImageFont.truetype(mono_path, 10),
                "badge": ImageFont.truetype(ui_path, 9),
                "hdr_user": ImageFont.truetype(mono_path, 10),
                "ui_stat": ImageFont.truetype(ui_path, 9),
                "clock": ImageFont.truetype(mono_path, 10),
            }
        except Exception:
            pass

    df = ImageFont.load_default()
    return {
        "title": df, "mono_sm": df, "badge": df,
        "hdr_user": df, "ui_stat": df, "clock": df
    }

RETRO_FONTS = _load_retro_fonts()

def _get_gauge_color(pct: float, is_used: bool = False) -> Tuple[int, int, int]:
    val = pct if is_used else (100.0 - pct)
    if val >= 90.0:
        return (239, 68, 68)   # Red
    elif val >= 75.0:
        return (245, 158, 11)  # Amber
    return (34, 197, 94)       # Emerald Green

def render_quotas_2_3_panel(
    providers: List[ProviderQuota],
    metric_mode: str = "remaining"
) -> Image.Image:
    """
    Renders the bottom 2/3 (y=80 to 240, height=160px) quota monitoring cards.
    Displays all 3 providers (Claude, Codex, Gemini) simultaneously.
    """
    panel = Image.new("RGBA", (240, 160), (7, 11, 26, 255))
    d = ImageDraw.Draw(panel)

    # Top border line separating avatar room from quotas
    d.line([0, 0, 240, 0], fill=(42, 65, 115, 255), width=1)

    display_providers = providers[:3]
    card_h = 50
    y = 3
    is_used = (metric_mode.lower() == "used")

    for p in display_providers:
        # Card container
        d.rounded_rectangle([4, y, 236, y + card_h], radius=4, fill=(11, 16, 36, 255), outline=(30, 41, 59, 255), width=1)

        # 1. 8-Bit Icon
        icon = get_pixel_icon(p.provider_id)
        panel.paste(icon, (9, y + 5), icon)

        # 2. Title
        name = p.display_name.upper().replace(" CODE", "")
        d.text((29, y + 4), name, fill=(255, 255, 255, 255), font=RETRO_FONTS["title"])

        if not p.available:
            d.text((100, y + 6), "indisponible", fill=(245, 158, 11, 255), font=RETRO_FONTS["mono_sm"])
            y += card_h + 3
            continue

        # 3. 5H Session Line
        r5_str = p.session_5h.format_countdown() if p.session_5h else "--"
        pct_5h = ((p.session_5h.used_pct if is_used else p.session_5h.remaining_pct)
                  if p.session_5h else None)
        col_5h = _get_gauge_color(pct_5h, is_used=is_used) if pct_5h is not None else (148, 163, 184)

        d.text((9, y + 22), "5H", fill=(148, 163, 184, 255), font=RETRO_FONTS["badge"])
        d.text((25, y + 20), f"{int(round(pct_5h))}%" if pct_5h is not None else "--",
               fill=col_5h, font=RETRO_FONTS["mono_sm"])

        # 5H Bar (x=52 to 175, w=123, h=5)
        d.rectangle([52, y + 24, 175, y + 29], fill=(18, 26, 46, 255))
        bw5 = int(123 * ((pct_5h or 0.0) / 100.0))
        if bw5 > 0:
            d.rectangle([52, y + 24, 52 + bw5, y + 29], fill=col_5h)
        d.text((182, y + 20), r5_str, fill=(203, 213, 225, 255), font=RETRO_FONTS["mono_sm"])

        # 4. 7J Weekly Line
        r7_str = p.weekly_7d.format_countdown() if p.weekly_7d else "--"
        pct_7d = ((p.weekly_7d.used_pct if is_used else p.weekly_7d.remaining_pct)
                  if p.weekly_7d else None)
        col_7d = _get_gauge_color(pct_7d, is_used=is_used) if pct_7d is not None else (148, 163, 184)

        d.text((9, y + 36), "7J", fill=(148, 163, 184, 255), font=RETRO_FONTS["badge"])
        d.text((25, y + 34), f"{int(round(pct_7d))}%" if pct_7d is not None else "--",
               fill=col_7d, font=RETRO_FONTS["mono_sm"])

        # 7J Bar
        d.rectangle([52, y + 38, 175, y + 43], fill=(18, 26, 46, 255))
        bw7 = int(123 * ((pct_7d or 0.0) / 100.0))
        if bw7 > 0:
            d.rectangle([52, y + 38, 52 + bw7, y + 43], fill=col_7d)
        d.text((182, y + 34), r7_str, fill=(203, 213, 225, 255), font=RETRO_FONTS["mono_sm"])

        y += card_h + 3

    return panel

def render_cozy_avatar(
    snapshot: DashboardSnapshot,
    avatar_cfg: Optional[AvatarConfig] = None,
    time_str: Optional[str] = None,
    animated: bool = True,
    frame_offset: int = 0
) -> bytes:
    """
    Renders 1/3 top animated avatar scene + 2/3 bottom crystal-clear quota cards.
    Outputs animated GIF (8 FPS) or single frame JPEG.
    """
    if avatar_cfg is None:
        avatar_cfg = AvatarConfig()

    now = datetime.now()
    if not time_str:
        time_str = now.strftime("%H:%M")

    try:
        hour = int(time_str.split(":")[0])
        if not 0 <= hour <= 23:
            raise ValueError("hour out of range")
    except (ValueError, IndexError):
        hour = now.hour

    # 1. Action & mood status
    requested_action = avatar_cfg.action.lower()
    action = requested_action
    status_msg = avatar_cfg.status

    if action == "auto" or status_msg == "auto":
        auto_act, auto_stat = get_auto_mood(hour)
        if action == "auto":
            action = auto_act
        if status_msg == "auto":
            labels = {"desk": "Dans le flow", "coffee": "Pause cafe",
                      "pet": "Calin au chat", "run": "En balade", "sleep": "Zzz..."}
            status_msg = auto_stat if requested_action == "auto" else labels.get(action, "")

    # 2. Manual atmosphere presets override the clock only in the renderer.
    selected_scene = avatar_cfg.scene if avatar_cfg.scene in ("auto", "day", "night", "rain") else "auto"
    scene = ("night" if hour >= 20 or hour < 7 else "day") if selected_scene == "auto" else selected_scene
    is_night = scene == "night"

    # Render top 1/3 room background (y=0 to 78)
    show_stool = (action != "desk" and action != "pet" and action != "sleep")
    room_bg = render_room_1_3_background(
        user_name=avatar_cfg.name,
        status_message=status_msg,
        time_str=time_str,
        font_mono_hdr=RETRO_FONTS["hdr_user"],
        font_ui_stat=RETRO_FONTS["ui_stat"],
        font_mono_clock=RETRO_FONTS["clock"],
        show_stool=show_stool,
        is_night=is_night,
        palette=avatar_cfg.palette
    )

    # 3. Pre-render bottom 2/3 quotas panel (y=80 to 240)
    quotas_panel = render_quotas_2_3_panel(
        providers=list(snapshot.providers),
        metric_mode=avatar_cfg.metric
    )

    # 4. Check for custom user animation or procedural chibi frames
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    assets_dir = base_dir / "assets"
    custom_frames = load_custom_frames(assets_dir) if avatar_cfg.animated else None

    # Stock HTTP firmware receives JPEG; do not render eight throwaway frames.
    frames_count = 8 if animated and avatar_cfg.animated else 1
    frame_images = []

    avatar_y = 38
    if action == "run":
        avatar_base_x = 95
        offsets = [-12, -6, 0, 6, 12, 6, 0, -6]
    elif action == "desk":
        avatar_base_x = 92
        offsets = [0] * 8
    elif action == "coffee":
        avatar_base_x = 135 # near window
        offsets = [0] * 8
    elif action == "pet":
        avatar_base_x = 90
        offsets = [0] * 8
    elif action == "sleep":
        avatar_base_x = 88
        offsets = [0] * 8
    else:
        avatar_base_x = 95
        offsets = [0] * 8

    for i in range(frames_count):
        phase = (i + frame_offset) % 8
        frame = Image.new("RGBA", (240, 240), (7, 11, 26, 255))
        frame.paste(room_bg, (0, 0), room_bg)

        # Get sprite
        if custom_frames:
            avatar_sprite = custom_frames[phase % len(custom_frames)]
        elif action == "run":
            avatar_sprite = create_runner_avatar(phase)
        elif action == "desk":
            avatar_sprite = create_desk_avatar(phase)
        elif action == "coffee":
            avatar_sprite = create_coffee_avatar(phase)
        elif action == "pet":
            avatar_sprite = create_pet_avatar(phase)
        elif action == "sleep":
            avatar_sprite = create_sleep_avatar(phase)
        else:
            avatar_sprite = create_desk_avatar(phase)

        cur_x = avatar_base_x + offsets[phase]
        frame.paste(avatar_sprite, (cur_x, avatar_y), avatar_sprite)

        # A separate companion inhabits the room even while the developer codes.
        if avatar_cfg.show_cat and action != "pet":
            room_cat = create_ambient_cat(phase, sleeping=(action == "sleep"))
            cat_x = 174 + (-2, -1, 0, 1, 2, 1, 0, -1)[phase]
            frame.paste(room_cat, (cat_x, 57), room_cat)

        draw_atmosphere(frame, scene, phase, action, enabled=avatar_cfg.effects)

        # Paste bottom quotas panel (y=80 to 240)
        frame.paste(quotas_panel, (0, 80), quotas_panel)

        frame_rgb = frame.convert("RGB")
        frame_images.append(frame_rgb)

    buf = io.BytesIO()
    if animated and avatar_cfg.animated:
        duration_ms = max(80, int(1000 / max(1, min(12, avatar_cfg.fps))))
        frame_images[0].save(
            buf,
            format="GIF",
            save_all=True,
            append_images=frame_images[1:],
            duration=duration_ms,
            loop=0,
            optimize=True
        )
    else:
        target_f = frame_images[0]
        target_f.save(buf, format="JPEG", quality=92)

    return buf.getvalue()
