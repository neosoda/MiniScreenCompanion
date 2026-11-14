from typing import Optional, Tuple
from datetime import datetime
from .models import DashboardSnapshot

class TamagotchiBrain:
    """
    Autonomous living pet simulation brain.
    Reactions are driven by real coding quota changes, time of day, and idle rhythms.
    """
    def __init__(self):
        self._last_snapshot: Optional[DashboardSnapshot] = None
        self._idle_cycles: int = 0
        self._current_action: str = "desk"
        self._current_mood: str = "Dans le flow"

    def update(self, snapshot: DashboardSnapshot, hour: Optional[int] = None) -> Tuple[str, str]:
        if hour is None:
            hour = datetime.now().hour

        # 1. Detect if code was just generated (quota changed)
        code_activity = False
        if self._last_snapshot is not None:
            for p_curr in snapshot.providers:
                p_prev = next((p for p in self._last_snapshot.providers if p.provider_id == p_curr.provider_id), None)
                if p_prev and p_curr.session_5h and p_prev.session_5h:
                    # If used percentage changed or countdown progressed
                    if abs(p_curr.session_5h.used_pct - p_prev.session_5h.used_pct) >= 0.1:
                        code_activity = True
                        break

        self._last_snapshot = snapshot

        # 2. Activity detected -> Code Turbo mode!
        if code_activity:
            self._idle_cycles = 0
            self._current_action = "desk"
            coding_phrases = ["En plein hack !", "Dans le flow", "Mode Turbo !", "Ça code fort", "Full focus"]
            # Pick phrase based on current minute
            self._current_mood = coding_phrases[(datetime.now().minute // 2) % len(coding_phrases)]
            return self._current_action, self._current_mood

        # 3. Night hours (23h to 07h) -> Sleep time
        if 23 <= hour or hour < 7:
            self._current_action = "sleep"
            night_phrases = ["Dodo time", "Zzz...", "Au lit !", "Mode veille"]
            self._current_mood = night_phrases[(datetime.now().minute // 5) % len(night_phrases)]
            return self._current_action, self._current_mood

        # 4. Idle progression through the day
        self._idle_cycles += 1

        # Cycle of autonomous activities
        # 0..1: Coding at desk
        # 2..3: Pause café
        # 4..5: Câlin chat
        # 6..7: Petite trottinette / jog
        phase = (self._idle_cycles // 2) % 4

        if phase == 0:
            self._current_action = "desk"
            self._current_mood = "En dev..."
        elif phase == 1:
            self._current_action = "coffee"
            self._current_mood = "Pause café"
        elif phase == 2:
            self._current_action = "pet"
            self._current_mood = "Câlin chat"
        else:
            self._current_action = "run"
            self._current_mood = "Ça vib"

        return self._current_action, self._current_mood
