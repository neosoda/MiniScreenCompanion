import io
from datetime import datetime, timezone

from PIL import Image

from mini_screen_companion.collectors.mock import MockCollector
from mini_screen_companion.core.config import AvatarConfig
from mini_screen_companion.core.models import DashboardSnapshot
from mini_screen_companion.renderers.ambient import create_ambient_cat
from mini_screen_companion.renderers.cozy_avatar import render_cozy_avatar


def test_cat_moves_without_firmware():
    one = create_ambient_cat(0)
    two = create_ambient_cat(3)
    assert one.size == two.size == (30, 20)
    assert one.tobytes() != two.tobytes()


def test_night_background_and_local_animation():
    snap = DashboardSnapshot(
        timestamp=datetime.now(timezone.utc),
        providers=tuple(MockCollector().collect_all()),
    )
    cfg = AvatarConfig(name="DEMO", action="sleep", animated=True)
    raw = render_cozy_avatar(snap, cfg, time_str="23:10", animated=True)
    with Image.open(io.BytesIO(raw)) as im:
        assert im.n_frames == 8
        im.seek(0)
        assert im.convert("RGB").getpixel((1, 20))[2] < 100


def test_factory_preview_is_single_jpeg():
    snap = DashboardSnapshot(
        timestamp=datetime.now(timezone.utc),
        providers=tuple(MockCollector().collect_all()),
    )
    raw = render_cozy_avatar(snap, AvatarConfig(action="desk"), time_str="13:10",
                             animated=False, frame_offset=4)
    with Image.open(io.BytesIO(raw)) as im:
        assert im.format == "JPEG"
        assert im.size == (240, 240)
