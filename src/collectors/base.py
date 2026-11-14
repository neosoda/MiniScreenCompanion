from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CpuMetrics:
    usage_percent: float = 0.0
    temperature_c: Optional[float] = None
    frequency_mhz: float = 0.0
    core_count: int = 0
    history: List[float] = field(default_factory=list)
    per_cpu: List[float] = field(default_factory=list)


@dataclass
class RamMetrics:
    usage_percent: float = 0.0
    used_gb: float = 0.0
    total_gb: float = 0.0
    available_gb: float = 0.0


@dataclass
class NetMetrics:
    down_speed_kb: float = 0.0
    up_speed_kb: float = 0.0
    total_recv_mb: float = 0.0
    total_sent_mb: float = 0.0
    down_history: List[float] = field(default_factory=list)
    up_history: List[float] = field(default_factory=list)


@dataclass
class GpuMetrics:
    available: bool = False
    name: str = "N/A"
    usage_percent: float = 0.0
    temperature_c: float = 0.0
    memory_used_mb: float = 0.0
    memory_total_mb: float = 0.0
    memory_percent: float = 0.0
    power_watts: float = 0.0
    history: List[float] = field(default_factory=list)


@dataclass
class QuotaMetrics:
    name: str
    session_remaining: Optional[float] = None
    weekly_remaining: Optional[float] = None


@dataclass
class TelemetrySnapshot:
    cpu: CpuMetrics = field(default_factory=CpuMetrics)
    ram: RamMetrics = field(default_factory=RamMetrics)
    net: NetMetrics = field(default_factory=NetMetrics)
    gpu: GpuMetrics = field(default_factory=GpuMetrics)
    uptime_seconds: float = 0.0
    hostname: str = ""
    timestamp_str: str = ""
    quotas: List[QuotaMetrics] = field(default_factory=list)
