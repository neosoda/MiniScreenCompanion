from __future__ import annotations

import time
import logging
from typing import Optional
import numpy as np
import serial
import serial.tools.list_ports
from PIL import Image

logger = logging.getLogger("TuringDriver")


class TuringRevA:
    CMD_RESET = 101
    CMD_CLEAR = 102
    CMD_SCREEN_OFF = 108
    CMD_SCREEN_ON = 109
    CMD_SET_BRIGHTNESS = 110
    CMD_SET_ORIENTATION = 121
    CMD_DISPLAY_BITMAP = 197

    def __init__(
        self,
        port: str = "AUTO",
        baudrate: int = 115200,
        width: int = 480,
        height: int = 320,
        orientation: str = "landscape",
        brightness: int = 80,
        rotation: int = 0,
    ):
        self.configured_port = port
        self.baudrate = baudrate
        self.width = width
        self.height = height
        self.orientation = orientation.lower()
        self.brightness = max(0, min(100, brightness))
        self.rotation = rotation
        self.serial_port: Optional[serial.Serial] = None
        self.active_port_name: Optional[str] = None
        self._last_reconnect_attempt: float = 0.0

    @staticmethod
    def auto_detect_port() -> Optional[str]:
        ports = serial.tools.list_ports.comports()
        for p in ports:
            # Check for exact Turing 3.5 serial ID
            if p.serial_number and "USB35INCHIPSV2" in p.serial_number:
                return p.device
            # Check for QinHeng 1A86:5722
            if p.vid == 0x1A86 and p.pid == 0x5722:
                return p.device
        return None

    def connect(self) -> bool:
        port_name = self.configured_port
        if port_name.upper() == "AUTO":
            port_name = self.auto_detect_port()
            if not port_name:
                now = time.time()
                if now - self._last_reconnect_attempt > 5.0:
                    logger.warning("Turing 3.5 screen not found on any COM port.")
                    self._last_reconnect_attempt = now
                return False

        try:
            logger.info(f"Connecting to Turing 3.5 on {port_name} ({self.baudrate} baud)...")
            self.serial_port = serial.Serial(
                port_name,
                self.baudrate,
                timeout=1.0,
                write_timeout=1.0,
                rtscts=True,
            )
            self.active_port_name = port_name
            # Allow CH552T MCU CDC serial port to settle
            time.sleep(0.3)

            # Configure orientation & brightness
            self.apply_orientation()
            time.sleep(0.05)
            self.set_brightness(self.brightness)
            logger.info(f"Connected successfully on {port_name}.")
            return True
        except Exception as e:
            now = time.time()
            if now - self._last_reconnect_attempt > 5.0:
                logger.warning(f"Failed to connect to {port_name}: {e}")
                self._last_reconnect_attempt = now
            self.disconnect()
            return False

    def disconnect(self):
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.close()
            except Exception:
                pass
        self.serial_port = None
        self.active_port_name = None

    def is_connected(self) -> bool:
        return self.serial_port is not None and self.serial_port.is_open

    def _send_cmd(self, cmd: int, x: int = 0, y: int = 0, ex: int = 0, ey: int = 0):
        if not self.is_connected():
            return
        buf = bytearray(6)
        buf[0] = (x >> 2) & 0xFF
        buf[1] = (((x & 3) << 6) + (y >> 4)) & 0xFF
        buf[2] = (((y & 15) << 4) + (ex >> 6)) & 0xFF
        buf[3] = (((ex & 63) << 2) + (ey >> 8)) & 0xFF
        buf[4] = ey & 0xFF
        buf[5] = cmd & 0xFF
        try:
            self.serial_port.write(bytes(buf))
            self.serial_port.flush()
        except Exception:
            self.disconnect()

    def apply_orientation(self, force_portrait: bool = False):
        if not self.is_connected():
            return
        # orientation codes:
        # 0 = Portrait (320x480)
        # 1 = Reverse Portrait (320x480, 180 deg)
        # 2 = Landscape (480x320)
        # 3 = Reverse Landscape (480x320, 180 deg)
        if force_portrait:
            orient_code = 0
            w, h = self.height, self.width
        else:
            orient_str = str(self.orientation).lower()
            if "reverse_landscape" in orient_str or "reverse-landscape" in orient_str or orient_str == "3":
                orient_code = 3
                w, h = self.width, self.height
            elif "reverse_portrait" in orient_str or "reverse-portrait" in orient_str or orient_str == "1":
                orient_code = 1
                w, h = self.height, self.width
            elif "portrait" in orient_str or orient_str == "0":
                orient_code = 0
                w, h = self.height, self.width
            else:
                orient_code = 2
                w, h = self.width, self.height

        buf = bytearray(16)
        buf[5] = self.CMD_SET_ORIENTATION
        buf[6] = (orient_code + 100) & 0xFF
        buf[7] = (w >> 8) & 0xFF
        buf[8] = w & 0xFF
        buf[9] = (h >> 8) & 0xFF
        buf[10] = h & 0xFF
        try:
            self.serial_port.write(bytes(buf))
            self.serial_port.flush()
            time.sleep(0.05)
        except Exception:
            self.disconnect()

    def set_brightness(self, level: int):
        self.brightness = max(0, min(100, level))
        if not self.is_connected():
            return
        # 0 is brightest, 255 is darkest in hardware protocol
        raw_val = int(255 - ((self.brightness / 100.0) * 255))
        self._send_cmd(self.CMD_SET_BRIGHTNESS, raw_val, 0, 0, 0)

    def screen_off(self):
        if self.is_connected():
            self._send_cmd(self.CMD_SCREEN_OFF)

    def screen_on(self):
        if self.is_connected():
            self._send_cmd(self.CMD_SCREEN_ON)

    def clear(self):
        if not self.is_connected():
            return
        # Revision A firmware requires portrait orientation before clearing
        self.apply_orientation(force_portrait=True)
        self._send_cmd(self.CMD_CLEAR)
        self.apply_orientation()

    def display_pil_image(self, img: Image.Image) -> bool:
        if not self.is_connected():
            if not self.connect():
                return False

        try:
            if img.size != (self.width, self.height):
                img = img.resize((self.width, self.height), Image.Resampling.BILINEAR)

            if self.rotation == 180:
                img = img.rotate(180)

            if img.mode != "RGB":
                img = img.convert("RGB")

            # Fast vectorized RGB565 little-endian conversion
            rgb = np.asarray(img).reshape((-1, 3))
            r = (rgb[:, 0] >> 3).astype(np.uint16)
            g = (rgb[:, 1] >> 2).astype(np.uint16)
            b = (rgb[:, 2] >> 3).astype(np.uint16)
            raw_rgb565 = ((r << 11) | (g << 5) | b).astype("<u2").tobytes()

            # Send DISPLAY_BITMAP header
            self._send_cmd(self.CMD_DISPLAY_BITMAP, 0, 0, self.width - 1, self.height - 1)

            # Stream chunks
            chunk_size = self.width * 8
            total_bytes = len(raw_rgb565)
            for offset in range(0, total_bytes, chunk_size):
                self.serial_port.write(raw_rgb565[offset: offset + chunk_size])
            self.serial_port.flush()

            return True
        except (serial.SerialException, serial.SerialTimeoutException, OSError) as e:
            logger.warning(f"Serial communication error: {e}. Reconnecting on next tick...")
            self.disconnect()
            return False

    def display_partial(self, img: Image.Image, x: int, y: int) -> bool:
        if not self.is_connected():
            if not self.connect():
                return False

        try:
            w, h = img.size
            if w <= 0 or h <= 0:
                return True

            if self.rotation == 180:
                img = img.rotate(180)
                x = self.width - x - w
                y = self.height - y - h

            if img.mode != "RGB":
                img = img.convert("RGB")

            x0 = max(0, min(self.width - 1, int(x)))
            y0 = max(0, min(self.height - 1, int(y)))
            x1 = max(x0, min(self.width - 1, int(x + w - 1)))
            y1 = max(y0, min(self.height - 1, int(y + h - 1)))

            rgb = np.asarray(img).reshape((-1, 3))
            r = (rgb[:, 0] >> 3).astype(np.uint16)
            g = (rgb[:, 1] >> 2).astype(np.uint16)
            b = (rgb[:, 2] >> 3).astype(np.uint16)
            raw = ((r << 11) | (g << 5) | b).astype("<u2").tobytes()

            self._send_cmd(self.CMD_DISPLAY_BITMAP, x0, y0, x1, y1)
            self.serial_port.write(raw)
            self.serial_port.flush()
            return True
        except (serial.SerialException, serial.SerialTimeoutException, OSError) as e:
            logger.warning(f"Partial serial error: {e}")
            self.disconnect()
            return False
