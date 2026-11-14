import hashlib
import logging
import socket
import concurrent.futures
from typing import Optional, List, Tuple
import requests
from .base import BaseScreen

logger = logging.getLogger(__name__)

class GeekMagicScreen(BaseScreen):
    """
    Client for GeekMagic 'Smart Weather Clock' / SmallTV ESP8266 & ESP32 screens.
    Idempotent: skips network transmission when frame hash is unchanged.
    """
    def __init__(self, host: str = "192.168.1.4", port: int = 80, timeout: int = 8):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{self.host}:{self.port}"
        self._last_frame_hash: Optional[str] = None
        self._configured_photo_mode: bool = False

    def is_reachable(self) -> bool:
        try:
            r = requests.get(f"{self.base_url}/", timeout=self.timeout)
            return r.status_code == 200
        except Exception:
            return False

    def set_brightness(self, level: int) -> bool:
        level = max(2, min(99, level))
        try:
            r = requests.get(f"{self.base_url}/updateLEDBrightness?ledBrightness={level}", timeout=self.timeout)
            return r.status_code == 200
        except Exception as e:
            logger.warning(f"Failed to set screen brightness: {e}")
            return False

    def ensure_single_photo_mode(self) -> bool:
        if self._configured_photo_mode:
            return True
        try:
            # 1. Enable single-slot photo mode
            requests.get(f"{self.base_url}/file1-switch?getstate=1", timeout=self.timeout)
            for slot in range(2, 6):
                requests.get(f"{self.base_url}/file{slot}-switch?getstate=0", timeout=self.timeout)
            # 2. Switch theme to photo display (Theme 2)
            r = requests.get(f"{self.base_url}/themeselect?getstate=2", timeout=self.timeout)
            self._configured_photo_mode = (r.status_code == 200)
            logger.info("Screen configured into single-slot Photo mode.")
            return True
        except Exception as e:
            logger.warning(f"Could not enforce single photo mode: {e}")
            return False

    def upload_frame(self, image_bytes: bytes, force: bool = False) -> bool:
        # Idempotency check: Skip upload if image hash has not changed
        current_hash = hashlib.sha256(image_bytes).hexdigest()
        if not force and current_hash == self._last_frame_hash:
            logger.debug("Frame unchanged (SHA-256 match), skipping upload.")
            return True

        self.ensure_single_photo_mode()

        files = {"imageFile": ("file1.jpg", image_bytes, "image/jpeg")}
        try:
            r = requests.post(f"{self.base_url}/upload", files=files, timeout=self.timeout)
            if r.status_code == 200 or "successful" in r.text.lower():
                self._last_frame_hash = current_hash
                logger.debug("Frame uploaded successfully.")
                return True
            else:
                logger.error(f"Screen upload returned status {r.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            err_str = str(e).lower()
            if "data after connection: close" in err_str or "upload successful" in err_str:
                self._last_frame_hash = current_hash
                logger.debug(f"Handled benign firmware framing exception: {e}")
                return True
            logger.error(f"Connection error uploading frame to {self.base_url}: {e}")
            return False

    @classmethod
    def discover_on_subnet(cls, subnet_prefix: str = "192.168.1", max_workers: int = 50) -> List[Tuple[str, str]]:
        """
        Scan a local /24 subnet to find active GeekMagic / Smart Weather Clock devices.
        Returns a list of (ip_address, title/hostname).
        """
        found = []

        def probe_ip(ip: str):
            try:
                s = socket.socket()
                s.settimeout(0.3)
                s.connect((ip, 80))
                s.close()

                r = requests.get(f"http://{ip}/", timeout=1.0)
                if r.status_code == 200:
                    text = r.text
                    if "Smart Weather clock" in text or "WiFi-settings" in text or "file1" in text:
                        return (ip, "GeekMagic Smart Weather Clock")
            except Exception:
                pass
            return None

        ips = [f"{subnet_prefix}.{i}" for i in range(1, 255)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(probe_ip, ip) for ip in ips]
            for f in concurrent.futures.as_completed(futures):
                res = f.result()
                if res:
                    found.append(res)

        return found
