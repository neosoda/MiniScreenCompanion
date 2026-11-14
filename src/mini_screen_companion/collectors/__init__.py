import logging
from datetime import datetime, timezone
from typing import List
from ..core.models import DashboardSnapshot, ProviderQuota
from ..core.config import AppConfig
from .plugin_cache import PluginCacheCollector
from .mock import MockCollector

logger = logging.getLogger(__name__)

def get_dashboard_snapshot(config: AppConfig, use_mock: bool = False) -> DashboardSnapshot:
    """
    Collect quotas across configured providers and return an immutable DashboardSnapshot.
    Falls back gracefully if plugin cache is not present.
    """
    now = datetime.now(timezone.utc)
    
    if use_mock:
        providers = MockCollector(now).collect_all()
        return DashboardSnapshot(timestamp=now, providers=tuple(providers))

    # 1. Try local plugin cache collector
    cache_collector = PluginCacheCollector()
    if cache_collector.is_available():
        providers = cache_collector.collect_all()
        if providers:
            logger.debug(f"Collected {len(providers)} providers from active cache.")
            return DashboardSnapshot(timestamp=now, providers=tuple(providers))

    # 2. Fallback to mock / demo if no collector succeeded
    logger.info("No active usage cache detected. Using demonstration data. Start your CLI or configure credentials.")
    mock_providers = MockCollector(now).collect_all()
    return DashboardSnapshot(timestamp=now, providers=tuple(mock_providers))
