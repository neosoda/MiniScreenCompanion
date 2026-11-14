import os
import json
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional

@dataclass
class ScreenConfig:
    type: str = "geekmagic"
    host: str = "192.168.1.4"
    port: int = 80
    timeout: int = 8
    brightness: int = 85
    min_upload_interval_seconds: int = 300  # Limit stock photo-mode flash writes

@dataclass
class DisplayConfig:
    mode: str = "summary"
    carousel_page_duration_seconds: int = 10

@dataclass
class AvatarConfig:
    name: str = ""
    status: str = "auto"
    action: str = "run"    # "run", "desk", "coffee", "pet", "sleep", "auto"
    animated: bool = True
    fps: int = 8
    metric: str = "remaining"   # "remaining" or "used"
    scene: str = "auto"        # auto, day, night, rain
    palette: str = "warm"      # warm, mint, lavender
    show_cat: bool = True
    effects: bool = True

@dataclass
class PollingConfig:
    refresh_interval_seconds: int = 60
    retry_delay_seconds: int = 20

@dataclass
class LoggingConfig:
    level: str = "INFO"
    file: str = "dashboard.log"

@dataclass
class AppConfig:
    screen: ScreenConfig = field(default_factory=ScreenConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)
    avatar: AvatarConfig = field(default_factory=AvatarConfig)
    polling: PollingConfig = field(default_factory=PollingConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    providers: Dict[str, Any] = field(default_factory=lambda: {
        "claude": {"enabled": True},
        "codex": {"enabled": True},
        "antigravity": {"enabled": True}
    })

    @classmethod
    def load(cls, path: Optional[str] = None) -> "AppConfig":
        cfg = cls()
        config_file = Path(path) if path else Path("config.json")
        
        if config_file.is_file():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                if "screen" in data:
                    s = data["screen"]
                    cfg.screen = ScreenConfig(
                        type=s.get("type", cfg.screen.type),
                        host=s.get("host", cfg.screen.host),
                        port=s.get("port", cfg.screen.port),
                        timeout=s.get("timeout", cfg.screen.timeout),
                        brightness=s.get("brightness", cfg.screen.brightness),
                        min_upload_interval_seconds=max(30, int(s.get(
                            "min_upload_interval_seconds", cfg.screen.min_upload_interval_seconds)))
                    )
                if "display" in data:
                    d = data["display"]
                    cfg.display = DisplayConfig(
                        mode=d.get("mode", cfg.display.mode),
                        carousel_page_duration_seconds=d.get("carousel_page_duration_seconds", cfg.display.carousel_page_duration_seconds)
                    )
                if "avatar" in data:
                    a = data["avatar"]
                    cfg.avatar = AvatarConfig(
                        name=a.get("name", cfg.avatar.name),
                        status=a.get("status", cfg.avatar.status),
                        action=a.get("action", cfg.avatar.action),
                        animated=a.get("animated", cfg.avatar.animated),
                        fps=a.get("fps", cfg.avatar.fps),
                        metric=a.get("metric", cfg.avatar.metric),
                        scene=a.get("scene", cfg.avatar.scene),
                        palette=a.get("palette", cfg.avatar.palette),
                        show_cat=a.get("show_cat", cfg.avatar.show_cat),
                        effects=a.get("effects", cfg.avatar.effects)
                    )
                if "polling" in data:
                    p = data["polling"]
                    cfg.polling = PollingConfig(
                        refresh_interval_seconds=p.get("refresh_interval_seconds", cfg.polling.refresh_interval_seconds),
                        retry_delay_seconds=p.get("retry_delay_seconds", cfg.polling.retry_delay_seconds)
                    )
                if "logging" in data:
                    l = data["logging"]
                    cfg.logging = LoggingConfig(
                        level=l.get("level", cfg.logging.level),
                        file=l.get("file", cfg.logging.file)
                    )
                if "providers" in data:
                    cfg.providers = data["providers"]
            except (OSError, ValueError, TypeError, KeyError) as e:
                raise ValueError(f"Invalid config file {config_file}: {e}") from e

        # Environment variable overrides
        if "AI_SCREEN_HOST" in os.environ:
            cfg.screen.host = os.environ["AI_SCREEN_HOST"]
        if "AI_SCREEN_PORT" in os.environ:
            try:
                cfg.screen.port = int(os.environ["AI_SCREEN_PORT"])
            except ValueError:
                pass
        if "AI_SCREEN_MODE" in os.environ:
            cfg.display.mode = os.environ["AI_SCREEN_MODE"]
        if "AI_SCREEN_BRIGHTNESS" in os.environ:
            try:
                cfg.screen.brightness = int(os.environ["AI_SCREEN_BRIGHTNESS"])
            except ValueError:
                pass

        return cfg

    def save(self, path: str = "config.json"):
        data = {
            "screen": {
                "type": self.screen.type,
                "host": self.screen.host,
                "port": self.screen.port,
                "timeout": self.screen.timeout,
                "brightness": self.screen.brightness,
                "min_upload_interval_seconds": self.screen.min_upload_interval_seconds
            },
            "display": {
                "mode": self.display.mode,
                "carousel_page_duration_seconds": self.display.carousel_page_duration_seconds
            },
            "avatar": {
                "name": self.avatar.name,
                "status": self.avatar.status,
                "action": self.avatar.action,
                "animated": self.avatar.animated,
                "fps": self.avatar.fps,
                "metric": self.avatar.metric,
                "scene": self.avatar.scene,
                "palette": self.avatar.palette,
                "show_cat": self.avatar.show_cat,
                "effects": self.avatar.effects
            },
            "polling": {
                "refresh_interval_seconds": self.polling.refresh_interval_seconds,
                "retry_delay_seconds": self.polling.retry_delay_seconds
            },
            "providers": self.providers,
            "logging": {
                "level": self.logging.level,
                "file": self.logging.file
            }
        }
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp",
                                          dir=str(target.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary, target)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
