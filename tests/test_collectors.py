from mini_screen_companion.collectors.mock import MockCollector
from mini_screen_companion.collectors.plugin_cache import PluginCacheCollector

def test_mock_collector():
    collector = MockCollector()
    providers = collector.collect_all()
    assert len(providers) == 3
    ids = [p.provider_id for p in providers]
    assert "claude" in ids
    assert "codex" in ids
    assert "gemini" in ids

def test_plugin_cache_parser_empty():
    collector = PluginCacheCollector(cache_path="non_existent_file.json")
    assert not collector.is_available()
    assert collector.collect_all() == []

def test_plugin_cache_parser_valid():
    raw_sample = {
        "data": {
            "claude_code": {
                "session": {"percentage": 15.5, "reset_seconds": 3600, "available": True},
                "weekly": {"percentage": 50.0, "reset_seconds": 86400, "available": True}
            }
        }
    }
    collector = PluginCacheCollector()
    parsed = collector._parse_cache(raw_sample)
    assert len(parsed) == 1
    p = parsed[0]
    assert p.provider_id == "claude"
    assert p.session_5h.used_pct == 15.5
    assert p.session_5h.remaining_pct == 84.5
