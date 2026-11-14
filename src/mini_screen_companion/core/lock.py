import os
import sys
import time
from pathlib import Path
from typing import Optional

def is_pid_alive(pid: int) -> bool:
    """Check if a process with given PID is currently active."""
    if pid <= 0:
        return False
    if sys.platform.startswith("win"):
        import ctypes
        kernel32 = ctypes.windll.kernel32
        SYNCHRONIZE = 0x00100000
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION | SYNCHRONIZE, False, pid)
        if handle:
            kernel32.CloseHandle(handle)
            return True
        return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False

class ProcessLock:
    """
    Idempotent single-instance file lock.
    Guarantees only one companion daemon runs simultaneously.
    """
    def __init__(self, lock_file: str = ".companion.lock"):
        self.lock_path = Path(lock_file)

    def is_running(self) -> Optional[int]:
        if not self.lock_path.is_file():
            return None
        try:
            content = self.lock_path.read_text(encoding="utf-8").strip()
            if not content:
                return None
            pid = int(content.split()[0])
            if is_pid_alive(pid):
                return pid
            # Stale lockfile
            self.lock_path.unlink(missing_ok=True)
            return None
        except Exception:
            return None

    def acquire(self) -> bool:
        running_pid = self.is_running()
        if running_pid:
            return False
        try:
            self.lock_path.write_text(f"{os.getpid()} {time.time()}\n", encoding="utf-8")
            return True
        except Exception:
            return False

    def release(self):
        try:
            if self.lock_path.is_file():
                content = self.lock_path.read_text(encoding="utf-8").strip()
                if content and int(content.split()[0]) == os.getpid():
                    self.lock_path.unlink(missing_ok=True)
        except Exception:
            pass

    def __enter__(self):
        if not self.acquire():
            pid = self.is_running()
            raise RuntimeError(f"Mini Screen Companion is already running (PID {pid}).")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
