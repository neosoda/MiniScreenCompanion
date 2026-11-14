from abc import ABC, abstractmethod
from typing import Optional, List
from ..core.models import ProviderQuota

class BaseCollector(ABC):
    """Abstract interface for AI quota collectors."""

    @abstractmethod
    def collect(self) -> Optional[ProviderQuota]:
        """Collect quota data for a specific provider."""
        pass
