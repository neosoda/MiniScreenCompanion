import os
import sys
from pathlib import Path
from typing import Optional

def get_home_dir() -> Path:
    """Return the user's home directory in a cross-platform way."""
    return Path.home()

def get_app_data_dir(app_name: str) -> Path:
    """
    Return the standard application data directory for the current OS.
    - Windows: %APPDATA%/<app_name>
    - macOS: ~/Library/Application Support/<app_name>
    - Linux / Other: ~/.config/<app_name> or $XDG_CONFIG_HOME/<app_name>
    """
    if sys.platform.startswith("win"):
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / app_name
        return Path.home() / "AppData" / "Roaming" / app_name
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / app_name
    else:
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config:
            return Path(xdg_config) / app_name
        return Path.home() / ".config" / app_name

def find_usage_monitor_cache() -> Optional[Path]:
    """Auto-detect ClaudeCodeUsageMonitor usage-cache.json across platforms."""
    # 1. Standard OS AppData path
    standard = get_app_data_dir("ClaudeCodeUsageMonitor") / "usage-cache.json"
    if standard.is_file():
        return standard

    # 2. Check local AppData on Windows
    if sys.platform.startswith("win"):
        local_appdata = os.environ.get("LOCALAPPDATA")
        if local_appdata:
            loc = Path(local_appdata) / "ClaudeCodeUsageMonitor" / "usage-cache.json"
            if loc.is_file():
                return loc

    # 3. Check ~/.claude-usage-cache.json or current directory
    home_fallback = Path.home() / ".claude-usage-cache.json"
    if home_fallback.is_file():
        return home_fallback

    return None

def find_claude_credentials() -> Optional[Path]:
    """Auto-detect Claude CLI credentials."""
    env_path = os.environ.get("CLAUDE_CONFIG_DIR")
    if env_path:
        p = Path(env_path) / "credentials.json"
        if p.is_file():
            return p
    default_p = Path.home() / ".claude" / "credentials.json"
    return default_p if default_p.is_file() else None

def find_codex_auth() -> Optional[Path]:
    """Auto-detect OpenAI Codex auth credentials."""
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        p = Path(codex_home) / "auth.json"
        if p.is_file():
            return p
    default_p = Path.home() / ".codex" / "auth.json"
    return default_p if default_p.is_file() else None
