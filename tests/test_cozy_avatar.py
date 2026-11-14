import io
from datetime import datetime, timezone
from PIL import Image

from mini_screen_companion.collectors.mock import MockCollector
from mini_screen_companion.core.models import DashboardSnapshot
from mini_screen_companion.core.config import AvatarConfig
from mini_screen_companion.renderers.pixel_icons import get_pixel_icon
from mini_screen_companion.renderers.cozy_avatar import render_cozy_avatar

def test_pixel_icons_generation():
    for pid in ["claude", "codex", "gemini", "antigravity", "unknown"]:
        icon = get_pixel_icon(pid)
        assert isinstance(icon, Image.Image)
        assert icon.size == (16, 16)
        assert icon.mode == "RGBA"

def test_render_cozy_avatar_animated_gif():
    providers = MockCollector().collect_all()
    snap = DashboardSnapshot(timestamp=datetime.now(timezone.utc), providers=tuple(providers))
    cfg = AvatarConfig(name="TESTUSER", status="Ça vib", action="run", animated=True)

    gif_bytes = render_cozy_avatar(snap, avatar_cfg=cfg, time_str="14:30", animated=True)
    assert isinstance(gif_bytes, bytes)
    assert gif_bytes.startswith((b"GIF87a", b"GIF89a"))

    im = Image.open(io.BytesIO(gif_bytes))
    assert im.size == (240, 240)
    assert getattr(im, "n_frames", 1) == 8

def test_render_cozy_avatar_static_jpeg():
    providers = MockCollector().collect_all()
    snap = DashboardSnapshot(timestamp=datetime.now(timezone.utc), providers=tuple(providers))
    cfg = AvatarConfig(name="TESTUSER", action="run", animated=False)

    jpg_bytes = render_cozy_avatar(snap, avatar_cfg=cfg, time_str="14:30", animated=False)
    assert isinstance(jpg_bytes, bytes)
    assert jpg_bytes.startswith(b"\xff\xd8")

    im = Image.open(io.BytesIO(jpg_bytes))
    assert im.size == (240, 240)
    assert im.format == "JPEG"

def test_all_avatar_actions():
    providers = MockCollector().collect_all()
    snap = DashboardSnapshot(timestamp=datetime.now(timezone.utc), providers=tuple(providers))

    for act in ["run", "desk", "coffee", "sleep", "auto"]:
        cfg = AvatarConfig(name="DEMBS", action=act, animated=True)
        raw = render_cozy_avatar(snap, avatar_cfg=cfg, time_str="22:00", animated=True)
        assert len(raw) > 5000
