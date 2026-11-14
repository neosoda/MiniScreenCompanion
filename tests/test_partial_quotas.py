"""Unavailable quota windows must not masquerade as actual zero-percent quotas."""
from datetime import datetime, timezone

from mini_screen_companion.core.models import ProviderQuota, QuotaWindow, DashboardSnapshot
from mini_screen_companion.renderers.cozy_avatar import render_quotas_2_3_panel, render_cozy_avatar
from mini_screen_companion.core.config import AvatarConfig


def test_unknown_window_is_distinct_from_zero_percent():
    partial = ProviderQuota(provider_id="codex", display_name="Codex",
                            session_5h=None, weekly_7d=QuotaWindow(used_pct=30))
    depleted = ProviderQuota(provider_id="codex", display_name="Codex",
                             session_5h=QuotaWindow(used_pct=100),
                             weekly_7d=QuotaWindow(used_pct=30))
    one = render_quotas_2_3_panel([partial])
    two = render_quotas_2_3_panel([depleted])
    assert one.size == two.size == (240, 160)
    assert one.tobytes() != two.tobytes()


def test_missing_both_windows_does_not_break_render():
    p = ProviderQuota(provider_id="claude", display_name="Claude Code",
                      session_5h=None, weekly_7d=None, available=True)
    snapshot = DashboardSnapshot(timestamp=datetime.now(timezone.utc), providers=(p,))
    raw = render_cozy_avatar(snapshot, AvatarConfig(action="desk"),
                             animated=False)
    assert raw.startswith(b"\xff\xd8")
