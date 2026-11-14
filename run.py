#!/usr/bin/env python3
from __future__ import annotations

import argparse
import atexit
import ctypes
from ctypes import wintypes
import logging
import os
from pathlib import Path
import sys
import time
import psutil

# Ensure sys.stdout and sys.stderr are valid under pythonw.exe
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR))

PID_FILE = PROJECT_DIR / ".companion.pid"
MUTEX_NAME = "Global\\Turing35CompanionRunningMutex"
_mutex_handle = None


def acquire_mutex():
    global _mutex_handle
    try:
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.CreateMutexW(None, True, MUTEX_NAME)
        last_error = kernel32.GetLastError()
        ERROR_ALREADY_EXISTS = 183
        if last_error == ERROR_ALREADY_EXISTS:
            if handle:
                kernel32.CloseHandle(handle)
            return False, None
        _mutex_handle = handle
        return True, handle
    except Exception:
        # Fallback to PID file check if ctypes mutex fails
        return True, None


def release_mutex():
    global _mutex_handle
    if _mutex_handle:
        try:
            ctypes.windll.kernel32.ReleaseMutex(_mutex_handle)
            ctypes.windll.kernel32.CloseHandle(_mutex_handle)
        except Exception:
            pass
        _mutex_handle = None


def get_running_pid() -> int | None:
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            if psutil.pid_exists(pid):
                proc = psutil.Process(pid)
                if "python" in proc.name().lower():
                    return pid
        except Exception:
            pass
    return None


def stop_running_instance():
    pid = get_running_pid()
    stopped = False
    if pid:
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            proc.wait(timeout=2.0)
            stopped = True
        except Exception:
            try:
                proc.kill()
                stopped = True
            except Exception:
                pass

    if PID_FILE.exists():
        try:
            PID_FILE.unlink()
        except Exception:
            pass
    return stopped, pid


def cleanup_on_exit():
    release_mutex()
    try:
        if PID_FILE.exists():
            my_pid = os.getpid()
            recorded_pid = int(PID_FILE.read_text().strip())
            if recorded_pid == my_pid:
                PID_FILE.unlink()
    except Exception:
        pass


atexit.register(cleanup_on_exit)

from src.config import AppConfig
from src.engine import TuringCompanionEngine


def main():
    parser = argparse.ArgumentParser(description="Turing 3.5' PC Stats Cockpit Companion")
    parser.add_argument("--simulate", action="store_true", help="Run without physical hardware (saves preview.png)")
    parser.add_argument("--port", type=str, default=None, help="Force specific COM port (e.g. COM3)")
    parser.add_argument("--brightness", type=int, default=None, help="Screen brightness (0-100)")
    parser.add_argument("--interval", type=float, default=None, help="Update interval in seconds (default: 1.0)")
    parser.add_argument("--rotation", type=int, choices=[0, 180], default=None, help="Screen rotation (0 or 180)")
    parser.add_argument("--test", action="store_true", help="Render single frame, send to screen and exit")
    parser.add_argument("--stop", action="store_true", help="Stop background running instance")
    parser.add_argument("--restart", action="store_true", help="Restart running instance")
    parser.add_argument("--status", action="store_true", help="Check companion status")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose debug logging")

    args = parser.parse_args()

    # CLI Actions: Stop / Status / Restart
    if args.stop:
        stopped, pid = stop_running_instance()
        if stopped:
            print(f"[OK] Turing 3.5 Companion (PID {pid}) stopped.")
        else:
            print("[INFO] No running instance found.")
        return

    if args.status:
        pid = get_running_pid()
        if pid:
            try:
                proc = psutil.Process(pid)
                mem_mb = proc.memory_info().rss / (1024 * 1024)
                print(f"[RUNNING] Turing 3.5 Companion is active (PID: {pid}, Memory: {mem_mb:.1f} MB)")
            except Exception:
                print(f"[RUNNING] Turing 3.5 Companion is active (PID: {pid})")
        else:
            print("[STOPPED] Turing 3.5 Companion is not running.")
        return

    if args.restart:
        stop_running_instance()
        time.sleep(1.0)

    # Single instance lock check
    if not args.test:
        ok, _ = acquire_mutex()
        if not ok:
            running_pid = get_running_pid()
            msg = f"Another instance is already running (PID: {running_pid}). Exiting."
            print(msg)
            sys.exit(0)

        PID_FILE.write_text(str(os.getpid()))

    log_level = logging.DEBUG if args.verbose else logging.INFO
    log_file = PROJECT_DIR / "companion.log"

    handlers = [logging.FileHandler(log_file, encoding="utf-8")]
    if sys.stderr is not None and not sys.stderr.closed and hasattr(sys.stderr, "isatty"):
        handlers.append(logging.StreamHandler(sys.stderr))

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        handlers=handlers,
    )

    def _handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.critical("Uncaught top-level exception:", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = _handle_exception

    config = AppConfig.load()
    if args.port:
        config.screen.port = args.port
    if args.brightness is not None:
        config.screen.brightness = args.brightness
    if args.interval is not None:
        config.telemetry.interval_sec = args.interval
    if args.rotation is not None:
        config.screen.rotation = args.rotation

    engine = TuringCompanionEngine(config=config, simulate=args.simulate)

    if args.test:
        logging.info("Rendering single test snapshot...")
        snap = engine._collect_snapshot()
        img = engine.renderer.render(snap)
        preview_path = PROJECT_DIR / "preview.png"
        img.save(preview_path, "PNG")
        logging.info(f"Test frame saved to {preview_path}")

        if not args.simulate and engine.driver.connect():
            engine.driver.display_pil_image(img)
            engine.driver.disconnect()
            logging.info("Test frame successfully displayed on Turing 3.5 screen!")
        return

    engine.start()


if __name__ == "__main__":
    main()
