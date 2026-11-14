from __future__ import annotations

import logging
import signal
import sys
import time
from typing import Optional

from src.collectors import SystemCollector, GpuCollector, TelemetrySnapshot
from src.config import AppConfig
from src.driver import TuringRevA, SimulatorDriver
from src.renderer import CockpitRenderer

logger = logging.getLogger("TuringEngine")


class TuringCompanionEngine:
    """
    Main Companion Engine for Turing 3.5" Smart Screen.
    Architecture inspired by mathoudebine/turing-smart-screen-python:
    - Auto-port detection & resilient auto-reconnect
    - Native zero-overhead NVML GPU & psutil telemetry (< 0.2% CPU)
    - Paced, stable frame sync with zero serial queue saturation
    - Clean standby/shutdown screen on exit
    """

    def __init__(self, config: Optional[AppConfig] = None, simulate: bool = False):
        self.config = config or AppConfig.load()
        self.simulate = simulate
        self.running = False

        # Telemetry Collectors
        self.sys_collector = SystemCollector(history_length=self.config.telemetry.history_length)
        self.gpu_collector = GpuCollector(history_length=self.config.telemetry.history_length)
        from src.collectors.quotas import QuotaCollector
        self.quota_collector = QuotaCollector()

        # Cockpit Renderer (Visual Design preserved 100%)
        self.renderer = CockpitRenderer(
            width=self.config.screen.width,
            height=self.config.screen.height,
            theme=self.config.theme,
        )

        # Hardware or Simulator Driver
        if self.simulate:
            logger.info("Starting in SIMULATION mode (saving to preview.png)...")
            self.driver = SimulatorDriver(
                width=self.config.screen.width,
                height=self.config.screen.height,
            )
        else:
            self.driver = TuringRevA(
                port=self.config.screen.port,
                baudrate=self.config.screen.baudrate,
                width=self.config.screen.width,
                height=self.config.screen.height,
                orientation=self.config.screen.orientation,
                brightness=self.config.screen.brightness,
                rotation=self.config.screen.rotation,
            )

        # Update Interval (default: 1.0 second for calm, rock-solid monitoring)
        self.interval_sec = max(0.5, float(self.config.telemetry.interval_sec or 1.0))

    def _setup_signal_handlers(self):
        def _handler(sig, frame):
            logger.info("Shutdown signal received. Stopping companion cleanly...")
            self.stop()
            sys.exit(0)

        try:
            signal.signal(signal.SIGINT, _handler)
            signal.signal(signal.SIGTERM, _handler)
        except Exception:
            pass

    def _collect_snapshot(self) -> TelemetrySnapshot:
        return TelemetrySnapshot(
            cpu=self.sys_collector.collect_cpu(),
            ram=self.sys_collector.collect_ram(),
            net=self.sys_collector.collect_net(),
            gpu=self.gpu_collector.collect(),
            uptime_seconds=self.sys_collector.get_uptime_seconds(),
            hostname=self.sys_collector.hostname,
            timestamp_str=self.sys_collector.get_timestamp_str(),
            quotas=self.quota_collector.collect(),
        )

    def start(self):
        self.running = True
        self._setup_signal_handlers()

        logger.info("Initializing Turing 3.5 hardware driver...")
        connected = self.driver.connect()
        if not connected and not self.simulate:
            logger.warning("Waiting for Turing 3.5 hardware on COM port (auto-reconnect active)...")

        logger.info(f"Engine started: Interval = {self.interval_sec:.1f}s | NVML Native = {self.gpu_collector._is_available}")

        fps_counter = 0
        t0_fps = time.perf_counter()

        try:
            while self.running:
                loop_start = time.perf_counter()

                # 1. Verify connection / attempt auto-reconnect
                if not self.simulate and not self.driver.is_connected():
                    logger.debug("Attempting to reconnect to Turing 3.5...")
                    if not self.driver.connect():
                        time.sleep(2.0)
                        continue

                # 2. Collect hardware telemetry snapshot
                snap = self._collect_snapshot()

                # 3. Render dashboard frame
                frame_img = self.renderer.render(snap)

                # 4. Push frame to Turing display
                success = self.driver.display_pil_image(frame_img)
                if success:
                    fps_counter += 1
                else:
                    logger.warning("Frame send failed. Driver marked disconnected.")

                # Periodic performance logging (every ~15s)
                dt_fps = time.perf_counter() - t0_fps
                if dt_fps >= 15.0:
                    effective_fps = fps_counter / dt_fps
                    gpu_name = snap.gpu.name or "GPU"
                    logger.info(
                        f"STATS: {effective_fps:.1f} FPS | "
                        f"CPU: {snap.cpu.usage_percent:4.1f}% | "
                        f"{gpu_name}: {snap.gpu.usage_percent:4.1f}% ({snap.gpu.temperature_c:.0f}°C, {snap.gpu.power_watts:.0f}W) | "
                        f"RAM: {snap.ram.usage_percent:4.1f}% | "
                        f"NET: v {snap.net.down_speed_kb:5.1f} KB/s ^ {snap.net.up_speed_kb:5.1f} KB/s"
                    )
                    t0_fps = time.perf_counter()
                    fps_counter = 0

                # 5. Paced sleep to match interval precisely
                elapsed = time.perf_counter() - loop_start
                sleep_time = max(0.05, self.interval_sec - elapsed)
                time.sleep(sleep_time)

        except (KeyboardInterrupt, SystemExit):
            logger.info("Engine stopped by user.")
        except Exception as e:
            logger.exception(f"Unexpected error in engine loop: {e}")
        finally:
            self.stop()

    def stop(self):
        if not self.running:
            return
        self.running = False
        logger.info("Shutting down TuringCompanionEngine...")

        # Display clean standby screen
        try:
            if hasattr(self.driver, "display_pil_image") and self.driver.is_connected():
                standby_img = self.renderer.render_standby("COMPANION STANDBY")
                self.driver.display_pil_image(standby_img)
        except Exception:
            pass

        # Disconnect hardware
        try:
            if hasattr(self.driver, "disconnect"):
                self.driver.disconnect()
        except Exception:
            pass

        # Shutdown NVML
        try:
            self.gpu_collector.shutdown()
        except Exception:
            pass

        logger.info("Companion shutdown complete.")
