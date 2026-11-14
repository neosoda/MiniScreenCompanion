import os
import sys
import time
import signal
import logging
import argparse
import subprocess
from dataclasses import replace
from datetime import datetime
from pathlib import Path

from .core.config import AppConfig
from .core.lock import ProcessLock, is_pid_alive
from .collectors import get_dashboard_snapshot
from .renderers import render_summary, render_detail, render_cozy_avatar
from .screens import get_screen_client, GeekMagicScreen, LocalFileScreen
from .core.tamagotchi import TamagotchiBrain

def setup_logging(level_name: str = "INFO", log_file: str = "dashboard.log"):
    level = getattr(logging, level_name.upper(), logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        try:
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setFormatter(formatter)
            handlers.append(fh)
        except Exception:
            pass
    logging.basicConfig(level=level, handlers=handlers, force=True)

class CompanionApp:
    def __init__(self, config: AppConfig, use_mock: bool = False):
        self.config = config
        self.use_mock = use_mock
        self.screen = get_screen_client(config.screen)
        self.lock = ProcessLock()
        self.tamagotchi = TamagotchiBrain()

    def run_once(self) -> bool:
        logging.info(f"Target display: {self.screen.__class__.__name__} ({self.config.screen.host})")
        snapshot = get_dashboard_snapshot(self.config, use_mock=self.use_mock)
        logging.info(f"Collected {len(snapshot.providers)} provider quotas.")
        for p in snapshot.providers:
            s5 = f"{p.session_5h.remaining_pct:.0f}% ({p.session_5h.format_countdown()})" if p.session_5h else "N/A"
            w7 = f"{p.weekly_7d.remaining_pct:.0f}% ({p.weekly_7d.format_countdown()})" if p.weekly_7d else "N/A"
            logging.info(f"  {p.display_name}: 5H={s5} | 7J={w7}")

        act_cfg = self.config.avatar
        mode = self.config.display.mode.lower()
        if mode in ("cozy", "retro", "avatar"):
            if act_cfg.action == "auto" or act_cfg.status == "auto":
                act, mood = self.tamagotchi.update(snapshot)
                act_cfg = replace(
                    act_cfg,
                    action=act if act_cfg.action == "auto" else act_cfg.action,
                    status=mood if act_cfg.status == "auto" else act_cfg.status
                )
            frame = render_cozy_avatar(snapshot, avatar_cfg=act_cfg,
                                       animated=not isinstance(self.screen, GeekMagicScreen))
        elif mode in ("claude", "codex", "gemini"):
            p = next((x for x in snapshot.providers if x.provider_id == mode), snapshot.providers[0])
            frame = render_detail(p)
        else:
            frame = render_summary(snapshot)

        ok = self.screen.upload_frame(frame)
        if ok:
            logging.info("Frame processed successfully (uploaded, unchanged or rate-limited).")
        else:
            logging.error("Failed to upload frame to screen.")
        return ok

    def run_loop(self):
        logging.info(f"Starting Mini Screen Companion daemon (mode: {self.config.display.mode})...")
        if not self.screen.is_reachable():
            logging.warning(f"Screen at {self.config.screen.host} is not currently responding. Will retry in loop.")

        if self.config.screen.brightness:
            self.screen.set_brightness(self.config.screen.brightness)

        interval = max(10, self.config.polling.refresh_interval_seconds)
        carousel_page = 0
        loop_counter = 0
        last_poll_time = 0.0
        snapshot = None

        running = True
        def handle_signal(sig, frame):
            nonlocal running
            logging.info("Shutting down companion gracefully...")
            running = False

        try:
            signal.signal(signal.SIGINT, handle_signal)
            signal.signal(signal.SIGTERM, handle_signal)
        except Exception:
            pass

        while running:
            try:
                now = time.time()
                if snapshot is None or (now - last_poll_time) >= interval:
                    snapshot = get_dashboard_snapshot(self.config, use_mock=self.use_mock)
                    last_poll_time = now

                time_str = datetime.now().strftime("%H:%M")
                mode = self.config.display.mode.lower()

                if mode in ("cozy", "retro", "avatar"):
                    act_cfg = self.config.avatar
                    if act_cfg.action == "auto" or act_cfg.status == "auto":
                        act, mood = self.tamagotchi.update(snapshot)
                        act_cfg = replace(
                            act_cfg,
                            action=act if act_cfg.action == "auto" else act_cfg.action,
                            status=mood if act_cfg.status == "auto" else act_cfg.status
                        )
                    is_photo_screen = isinstance(self.screen, GeekMagicScreen)
                    phase = int(now // 300) if is_photo_screen else loop_counter
                    frame = render_cozy_avatar(snapshot, avatar_cfg=act_cfg, time_str=time_str,
                                               animated=not is_photo_screen, frame_offset=phase)
                    loop_counter += 1
                    sleep_time = max(60, interval) if is_photo_screen else min(interval, 20)
                elif mode == "carousel" and snapshot.providers:
                    # Alternates Summary with large provider views
                    pages = ["summary"] + [p.provider_id for p in snapshot.providers]
                    curr = pages[carousel_page % len(pages)]
                    if curr == "summary":
                        frame = render_summary(snapshot, time_str=time_str)
                    else:
                        p = next((x for x in snapshot.providers if x.provider_id == curr), snapshot.providers[0])
                        idx = carousel_page % len(pages)
                        frame = render_detail(p, page_idx=idx, total_pages=len(pages)-1, time_str=time_str)
                    carousel_page += 1
                    sleep_time = self.config.display.carousel_page_duration_seconds
                elif mode in ("claude", "codex", "gemini"):
                    p = next((x for x in snapshot.providers if x.provider_id == mode), snapshot.providers[0])
                    frame = render_detail(p, page_idx=1, total_pages=1, time_str=time_str)
                    sleep_time = min(interval, 30)
                else:
                    frame = render_summary(snapshot, time_str=time_str)
                    sleep_time = min(interval, 30)

                self.screen.upload_frame(frame)
                time.sleep(sleep_time)

            except Exception as e:
                logging.error(f"Loop iteration error: {e}")
                time.sleep(10)

def cmd_studio(args):
    """Open local Companion Studio; no firmware or screen I/O."""
    from .studio import serve_studio
    serve_studio(config_path=args.config, port=args.port,
                 open_browser=not args.no_open, demo=args.demo)


def cmd_discover(args):
    """Scan local subnet for GeekMagic screens."""
    print("Scanning local subnet for GeekMagic smart screens...")
    prefix = args.subnet or "192.168.1"
    devices = GeekMagicScreen.discover_on_subnet(subnet_prefix=prefix)
    if not devices:
        print(f"No GeekMagic devices found on subnet {prefix}.0/24.")
    else:
        print(f"Found {len(devices)} device(s):")
        for ip, title in devices:
            print(f"  - {ip} ({title})")
        print("\nTo use this device, update your config.json with:")
        print(f'  "screen": {{ "host": "{devices[0][0]}" }}')

def cmd_preview(args):
    """Generate preview image and display it."""
    cfg = AppConfig.load(args.config)
    preview_file = args.output or ("preview.gif" if cfg.display.mode.lower() in ("cozy", "retro", "avatar") else "preview.jpg")
    screen = LocalFileScreen(output_path=preview_file)
    snapshot = get_dashboard_snapshot(cfg, use_mock=args.demo)

    mode = cfg.display.mode.lower()
    if mode in ("cozy", "retro", "avatar"):
        brain = TamagotchiBrain()
        act_cfg = cfg.avatar
        if act_cfg.action == "auto" or act_cfg.status == "auto":
            act, mood = brain.update(snapshot)
            act_cfg = replace(
                act_cfg,
                action=act if act_cfg.action == "auto" else act_cfg.action,
                status=mood if act_cfg.status == "auto" else act_cfg.status
            )
        frame = render_cozy_avatar(snapshot, avatar_cfg=act_cfg)
    elif mode in ("claude", "codex", "gemini"):
        p = next((x for x in snapshot.providers if x.provider_id == mode), snapshot.providers[0])
        frame = render_detail(p)
    else:
        frame = render_summary(snapshot)

    screen.upload_frame(frame, force=True)
    p_path = Path(preview_file).resolve()
    print(f"Preview generated: {p_path}")
    if p_path.suffix.lower() == ".gif":
        jpg_companion = p_path.with_suffix(".jpg")
        if jpg_companion.is_file():
            print(f"Static JPEG frame: {jpg_companion}")

    if args.open:
        try:
            target_open = str(p_path)
            if sys.platform.startswith("win"):
                os.startfile(target_open)
            elif sys.platform == "darwin":
                subprocess.run(["open", target_open])
            else:
                subprocess.run(["xdg-open", target_open])
        except Exception:
            pass

def cmd_status(args):
    """Check running companion status."""
    lock = ProcessLock()
    pid = lock.is_running()
    if pid:
        print(f"Mini Screen Companion is RUNNING (PID {pid}).")
    else:
        print("Mini Screen Companion is STOPPED.")

def cmd_stop(args):
    """Stop the running background daemon."""
    lock = ProcessLock()
    pid = lock.is_running()
    if not pid:
        print("No companion daemon running.")
        return
    print(f"Stopping companion daemon (PID {pid})...")
    try:
        if sys.platform.startswith("win"):
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
        else:
            os.kill(pid, signal.SIGTERM)
        time.sleep(1)
        if not is_pid_alive(pid):
            lock.release()
            print("Successfully stopped.")
        else:
            print(f"Process {pid} still running.")
    except Exception as e:
        print(f"Failed to stop process {pid}: {e}")

def main():
    parser = argparse.ArgumentParser(
        prog="mini-screen",
        description="Mini Screen Companion — AI Quota Desktop Monitor"
    )
    parser.add_argument("-c", "--config", default="config.json", help="Path to config.json")
    parser.add_argument("--demo", action="store_true", help="Use realistic demonstration data without credentials")

    subparsers = parser.add_subparsers(dest="command")

    # run / daemon
    p_run = subparsers.add_parser("run", help="Run monitor loop in foreground")
    p_run.add_argument("--demo", action="store_true", help="Use realistic demonstration data without credentials")

    p_daemon = subparsers.add_parser("daemon", help="Run monitor loop as managed daemon")
    p_daemon.add_argument("--demo", action="store_true", help="Use realistic demonstration data without credentials")

    # once
    p_once = subparsers.add_parser("once", help="Refresh quotas and upload single frame, then exit")
    p_once.add_argument("--demo", action="store_true", help="Use realistic demonstration data without credentials")

    # preview
    p_prev = subparsers.add_parser("preview", help="Render and save preview image locally")
    p_prev.add_argument("-o", "--output", default=None, help="Output file path")
    p_prev.add_argument("--open", action="store_true", help="Open image viewer automatically")
    p_prev.add_argument("--demo", action="store_true", help="Use realistic demonstration data without credentials")

    # Studio — local browser UI; never uploads to the device.
    p_studio = subparsers.add_parser("studio", help="Open local Living Companion visual editor")
    p_studio.add_argument("--port", type=int, default=8765, help="Local-only web port")
    p_studio.add_argument("--no-open", action="store_true", help="Do not launch a browser")
    p_studio.add_argument("--demo", action="store_true", help="Use fake quotas in preview only")

    # discover
    p_disc = subparsers.add_parser("discover", help="Scan local network for GeekMagic screens")
    p_disc.add_argument("--subnet", default="192.168.1", help="Subnet prefix (default: 192.168.1)")

    # status / stop
    subparsers.add_parser("status", help="Check background daemon status")
    subparsers.add_parser("stop", help="Stop background daemon")

    args = parser.parse_args()

    if args.command == "discover":
        cmd_discover(args)
        return
    elif args.command == "preview":
        cmd_preview(args)
        return
    elif args.command == "studio":
        cmd_studio(args)
        return
    elif args.command == "status":
        cmd_status(args)
        return
    elif args.command == "stop":
        cmd_stop(args)
        return

    # Load configuration
    cfg = AppConfig.load(args.config)
    setup_logging(cfg.logging.level, cfg.logging.file)
    app = CompanionApp(cfg, use_mock=args.demo)

    if args.command == "once":
        ok = app.run_once()
        sys.exit(0 if ok else 1)
    else: # run or daemon (default if no subcommand given)
        lock = ProcessLock()
        if lock.is_running():
            print(f"Error: Companion is already running (PID {lock.is_running()}). Use 'mini-screen stop' first.")
            sys.exit(1)
        with lock:
            app.run_loop()

if __name__ == "__main__":
    main()
