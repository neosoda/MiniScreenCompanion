from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple


@dataclass
class ScreenConfig:
    port: str = "AUTO"
    baudrate: int = 115200
    width: int = 480
    height: int = 320
    orientation: str = "landscape"  # "landscape" or "portrait"
    rotation: int = 0               # 0 or 180
    brightness: int = 80            # 0 to 100
    fps: int = 1


@dataclass
class TelemetryConfig:
    interval_sec: float = 0.05
    history_length: int = 30
    mode: str = "fluid"             # "fluid" (partial 400ms updates) or "full"
    full_sync_sec: float = 30.0


@dataclass
class ThemeConfig:
    background: Tuple[int, int, int] = (11, 15, 25)
    card_bg: Tuple[int, int, int] = (17, 24, 39)
    card_border: Tuple[int, int, int] = (31, 41, 55)
    card_inner: Tuple[int, int, int] = (24, 33, 50)
    cpu_accent: Tuple[int, int, int] = (0, 229, 255)
    ram_accent: Tuple[int, int, int] = (129, 140, 248)
    gpu_accent: Tuple[int, int, int] = (16, 185, 129)
    net_accent: Tuple[int, int, int] = (245, 158, 11)
    text_main: Tuple[int, int, int] = (243, 244, 246)
    text_muted: Tuple[int, int, int] = (156, 163, 175)
    good: Tuple[int, int, int] = (52, 211, 153)
    warn: Tuple[int, int, int] = (251, 191, 36)
    crit: Tuple[int, int, int] = (248, 113, 113)


@dataclass
class AppConfig:
    screen: ScreenConfig = field(default_factory=ScreenConfig)
    telemetry: TelemetryConfig = field(default_factory=TelemetryConfig)
    theme: ThemeConfig = field(default_factory=ThemeConfig)

    @classmethod
    def load(cls, path: Path | str | None = None) -> AppConfig:
        if path is None:
            path = Path(__file__).resolve().parent.parent / "config.json"
        p = Path(path)
        if not p.is_file():
            return cls()

        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)

            screen = ScreenConfig(**data.get("screen", {}))
            telemetry = TelemetryConfig(**data.get("telemetry", {}))

            theme_dict = data.get("theme", {})
            converted_theme = {}
            for k, v in theme_dict.items():
                if isinstance(v, list) and len(v) == 3:
                    converted_theme[k] = tuple(v)
                else:
                    converted_theme[k] = v
            theme = ThemeConfig(**converted_theme)

            return cls(screen=screen, telemetry=telemetry, theme=theme)
        except Exception:
            return cls()
