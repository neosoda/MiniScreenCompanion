import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from ..core.models import ProviderQuota, QuotaWindow
from ..core.paths import find_usage_monitor_cache

logger = logging.getLogger(__name__)

class PluginCacheCollector:
    """
    Collects real-time AI quota stats from ClaudeCodeUsageMonitor's usage-cache.json.
    Non-intrusive, read-only cache synchronization.
    """
    def __init__(self, cache_path: Optional[str] = None):
        self.cache_path = Path(cache_path) if cache_path else find_usage_monitor_cache()

    def is_available(self) -> bool:
        return self.cache_path is not None and self.cache_path.is_file()

    def collect_all(self) -> List[ProviderQuota]:
        if not self.is_available():
            return []

        try:
            with open(self.cache_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return self._parse_cache(raw)
        except Exception as e:
            logger.warning(f"Failed to read usage monitor cache at {self.cache_path}: {e}")
            return []

    def _parse_cache(self, raw: dict) -> List[ProviderQuota]:
        data = raw.get("data", {})
        results = []

        # 1. Claude Code
        claude_raw = data.get("claude_code", {})
        if claude_raw:
            s_5h = self._parse_window(claude_raw.get("session"))
            w_7d = self._parse_window(claude_raw.get("weekly"))
            results.append(ProviderQuota(
                provider_id="claude",
                display_name="Claude Code",
                session_5h=s_5h,
                weekly_7d=w_7d,
                available=True
            ))

        # 2. OpenAI Codex
        codex_raw = data.get("codex", {})
        if codex_raw:
            s_5h = self._parse_window(codex_raw.get("session"))
            w_7d = self._parse_window(codex_raw.get("weekly"))
            results.append(ProviderQuota(
                provider_id="codex",
                display_name="Codex",
                session_5h=s_5h,
                weekly_7d=w_7d,
                available=True
            ))

        # 3. Google Gemini / Antigravity
        gemini_raw = data.get("gemini", {})
        if gemini_raw:
            s_5h = self._parse_window(gemini_raw.get("session"))
            w_7d = self._parse_window(gemini_raw.get("weekly"))
            results.append(ProviderQuota(
                provider_id="gemini",
                display_name="Gemini",
                session_5h=s_5h,
                weekly_7d=w_7d,
                available=True
            ))

        return results

    def _parse_window(self, win_data: Optional[dict]) -> Optional[QuotaWindow]:
        if not win_data or not win_data.get("available", True):
            return None

        used = float(win_data.get("percentage", 0.0))
        r_dt = None

        resets_at = win_data.get("resets_at")
        if isinstance(resets_at, dict):
            secs = resets_at.get("secs_since_epoch")
            if secs:
                r_dt = datetime.fromtimestamp(secs, tz=timezone.utc)
        elif isinstance(resets_at, (int, float)):
            r_dt = datetime.fromtimestamp(resets_at, tz=timezone.utc)
        elif isinstance(resets_at, str):
            try:
                r_dt = datetime.fromisoformat(resets_at.replace("Z", "+00:00"))
            except ValueError:
                pass

        reset_seconds = win_data.get("reset_seconds")
        if reset_seconds is not None:
            reset_seconds = int(reset_seconds)

        return QuotaWindow(used_pct=used, resets_at=r_dt, reset_seconds=reset_seconds)
