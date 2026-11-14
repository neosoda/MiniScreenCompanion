import json
import time
import logging
from typing import Optional
import serial

from .base import BaseScreen

logger = logging.getLogger(__name__)

class GeekMagicSerialScreen(BaseScreen):
    """Direct high-speed serial driver for GeekMagic running custom MiniCompanion firmware."""

    def __init__(self, port: str = "COM7", baudrate: int = 115200, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._serial: Optional[serial.Serial] = None

    def _get_serial(self) -> serial.Serial:
        if self._serial is None or not self._serial.is_open:
            s = serial.Serial()
            s.port = self.port
            s.baudrate = self.baudrate
            s.timeout = self.timeout
            s.open()
            s.dtr = False
            s.rts = False
            time.sleep(0.15)
            self._serial = s
        return self._serial

    def send_command(self, cmd: dict) -> bool:
        try:
            s = self._get_serial()
            payload = json.dumps(cmd).encode("utf-8") + b"\n"
            s.write(payload)
            deadline = time.time() + max(1.5, self.timeout)
            while time.time() < deadline:
                line = s.readline().decode("utf-8", errors="ignore").strip()
                if not line:
                    continue
                if "ok" in line or "pong" in line or "Ready" in line:
                    return True
            return False
        except Exception as e:
            logger.error(f"Serial communication failed on {self.port}: {e}")
            if self._serial:
                try:
                    self._serial.close()
                except Exception:
                    pass
                self._serial = None
            return False

    def is_reachable(self) -> bool:
        try:
            return self.send_command({"cmd": "ping"})
        except Exception:
            return False

    def upload_frame(self, image_bytes: bytes) -> bool:
        # Custom firmware renders the top avatar continuously at 20 FPS on-chip.
        # Calling upload_frame serves as a keepalive / health check.
        return True

    def update_hud(
        self,
        claude: int,
        codex: int,
        gemini: int,
        act: str = "idle",
        mood: str = "",
        msg: str = "",
        rot: Optional[int] = None
    ) -> bool:
        payload = {
            "claude": int(claude),
            "codex": int(codex),
            "gemini": int(gemini),
            "act": act,
            "mood": mood,
            "msg": msg
        }
        if rot is not None:
            payload["rot"] = rot
        return self.send_command(payload)

    def set_brightness(self, level: int) -> bool:
        return True

    def set_rotation(self, rot: int) -> bool:
        return self.send_command({"rot": rot})
