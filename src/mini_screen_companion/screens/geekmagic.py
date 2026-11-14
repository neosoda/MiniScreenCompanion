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
        self._slots_sanitized: bool = False

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
            h = {"Connection": "close"}
            # 1. Lock slot 1 and disable stock slideshow slots 2-5
            requests.get(f"{self.base_url}/file1-switch?getstate=1", headers=h, timeout=self.timeout)
            for slot in range(2, 6):
                requests.get(f"{self.base_url}/file{slot}-switch?getstate=0", headers=h, timeout=self.timeout)
            # Maximize slideshow delay to avoid spurious cycling
            requests.get(f"{self.base_url}/delaytime?getstate=60", headers=h, timeout=self.timeout)
            # 2. Select Photo display theme (Theme 2)
            r = requests.get(f"{self.base_url}/themeselect?getstate=2", headers=h, timeout=self.timeout)
            self._configured_photo_mode = (r.status_code == 200)
            logger.info("Screen configured into single-slot Photo mode (slideshow disabled).")
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

        jpeg_payload = image_bytes
        if image_bytes.startswith((b"GIF87a", b"GIF89a")):
            import io
            from PIL import Image
            try:
                with Image.open(io.BytesIO(image_bytes)) as gif:
                    gif.seek(0)
                    buf = io.BytesIO()
                    gif.convert("RGB").save(buf, format="JPEG", quality=80)
                    jpeg_payload = buf.getvalue()
            except Exception as ex:
                logger.warning(f"Could not convert GIF to JPEG for GeekMagic: {ex}")

        files = {"imageFile": ("file1.jpg", jpeg_payload, "image/jpeg")}
        try:
            r = requests.post(f"{self.base_url}/upload", files=files, headers={"Connection": "close"}, timeout=self.timeout)
            success = r.status_code == 200 or "successful" in r.text.lower()
        except requests.exceptions.RequestException as e:
            err_str = str(e).lower()
            success = "data after connection: close" in err_str or "upload successful" in err_str
            if not success:
                logger.error(f"Connection error uploading frame to {self.base_url}: {e}")
                return False

        if success:
            self._last_frame_hash = current_hash
            logger.debug("Frame uploaded successfully.")
            # Sanitize secondary slideshow slots (2-5) once so factory photos are permanently eradicated
            if not self._slots_sanitized:
                self._slots_sanitized = True
                for slot_idx in range(2, 6):
                    try:
                        s_files = {"imageFile": (f"file{slot_idx}.jpg", jpeg_payload, "image/jpeg")}
                        requests.post(f"{self.base_url}/upload", files=s_files, headers={"Connection": "close"}, timeout=self.timeout)
                    except Exception:
                        pass
            return True
        else:
            logger.error("Screen upload failed.")
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
