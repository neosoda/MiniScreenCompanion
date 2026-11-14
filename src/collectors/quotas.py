from __future__ import annotations

import json
import math
import os
import time
from pathlib import Path
from typing import Any, Optional

from src.collectors.base import QuotaMetrics


class QuotaCollector:
    """Read the local usage monitor cache without blocking hardware telemetry."""

    PROVIDERS = (("CLAUDE", "claude_code"), ("CODEX", "codex"), ("GEMINI", "antigravity_gemini"))

    def __init__(self, path: Optional[Path] = None, interval: float = 15.0):
        self.path = path or Path(os.environ.get("APPDATA", "")) / "ClaudeCodeUsageMonitor" / "usage-cache.json"
        self.interval = interval
        self._next_read = 0.0
        self._quotas = [QuotaMetrics(name) for name, _ in self.PROVIDERS]

    @staticmethod
    def _remaining(window: Any) -> Optional[float]:
        if not isinstance(window, dict) or window.get("available") is False:
            return None
        used = window.get("percentage")
        if isinstance(used, bool) or not isinstance(used, (int, float)) or not math.isfinite(used):
            return None
        return max(0.0, min(100.0, 100.0 - used))

    def collect(self) -> list[QuotaMetrics]:
        now = time.monotonic()
        if now < self._next_read:
            return self._quotas
        self._next_read = now + self.interval
        self._quotas = [QuotaMetrics(name) for name, _ in self.PROVIDERS]
        try:
            with self.path.open(encoding="utf-8") as cache:
                raw = json.load(cache)
            updated = raw.get("updated_unix")
            if isinstance(updated, bool) or not isinstance(updated, (int, float)) or not math.isfinite(updated):
                return self._quotas
            age = time.time() - updated
            if age > 600 or age < -60 or raw.get("poll_ok") is not True:
                return self._quotas
            data = raw.get("data")
            if not isinstance(data, dict):
                return self._quotas
            for index, (name, key) in enumerate(self.PROVIDERS):
                provider = data.get(key)
                if name == "GEMINI" and not provider:
                    provider = data.get("gemini") or data.get("antigravity")
                if isinstance(provider, dict):
                    self._quotas[index] = QuotaMetrics(name, self._remaining(provider.get("session")), self._remaining(provider.get("weekly")))
        except (OSError, ValueError, TypeError, AttributeError):
            pass
        return self._quotas
