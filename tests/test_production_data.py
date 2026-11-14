from unittest.mock import patch

from mini_screen_companion.core.config import AppConfig
from mini_screen_companion.collectors import get_dashboard_snapshot
from mini_screen_companion.core.models import ProviderQuota, QuotaWindow


def test_missing_cache_does_not_fabricate_quota_percentages():
    with patch("mini_screen_companion.collectors.PluginCacheCollector") as collector:
        collector.return_value.is_available.return_value = False
        snapshot = get_dashboard_snapshot(AppConfig())
    assert len(snapshot.providers) == 3
    assert all(not p.available for p in snapshot.providers)
    assert all(p.session_5h is None for p in snapshot.providers)


def test_partial_cache_keeps_remaining_providers_unavailable():
    with patch("mini_screen_companion.collectors.PluginCacheCollector") as collector:
        collector.return_value.is_available.return_value = True
        collector.return_value.collect_all.return_value = [
            ProviderQuota("claude", "Claude Code", session_5h=QuotaWindow(used_pct=5))
        ]
        snapshot = get_dashboard_snapshot(AppConfig())
    assert snapshot.providers[0].available
    assert not snapshot.providers[1].available
    assert not snapshot.providers[2].available


def test_demo_is_explicit():
    snapshot = get_dashboard_snapshot(AppConfig(), use_mock=True)
    assert len(snapshot.providers) == 3
    assert all(p.available for p in snapshot.providers)
