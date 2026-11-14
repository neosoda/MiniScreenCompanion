import io
from PIL import Image
from mini_screen_companion.collectors.mock import MockCollector
from mini_screen_companion.core.models import DashboardSnapshot
from mini_screen_companion.renderers import render_summary, render_detail

def test_render_summary_dimensions_and_validity():
    providers = MockCollector().collect_all()
    snapshot = DashboardSnapshot(timestamp=providers[0].session_5h.resets_at, providers=tuple(providers))
    
    jpeg_bytes = render_summary(snapshot, time_str="12:34")
    assert isinstance(jpeg_bytes, bytes)
    assert len(jpeg_bytes) > 1000

    img = Image.open(io.BytesIO(jpeg_bytes))
    assert img.size == (240, 240)
    assert img.format == "JPEG"

def test_render_detail_dimensions():
    providers = MockCollector().collect_all()
    jpeg_bytes = render_detail(providers[0], page_idx=1, total_pages=3, time_str="12:34")
    assert isinstance(jpeg_bytes, bytes)

    img = Image.open(io.BytesIO(jpeg_bytes))
    assert img.size == (240, 240)
    assert img.format == "JPEG"

def test_render_determinism():
    providers = MockCollector().collect_all()
    snapshot = DashboardSnapshot(timestamp=providers[0].session_5h.resets_at, providers=tuple(providers))

    bytes_1 = render_summary(snapshot, time_str="10:00")
    bytes_2 = render_summary(snapshot, time_str="10:00")
    assert bytes_1 == bytes_2  # Pure deterministic rendering!
