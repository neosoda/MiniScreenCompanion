"""Quota snapshot assembly. NEVER silently substitute demo data in production."""
import logging
from datetime import datetime, timezone

from ..core.models import DashboardSnapshot, ProviderQuota
from ..core.config import AppConfig
from .plugin_cache import PluginCacheCollector
from .mock import MockCollector

logger = logging.getLogger(__name__)

PROVIDERS = (
    ("claude", "Claude Code", "claude"),
    ("codex", "Codex", "codex"),
    ("gemini", "Gemini", "antigravity"),
)


def get_dashboard_snapshot(config: AppConfig, use_mock: bool = False) -> DashboardSnapshot:
    now = datetime.now(timezone.utc)

    if use_mock:
        readings = MockCollector(now).collect_all()
    else:
        collector = PluginCacheCollector()
        readings = collector.collect_all() if collector.is_available() else []
        if not readings:
            logger.warning("No live quota cache available. Quotas will show unavailable (use --demo for sample values).")

    by_id = {provider.provider_id: provider for provider in readings}
    providers = []
    for provider_id, label, config_key in PROVIDERS:
        options = config.providers.get(config_key, config.providers.get(provider_id, {}))
        if isinstance(options, dict) and not options.get("enabled", True):
            continue

        reading = by_id.get(provider_id)
        if reading is not None and reading.available and (
            reading.session_5h is not None or reading.weekly_7d is not None
        ):
            providers.append(reading)
        else:
            providers.append(ProviderQuota(
                provider_id=provider_id,
                display_name=label,
                available=False,
                error_message="Donnees indisponibles",
            ))

    return DashboardSnapshot(timestamp=now, providers=tuple(providers))
