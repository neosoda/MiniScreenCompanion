"""Autonomous, deterministic wall-clock behavior for the living companion.

Display polling frequency must never control the character's daily rhythm.
No inference of coding activity is made from missing or simulated quota data.
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple

from .models import DashboardSnapshot


class TamagotchiBrain:
    """Small time-driven state machine; returns (action, French status label)."""

    def __init__(self):
        self._last_snapshot: Optional[DashboardSnapshot] = None
        self._started_at: Optional[datetime] = None
        self._last_activity_at: Optional[datetime] = None
        self._focus_until: Optional[datetime] = None
        self._current_action = "desk"
        self._current_mood = "Dans le flow"

    @staticmethod
    def _new_activity(previous: DashboardSnapshot, current: DashboardSnapshot) -> bool:
        previous_providers = {p.provider_id: p for p in previous.providers if p.available}
        for provider in current.providers:
            old = previous_providers.get(provider.provider_id)
            if not provider.available or old is None:
                continue
            if provider.session_5h is None or old.session_5h is None:
                continue
            # Reset windows make percentages go DOWN. Only genuine increases
            # can suggest consumption, and repeated snapshots are ignored.
            diff = provider.session_5h.used_pct - old.session_5h.used_pct
            if diff >= 0.1:
                return True
        return False

    def update(
        self,
        snapshot: DashboardSnapshot,
        hour: Optional[int] = None,
        now: Optional[datetime] = None,
    ) -> Tuple[str, str]:
        now = now or datetime.now()
        current_hour = now.hour if hour is None else hour

        if self._started_at is None or now < self._started_at:
            self._started_at = now

        previous = self._last_snapshot
        if previous is None or snapshot.timestamp != previous.timestamp:
            if previous is not None and self._new_activity(previous, snapshot):
                self._last_activity_at = now
                self._focus_until = now + timedelta(minutes=3)
            self._last_snapshot = snapshot

        if current_hour >= 23 or current_hour < 7:
            self._current_action, self._current_mood = "sleep", "Zzz..."
            return self._current_action, self._current_mood

        if self._focus_until is not None and now < self._focus_until:
            self._current_action = "desk"
            self._current_mood = "En plein code !"
            return self._current_action, self._current_mood

        reference = self._last_activity_at or self._started_at
        idle_seconds = max(0.0, (now - reference).total_seconds())

        if current_hour >= 23 or current_hour < 7:
            self._current_action, self._current_mood = "sleep", "Zzz..."
        elif idle_seconds < 180:
            self._current_action, self._current_mood = "desk", "Dans le flow"
        else:
            # Every 4 minutes at most, rather than each call / HTTP refresh.
            phases = (
                ("coffee", "Pause cafe"),
                ("pet", "Calin au chat"),
                ("run", "Petite balade"),
            )
            phase = int((idle_seconds - 180) // 240) % len(phases)
            self._current_action, self._current_mood = phases[phase]

        return self._current_action, self._current_mood
