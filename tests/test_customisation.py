"""Visual customisation regression checks for the Living Companion V2 renderer."""
import io
from datetime import datetime, timezone
from PIL import Image

from mini_screen_companion.core.config import AvatarConfig
from mini_screen_companion.core.models import DashboardSnapshot
from mini_screen_companion.renderers.cozy_avatar import render_cozy_avatar
from mini_screen_companion.renderers.effects import draw_atmosphere


SNAPSHOT = DashboardSnapshot(timestamp=datetime(2026, 11, 14, tzinfo=timezone.utc),
                             providers=())


def rgb(raw):
    with Image.open(io.BytesIO(raw)) as frame:
        return frame.convert("RGB").copy()


def test_palettes_change_wall_colour():
    warm = rgb(render_cozy_avatar(SNAPSHOT, AvatarConfig(action="desk", palette="warm"),
                                  time_str="13:00", animated=False))
    mint = rgb(render_cozy_avatar(SNAPSHOT, AvatarConfig(action="desk", palette="mint"),
                                  time_str="13:00", animated=False))
    assert warm.getpixel((4, 27)) != mint.getpixel((4, 27))


def test_user_can_hide_cat():
    with_cat = rgb(render_cozy_avatar(
        SNAPSHOT, AvatarConfig(action="desk", show_cat=True),
        time_str="13:00", animated=False))
    without_cat = rgb(render_cozy_avatar(
        SNAPSHOT, AvatarConfig(action="desk", show_cat=False),
        time_str="13:00", animated=False))
    assert with_cat.getpixel((179, 69)) != without_cat.getpixel((179, 69))


def test_scene_rain_moves_across_frames():
    a = Image.new("RGBA", (240, 240))
    b = Image.new("RGBA", (240, 240))
    draw_atmosphere(a, "rain", 0, "coffee")
    draw_atmosphere(b, "rain", 1, "coffee")
    assert a.tobytes() != b.tobytes()
    assert a.getpixel((180, 120)) == (0, 0, 0, 0)


def test_static_render_accepts_arbitrary_frame_offset():
    for action in ("desk", "coffee", "pet", "sleep", "run"):
        for offset in (0, 3, 7):
            out = render_cozy_avatar(
                SNAPSHOT, AvatarConfig(action=action, show_cat=False),
                time_str="08:00", animated=False, frame_offset=offset)
            assert out.startswith(b"\xff\xd8")


def test_sleep_preview_time_and_palette():
    one = rgb(render_cozy_avatar(SNAPSHOT, AvatarConfig(action="auto", scene="auto"),
                                 time_str="23:00", animated=False))
    two = rgb(render_cozy_avatar(SNAPSHOT, AvatarConfig(action="auto", scene="auto"),
                                 time_str="13:00", animated=False))
    assert one.getpixel((4, 27)) != two.getpixel((4, 27))
