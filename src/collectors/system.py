from __future__ import annotations

import collections
import platform
import json
from pathlib import Path
import time
from datetime import datetime
import psutil

from src.collectors.base import CpuMetrics, RamMetrics, NetMetrics


class SystemCollector:
    def __init__(self, history_length: int = 30):
        self.history_length = max(5, history_length)
        self.cpu_history = collections.deque(maxlen=self.history_length)
        self.net_down_history = collections.deque(maxlen=self.history_length)
        self.net_up_history = collections.deque(maxlen=self.history_length)

        self._last_net = psutil.net_io_counters()
        self._last_net_time = time.perf_counter()
        self._boot_time = psutil.boot_time()
        self.hostname = platform.node()
        self._cpu_temperature = None
        self._temperature_next = 0.0

        # Prime CPU percent measurement
        psutil.cpu_percent(interval=None)

    def collect_cpu(self) -> CpuMetrics:
        # non-blocking call
        if platform.system() == "Windows" and time.monotonic() >= self._temperature_next:
            self._temperature_next = time.monotonic() + 15.0
            self._read_cpu_temperature()
        pct = psutil.cpu_percent(interval=None)
        per_cpu = psutil.cpu_percent(interval=None, percpu=True)
        freq_info = psutil.cpu_freq()
        freq = freq_info.current if freq_info else 0.0
        cores = psutil.cpu_count(logical=True) or 0

        self.cpu_history.append(pct)

        return CpuMetrics(
            usage_percent=pct,
            temperature_c=self._cpu_temperature,
            frequency_mhz=freq,
            core_count=cores,
            history=list(self.cpu_history),
            per_cpu=per_cpu,
        )

    def _read_cpu_temperature(self) -> None:
        try:
            path = Path(__file__).resolve().parents[2] / "cpu_temperature.json"
            with path.open(encoding="utf-8-sig") as cache:
                data = json.load(cache)
            value = float(data["temperature_c"])
            age = time.time() - float(data["updated_unix"])
            self._cpu_temperature = value if 0 < value < 150 and -60 <= age <= 30 else None
        except (OSError, ValueError, TypeError, KeyError):
            self._cpu_temperature = None

    def collect_ram(self) -> RamMetrics:
        mem = psutil.virtual_memory()
        used_gb = mem.used / (1024 ** 3)
        total_gb = mem.total / (1024 ** 3)
        avail_gb = mem.available / (1024 ** 3)

        return RamMetrics(
            usage_percent=mem.percent,
            used_gb=round(used_gb, 1),
            total_gb=round(total_gb, 1),
            available_gb=round(avail_gb, 1),
        )

    def collect_net(self) -> NetMetrics:
        now = time.perf_counter()
        dt = max(now - self._last_net_time, 0.001)

        current_net = psutil.net_io_counters()
        delta_recv = max(0, current_net.bytes_recv - self._last_net.bytes_recv)
        delta_sent = max(0, current_net.bytes_sent - self._last_net.bytes_sent)

        self._last_net = current_net
        self._last_net_time = now

        # Convert to KB/s
        down_kb = (delta_recv / 1024.0) / dt
        up_kb = (delta_sent / 1024.0) / dt

        self.net_down_history.append(down_kb)
        self.net_up_history.append(up_kb)

        return NetMetrics(
            down_speed_kb=round(down_kb, 1),
            up_speed_kb=round(up_kb, 1),
            total_recv_mb=round(current_net.bytes_recv / (1024 * 1024), 1),
            total_sent_mb=round(current_net.bytes_sent / (1024 * 1024), 1),
            down_history=list(self.net_down_history),
            up_history=list(self.net_up_history),
        )

    def get_uptime_seconds(self) -> float:
        return time.time() - self._boot_time

    def get_timestamp_str(self) -> str:
        return datetime.now().strftime("%H:%M:%S")
