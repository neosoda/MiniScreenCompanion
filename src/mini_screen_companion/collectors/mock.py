from datetime import datetime, timezone, timedelta
from typing import List
from ..core.models import ProviderQuota, QuotaWindow

class MockCollector:
    """Provides realistic mock quota snapshots for offline preview, tests, and screenshots."""

    def __init__(self, now: datetime = None):
        self.now = now or datetime.now(timezone.utc)

    def collect_all(self) -> List[ProviderQuota]:
        return [
            ProviderQuota(
                provider_id="claude",
                display_name="Claude Code",
                session_5h=QuotaWindow(
                    used_pct=1.0,
                    resets_at=self.now + timedelta(hours=3, minutes=46),
                    reset_seconds=13560
                ),
                weekly_7d=QuotaWindow(
                    used_pct=66.0,  # 34% remaining
                    resets_at=self.now + timedelta(days=5, hours=3),
                    reset_seconds=442800
                ),
                available=True
            ),
            ProviderQuota(
                provider_id="codex",
                display_name="Codex",
                session_5h=QuotaWindow(
                    used_pct=0.0,
                    resets_at=self.now + timedelta(hours=4, minutes=59),
                    reset_seconds=17940
                ),
                weekly_7d=QuotaWindow(
                    used_pct=80.0,  # 20% remaining
                    resets_at=self.now + timedelta(days=4, hours=21),
                    reset_seconds=421200
                ),
                available=True
            ),
            ProviderQuota(
                provider_id="gemini",
                display_name="Gemini",
                session_5h=QuotaWindow(
                    used_pct=9.8,  # 90.2% remaining
                    resets_at=self.now + timedelta(hours=4, minutes=31),
                    reset_seconds=16260
                ),
                weekly_7d=QuotaWindow(
                    used_pct=2.8,  # 97.2% remaining
                    resets_at=self.now + timedelta(days=6, hours=23),
                    reset_seconds=601200
                ),
                available=True
            ),
        ]
