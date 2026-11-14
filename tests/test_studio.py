"""Companion Studio: loopback HTTP, validated preview, and persisted settings."""
import io
import json
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest
from PIL import Image

from mini_screen_companion.core.config import AppConfig, AvatarConfig
from mini_screen_companion.studio import coerce_avatar, create_studio_server


def test_profile_validation():
    current = AvatarConfig()
    candidate = coerce_avatar({
        "name": "Neo", "scene": "rain", "palette": "mint", "fps": 8,
        "action": "coffee", "show_cat": False, "effects": True,
    }, current)
    assert candidate.name == "Neo"
    assert candidate.scene == "rain"
    assert not candidate.show_cat
    assert current.show_cat
    for payload in (
        {"scene": "other"}, {"name": "X" * 40},
        {"fps": 1000}, {"show_cat": "false"},
        {"screen_host": "192.168.1.1"},
    ):
        with pytest.raises(ValueError):
            coerce_avatar(payload, current)


def test_studio_is_loopback_and_never_uploads(tmp_path):
    config_path = tmp_path / "config.json"
    server = create_studio_server(config_path, port=0, demo=True)
    assert server.server_address[0] == "127.0.0.1"
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = "http://127.0.0.1:" + str(server.server_port)
    try:
        with urlopen(base + "/api/config") as reply:
            data = json.load(reply)
            assert data["avatar"]["scene"] == "auto"

        with urlopen(base + "/api/preview?scene=rain&palette=mint&demo=1") as reply:
            assert reply.headers.get_content_type() == "image/gif"
            payload = reply.read()
        with Image.open(io.BytesIO(payload)) as image:
            assert image.size == (240, 240)
            assert image.n_frames == 8

        settings = json.dumps({"name": "Neo", "scene": "rain",
                               "palette": "mint", "action": "desk", "fps": 8,
                               "show_cat": False, "effects": True}).encode()
        blocked = Request(base + "/api/config", method="POST", data=settings,
                          headers={"Content-Type": "application/json",
                                   "Origin": "https://evil.example"})
        with pytest.raises(HTTPError) as err:
            urlopen(blocked)
        assert err.value.code == 403
        allowed = Request(base + "/api/config", method="POST", data=settings,
                          headers={"Content-Type": "application/json",
                                   "Origin": base})
        with urlopen(allowed) as reply:
            assert json.load(reply)["saved"] is True
        saved = AppConfig.load(str(config_path))
        assert saved.avatar.name == "Neo"
        assert saved.avatar.scene == "rain"
        assert saved.avatar.show_cat is False
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
