"""Transport tests: the official device's /upload is a flash-write path."""
import io
from unittest.mock import MagicMock, patch

from PIL import Image

from mini_screen_companion.screens.geekmagic import GeekMagicScreen


def jpeg(color=(20, 80, 130)):
    image = Image.new("RGB", (240, 240), color)
    out = io.BytesIO()
    image.save(out, format="JPEG")
    return out.getvalue()


def test_factory_upload_touches_only_photo_slot_1():
    screen = GeekMagicScreen("192.168.1.4", min_upload_interval_seconds=300)
    response = MagicMock(status_code=200, text="successful")
    with patch("mini_screen_companion.screens.geekmagic.requests.get", return_value=response), \
         patch("mini_screen_companion.screens.geekmagic.requests.post", return_value=response) as post, \
         patch("mini_screen_companion.screens.geekmagic.time.monotonic", return_value=100.0):
        assert screen.upload_frame(jpeg()) is True
        assert post.call_count == 1
        assert post.call_args.kwargs["files"]["imageFile"][0] == "file1.jpg"
        assert screen.upload_frame(jpeg((200, 20, 40))) is True
        assert post.call_count == 1  # Never hammer device flash.


def test_rejects_non_image_upload():
    screen = GeekMagicScreen("192.168.1.4")
    with patch("mini_screen_companion.screens.geekmagic.requests.post") as post:
        assert not screen.upload_frame(b"not a JPEG")
        post.assert_not_called()


def test_gif_is_flattened_not_streamed_to_stock_firmware():
    screen = GeekMagicScreen("192.168.1.4")
    image = Image.new("RGB", (240, 240), (55, 120, 30))
    out = io.BytesIO()
    image.save(out, format="GIF", save_all=True)
    response = MagicMock(status_code=200, text="successful")
    with patch("mini_screen_companion.screens.geekmagic.requests.get", return_value=response), \
         patch("mini_screen_companion.screens.geekmagic.requests.post", return_value=response) as post:
        assert screen.upload_frame(out.getvalue())
        assert post.call_args.kwargs["files"]["imageFile"][1].startswith(b"\xff\xd8")
