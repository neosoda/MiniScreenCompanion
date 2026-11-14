from datetime import datetime, timezone, timedelta
from mini_screen_companion.core.models import QuotaWindow, ProviderQuota, DashboardSnapshot

def test_quota_window_immutability():
    w = QuotaWindow(used_pct=34.0, reset_seconds=3600)
    assert w.remaining_pct == 66.0
    try:
        w.used_pct = 50.0  # Immutable!
        assert False, "Should have raised exception"
    except Exception:
        pass

def test_countdown_formatting():
    now = datetime(2026, 11, 14, 10, 0, 0, tzinfo=timezone.utc)
    
    # 45 minutes
    w1 = QuotaWindow(used_pct=10.0, resets_at=now + timedelta(minutes=45))
    assert w1.format_countdown(now) == "45m"

    # 3 hours 20 mins
    w2 = QuotaWindow(used_pct=10.0, resets_at=now + timedelta(hours=3, minutes=20))
    assert w2.format_countdown(now) == "3h20m"

    # 2 days 4 hours
    w3 = QuotaWindow(used_pct=10.0, resets_at=now + timedelta(days=2, hours=4))
    assert w3.format_countdown(now) == "2j04h"

    # Past / Zero
    w4 = QuotaWindow(used_pct=10.0, resets_at=now)
    assert w4.format_countdown(now) == "imminent"

def test_dashboard_snapshot_structure():
    now = datetime.now(timezone.utc)
    p = ProviderQuota(provider_id="claude", display_name="Claude Code")
    snap = DashboardSnapshot(timestamp=now, providers=(p,))
    assert len(snap.providers) == 1
    assert snap.providers[0].provider_id == "claude"
