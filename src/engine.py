from __future__ import annotations

import logging
import signal
import sys
import time
from typing import Optional
import numpy as np

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

        # Update Interval (support sub-second high-speed partial updates)
        self.interval_sec = max(0.05, float(self.config.telemetry.interval_sec or 0.25))
        self.mode = getattr(self.config.telemetry, "mode", "fluid").lower()
        self.full_sync_sec = float(getattr(self.config.telemetry, "full_sync_sec", 60.0))
        self._prev_frame_arr: Optional[np.ndarray] = None
        self._last_full_sync: float = 0.0

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

        # Cockpit UI quadrants for micro-blit dirty rect tracking
        zones = [
            (385, 0, 480, 28),    # Header: Digital Clock
            (195, 0, 285, 28),    # Header: Uptime Pill
            (6, 30, 238, 177),    # Card 1: CPU Tachometer, Load Matrix, Temp
            (242, 30, 474, 177),  # Card 2: GPU Tachometer, Power, VRAM
            (6, 177, 238, 316),   # Card 3: RAM % + Network Oscilloscope
            (242, 177, 474, 316), # Card 4: AI Quotas Matrix
        ]

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

                # 4. Push frame to Turing display (Fluid micro-blit or full sync)
                now_sync = time.perf_counter()
                use_partial = (
                    self.mode in ("fluid", "micro_blit", "partial", "turbo")
                    and hasattr(self.driver, "display_partial")
                )
                need_full = (
                    not use_partial
                    or self._prev_frame_arr is None
                    or (now_sync - self._last_full_sync) >= self.full_sync_sec
                )

                if need_full:
                    success = self.driver.display_pil_image(frame_img)
                    if success:
                        self._prev_frame_arr = np.asarray(frame_img).copy()
                        self._last_full_sync = now_sync
                        fps_counter += 1
                    else:
                        logger.warning("Full frame send failed. Driver marked disconnected.")
                        self._prev_frame_arr = None
                else:
                    curr_arr = np.asarray(frame_img)
                    diff = np.any(curr_arr != self._prev_frame_arr, axis=-1)

                    if np.any(diff):
                        sent_any = False
                        all_ok = True
                        for (zx1, zy1, zx2, zy2) in zones:
                            sub_diff = diff[zy1:zy2, zx1:zx2]
                            if np.any(sub_diff):
                                rows = np.any(sub_diff, axis=1)
                                cols = np.any(sub_diff, axis=0)
                                ymin, ymax = np.where(rows)[0][[0, -1]]
                                xmin, xmax = np.where(cols)[0][[0, -1]]

                                bx1 = zx1 + xmin
                                by1 = zy1 + ymin
                                bx2 = zx1 + xmax + 1
                                by2 = zy1 + ymax + 1

                                sub_img = frame_img.crop((bx1, by1, bx2, by2))
                                ok = self.driver.display_partial(sub_img, bx1, by1)
                                if ok:
                                    sent_any = True
                                else:
                                    all_ok = False
                                    break

                        if all_ok:
                            self._prev_frame_arr = curr_arr
                            if sent_any:
                                fps_counter += 1
                        else:
                            logger.warning("Partial frame send failed. Resetting full sync.")
                            self._prev_frame_arr = None
                    else:
                        # Frame identical to previous one, skip hardware write
                        pass

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
                sleep_time = max(0.01, self.interval_sec - elapsed)
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
