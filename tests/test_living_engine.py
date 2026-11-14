from datetime import datetime, timedelta, timezone

from mini_screen_companion.core.models import DashboardSnapshot, ProviderQuota, QuotaWindow
from mini_screen_companion.core.tamagotchi import TamagotchiBrain


def snapshot(when, used):
    return DashboardSnapshot(timestamp=when, providers=(
        ProviderQuota(provider_id="codex", display_name="Codex",
                      session_5h=QuotaWindow(used_pct=used)),))


def test_idle_states_are_time_driven_not_poll_count():
    brain = TamagotchiBrain()
    start = datetime(2026, 11, 14, 12, 0)
    base = snapshot(datetime(2026, 11, 14, 11, 0, tzinfo=timezone.utc), 25)
    assert brain.update(base, now=start)[0] == "desk"
    for _ in range(100):
        assert brain.update(base, now=start + timedelta(seconds=15))[0] == "desk"
    assert brain.update(base, now=start + timedelta(minutes=4))[0] == "coffee"
    assert brain.update(base, now=start + timedelta(minutes=8))[0] == "pet"
    assert brain.update(base, now=start + timedelta(minutes=12))[0] == "run"


def test_real_consumption_triggers_temporary_focus():
    brain = TamagotchiBrain()
    now = datetime(2026, 11, 14, 12, 0)
    t = datetime(2026, 11, 14, 12, 0, tzinfo=timezone.utc)
    brain.update(snapshot(t, 20), now=now)
    brain.update(snapshot(t + timedelta(seconds=30), 20.5),
                 now=now + timedelta(minutes=5))
    assert brain.update(snapshot(t + timedelta(seconds=30), 20.5),
                        now=now + timedelta(minutes=6))[0] == "desk"


def test_reset_or_absent_quota_does_not_trigger_focus():
    brain = TamagotchiBrain()
    now = datetime(2026, 11, 14, 12, 0)
    t = datetime(2026, 11, 14, 12, 0, tzinfo=timezone.utc)
    brain.update(snapshot(t, 99), now=now)
    result = brain.update(snapshot(t + timedelta(minutes=4), 0),
                          now=now + timedelta(minutes=4))
    assert result[0] == "coffee"


def test_sleep_at_night():
    brain = TamagotchiBrain()
    local = datetime(2026, 11, 14, 23, 15)
    t = datetime(2026, 11, 14, 23, 15, tzinfo=timezone.utc)
    assert brain.update(snapshot(t, 20), now=local)[0] == "sleep"
