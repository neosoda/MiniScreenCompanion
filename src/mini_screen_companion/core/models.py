from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Tuple

@dataclass(frozen=True)
class QuotaWindow:
    """Immutable representation of a time-bounded AI quota window."""
    used_pct: float
    resets_at: Optional[datetime] = None
    reset_seconds: Optional[int] = None

    @property
    def remaining_pct(self) -> float:
        return max(0.0, min(100.0, 100.0 - self.used_pct))

    def format_countdown(self, now: Optional[datetime] = None) -> str:
        secs = None
        if self.reset_seconds is not None and self.reset_seconds >= 0:
            secs = self.reset_seconds
        elif self.resets_at is not None:
            if now is None:
                now = datetime.now(timezone.utc)
            delta = (self.resets_at - now).total_seconds()
            secs = max(0, int(delta))

        if secs is None:
            return "--"
        if secs == 0:
            return "imminent"

        days = secs // 86400
        hours = (secs % 86400) // 3600
        mins = (secs % 3600) // 60

        if days >= 2:
            return f"{days}j{hours:02d}h" if hours > 0 else f"{days}j"
        elif days == 1:
            return f"1j{hours:02d}h"
        elif hours > 0:
            return f"{hours}h{mins:02d}m"
        return f"{mins}m"

@dataclass(frozen=True)
class ProviderQuota:
    """Immutable representation of an AI provider's quota state."""
    provider_id: str
    display_name: str
    session_5h: Optional[QuotaWindow] = None
    weekly_7d: Optional[QuotaWindow] = None
    available: bool = True
    error_message: str = ""

@dataclass(frozen=True)
class DashboardSnapshot:
    """Immutable point-in-time snapshot of all monitored AI quotas."""
    timestamp: datetime
    providers: Tuple[ProviderQuota, ...]
