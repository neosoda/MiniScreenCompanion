from __future__ import annotations

import time
from typing import Tuple, List
from PIL import Image, ImageDraw

from src.collectors.base import TelemetrySnapshot
from src.config import ThemeConfig
from src.renderer.fonts import FontManager
from src.renderer.widgets.gauge import draw_radial_tick_gauge
from src.renderer.widgets.led_bar import draw_segmented_bar


class CockpitRenderer:
    def __init__(self, width: int = 480, height: int = 320, theme: ThemeConfig | None = None):
        self.width = width
        self.height = height
        self.theme = theme or ThemeConfig()

        # Palettes
        self.C_BG = (6, 9, 15)
        self.C_CARD = (11, 17, 28)
        self.C_CARD_BORDER = (24, 36, 56)
        self.C_TRACK = (20, 30, 46)

        self.C_CYAN = (0, 240, 255)
        self.C_EMERALD = (16, 231, 117)
        self.C_PURPLE = (168, 85, 247)
        self.C_AMBER = (245, 158, 11)
        self.C_RED = (248, 113, 113)

        self.C_TEXT = (245, 247, 250)
        self.C_MUTED = (140, 155, 175)

    def render(self, snap: TelemetrySnapshot) -> Image.Image:
        img = Image.new("RGBA", (self.width, self.height), (*self.C_BG, 255))
        draw = ImageDraw.Draw(img)

        # 1. Header Bar
        self._render_header(draw, snap)

        # 2. Quadrants Layout (480x320)
        # Upper row: y: 32 to 175
        # Lower row: y: 179 to 314
        left_x1, left_x2 = 6, 238
        right_x1, right_x2 = 242, 474

        # Card 1: CPU Supercar Tachometer (Top-Left)
        self._render_cpu_card(img, draw, snap, (left_x1, 32, left_x2, 175))

        # Card 2: GPU Telemetry Tachometer (Top-Right)
        self._render_gpu_card(img, draw, snap, (right_x1, 32, right_x2, 175))

        # Card 3: RAM Memory Ladder (Bottom-Left)
        self._render_compact_system(draw, snap, (left_x1, 179, left_x2, 314))

        # Card 4: Network Oscilloscope (Bottom-Right)
        self._render_quotas(draw, snap, (right_x1, 179, right_x2, 314))

        return img.convert("RGB")

    def _render_compact_system(self, draw: ImageDraw.ImageDraw, snap: TelemetrySnapshot, rect: Tuple[int, int, int, int]):
        x1, y1, x2, y2 = rect
        self._render_card_base(draw, (x1, y1, x2, y1 + 64), self.C_PURPLE)
        self._render_card_base(draw, (x1, y1 + 69, x2, y2), self.C_AMBER)
        label = FontManager.get_font(12, bold=True)
        number = FontManager.get_font(22, bold=True)
        detail = FontManager.get_font(11, bold=False)
        draw.text((x1 + 10, y1 + 5), "RAM", fill=self.C_PURPLE, font=label)
        draw.text((x1 + 10, y1 + 23), f"{snap.ram.usage_percent:.0f}%", fill=self.C_TEXT, font=number)
        draw.text((x1 + 85, y1 + 25), f"{snap.ram.used_gb:.1f} / {snap.ram.total_gb:.1f} GB", fill=self.C_TEXT, font=detail)
        draw.text((x1 + 85, y1 + 41), f"Libre  {snap.ram.available_gb:.1f} GB", fill=self.C_MUTED, font=detail)
        draw.text((x1 + 10, y1 + 74), "NETWORK", fill=self.C_AMBER, font=label)
        def speed(kb: float) -> str:
            return f"{kb / 1024:.1f} MB/s" if kb >= 1024 else f"{kb:.0f} KB/s"
        draw.text((x1 + 10, y1 + 92), f"DN  {speed(snap.net.down_speed_kb)}", fill=self.C_CYAN, font=detail)
        draw.text((x1 + 10, y1 + 109), f"UP   {speed(snap.net.up_speed_kb)}", fill=self.C_AMBER, font=detail)
        draw.text((x1 + 126, y1 + 92), f"RX {snap.net.total_recv_mb / 1024:.1f} GB", fill=self.C_MUTED, font=detail)
        draw.text((x1 + 126, y1 + 109), f"TX {snap.net.total_sent_mb / 1024:.1f} GB", fill=self.C_MUTED, font=detail)

    def _render_quotas(self, draw: ImageDraw.ImageDraw, snap: TelemetrySnapshot, rect: Tuple[int, int, int, int]):
        x1, y1, x2, y2 = rect
        self._render_card_base(draw, rect, self.C_EMERALD)
        label = FontManager.get_font(12, bold=True)
        value = FontManager.get_font(12, bold=True)
        heading = FontManager.get_font(11, bold=True)
        draw.text((x1 + 10, y1 + 7), "QUOTAS IA", fill=self.C_EMERALD, font=label)
        draw.text((x1 + 97, y1 + 9), "5H", fill=self.C_MUTED, font=heading)
        draw.text((x1 + 164, y1 + 9), "7J", fill=self.C_MUTED, font=heading)
        quotas = {q.name: q for q in snap.quotas}
        for index, name in enumerate(("CLAUDE", "CODEX", "GEMINI")):
            y = y1 + 33 + index * 31
            quota = quotas.get(name)
            draw.text((x1 + 12, y + 5), name, fill=self.C_TEXT, font=label)
            for x, amount in ((x1 + 97, quota.session_remaining if quota else None),
                              (x1 + 164, quota.weekly_remaining if quota else None)):
                text = f"{amount:.0f}%" if amount is not None else "--"
                color = self.C_MUTED if amount is None else (self.C_RED if amount < 20 else self.C_EMERALD)
                draw.text((x, y - 2), text, fill=color, font=value)
                draw.rounded_rectangle((x, y + 15, x + 47, y + 21), radius=2, fill=self.C_TRACK)
                if amount is not None and amount > 0:
                    width = max(1, round(48 * min(100, max(0, amount)) / 100))
                    draw.rectangle((x, y + 15, x + width - 1, y + 21), fill=color)

    def _render_header(self, draw: ImageDraw.ImageDraw, snap: TelemetrySnapshot):
        font_sm = FontManager.get_font(11, bold=False)
        font_sm_bold = FontManager.get_font(12, bold=True)

        draw.rectangle([(0, 0), (self.width, 27)], fill=(9, 13, 22))
        draw.line([(0, 27), (self.width, 27)], fill=self.C_CARD_BORDER, width=1)

        # Pulsing Live Diode
        draw.ellipse([10, 9, 18, 17], fill=self.C_EMERALD)
        draw.text((24, 7), "NEO COCKPIT", fill=self.C_TEXT, font=font_sm_bold)

        host = snap.hostname.upper() if snap.hostname else "SYSTEM"
        draw.text((112, 8), f"// {host}", fill=self.C_CYAN, font=font_sm)

        # Center Uptime Pill
        uptime_h = int(snap.uptime_seconds // 3600)
        uptime_m = int((snap.uptime_seconds % 3600) // 60)
        uptime_str = f"UP {uptime_h}h {uptime_m:02d}m"
        draw.rounded_rectangle([(198, 4), (280, 22)], radius=4, fill=(16, 24, 38), outline=self.C_CARD_BORDER)
        draw.text((206, 6), uptime_str, fill=self.C_MUTED, font=font_sm)

        # Digital Clock (Right)
        clock_str = snap.timestamp_str or time.strftime("%H:%M:%S")
        draw.text((395, 6), clock_str, fill=self.C_TEXT, font=font_sm_bold)

    def _render_card_base(self, draw: ImageDraw.ImageDraw, rect: Tuple[int, int, int, int], accent_col: Tuple[int, int, int]):
        x1, y1, x2, y2 = rect
        draw.rounded_rectangle([x1, y1, x2, y2], radius=7, fill=self.C_CARD, outline=self.C_CARD_BORDER, width=1)
        # Tech bracket notch
        draw.line([(x1 + 6, y1), (x1 + 24, y1)], fill=accent_col, width=2)

    def _render_cpu_card(self, img: Image.Image, draw: ImageDraw.ImageDraw, snap: TelemetrySnapshot, rect: Tuple[int, int, int, int]):
        x1, y1, x2, y2 = rect
        self._render_card_base(draw, rect, self.C_CYAN)

        font_label = FontManager.get_font(12, bold=True)
        font_sub = FontManager.get_font(10, bold=False)
        font_metric = FontManager.get_font(26, bold=True)
        font_xs = FontManager.get_font(9, bold=False)

        # Header line
        draw.text((x1 + 10, y1 + 7), "CPU", fill=self.C_CYAN, font=font_label)
        freq_ghz = round(snap.cpu.frequency_mhz / 1000.0, 1) if snap.cpu.frequency_mhz else 0.0
        draw.text((x1 + 42, y1 + 8), f"// {freq_ghz} GHz · {snap.cpu.core_count}T", fill=self.C_MUTED, font=font_sub)
        cpu_temp = f"{snap.cpu.temperature_c:.0f}°C" if snap.cpu.temperature_c is not None else "--°C"
        cpu_temp_color = self.C_MUTED if snap.cpu.temperature_c is None else (self.C_RED if snap.cpu.temperature_c > 85 else self.C_CYAN)
        draw.text((x2 - 45, y1 + 7), cpu_temp, fill=cpu_temp_color, font=font_label)

        # Tachometer Arc (Center at x1 + 116, y1 + 64, radius 40)
        cx = x1 + (x2 - x1) // 2
        cy = y1 + 62
        pct = snap.cpu.usage_percent
        pct_color = self.C_RED if pct >= 85 else (self.C_AMBER if pct >= 70 else self.C_CYAN)

        draw_radial_tick_gauge(
            img,
            center=(cx, cy),
            radius=36,
            percent=pct,
            active_color=pct_color,
            track_color=self.C_TRACK,
            start_deg=140.0,
            total_deg=260.0,
            num_ticks=24,
            tick_length=8,
            major_tick_length=12,
            major_step=4,
        )

        # Big percentage in tachometer center
        pct_str = f"{int(pct)}%"
        draw.text((cx - 20, cy - 14), pct_str, fill=self.C_TEXT, font=font_metric)

        # Core Equalizer Activity (16 bars across bottom)
        eq_y = y2 - 8
        eq_x = x1 + 14
        eq_w = (x2 - x1) - 28
        cores = snap.cpu.per_cpu[:16] if snap.cpu.per_cpu else [pct] * 16
        num_cores = min(16, len(cores))
        bar_w = (eq_w - (num_cores - 1) * 3) // num_cores

        draw.text((x1 + 14, y2 - 32), "CORES LOAD MATRIX", fill=self.C_MUTED, font=font_xs)

        for i in range(num_cores):
            c_pct = cores[i]
            bx = eq_x + i * (bar_w + 3)
            bh = max(2, int((c_pct / 100.0) * 16))
            # Track
            draw.rectangle([(bx, eq_y - 16), (bx + bar_w, eq_y)], fill=(18, 26, 40))
            # Active
            b_col = self.C_RED if c_pct >= 85 else (self.C_AMBER if c_pct >= 60 else self.C_CYAN)
            draw.rectangle([(bx, eq_y - bh), (bx + bar_w, eq_y)], fill=b_col)

    def _render_gpu_card(self, img: Image.Image, draw: ImageDraw.ImageDraw, snap: TelemetrySnapshot, rect: Tuple[int, int, int, int]):
        x1, y1, x2, y2 = rect
        self._render_card_base(draw, rect, self.C_EMERALD)

        font_label = FontManager.get_font(12, bold=True)
        font_sub = FontManager.get_font(10, bold=False)
        font_metric = FontManager.get_font(26, bold=True)
        font_badge = FontManager.get_font(10, bold=True)
        font_xs = FontManager.get_font(9, bold=False)

        gpu_name = snap.gpu.name[:13] if snap.gpu.available else "GPU"
        draw.text((x1 + 10, y1 + 7), "GPU", fill=self.C_EMERALD, font=font_label)
        draw.text((x1 + 42, y1 + 8), f"// {gpu_name}", fill=self.C_MUTED, font=font_sub)

        # Temp Badge (Top Right)
        if snap.gpu.available:
            temp_str = f"{int(snap.gpu.temperature_c)}°C"
            temp_col = self.C_RED if snap.gpu.temperature_c > 80 else (self.C_AMBER if snap.gpu.temperature_c > 65 else self.C_EMERALD)
            badge_x = x2 - 46
            draw.rounded_rectangle([(badge_x, y1 + 6), (badge_x + 36, y1 + 20)], radius=3, fill=(18, 28, 42), outline=temp_col)
            draw.text((badge_x + 6, y1 + 7), temp_str, fill=temp_col, font=font_badge)

        # Tachometer Arc
        cx = x1 + (x2 - x1) // 2
        cy = y1 + 62
        pct = snap.gpu.usage_percent
        pct_color = self.C_RED if pct >= 90 else (self.C_AMBER if pct >= 75 else self.C_EMERALD)

        draw_radial_tick_gauge(
            img,
            center=(cx, cy),
            radius=36,
            percent=pct,
            active_color=pct_color,
            track_color=self.C_TRACK,
            start_deg=140.0,
            total_deg=260.0,
            num_ticks=24,
            tick_length=8,
            major_tick_length=12,
            major_step=4,
        )

        draw.text((cx - 20, cy - 14), f"{int(pct)}%", fill=self.C_TEXT, font=font_metric)

        # VRAM Segmented LED bar (Bottom of GPU card)
        vram_used = round(snap.gpu.memory_used_mb / 1024.0, 1)
        vram_total = round(snap.gpu.memory_total_mb / 1024.0, 1)
        vram_pct = snap.gpu.memory_percent

        draw.text((x1 + 14, y2 - 32), f"VRAM BUFFER {vram_used}/{vram_total} GB", fill=self.C_MUTED, font=font_xs)
        draw.text((x2 - 36, y2 - 32), f"{int(vram_pct)}%", fill=self.C_EMERALD, font=font_xs)

        draw_segmented_bar(
            draw,
            (x1 + 14, y2 - 18, x2 - 14, y2 - 8),
            percent=vram_pct,
            num_segments=18,
            active_color=self.C_EMERALD,
            track_color=self.C_TRACK,
            gap=2,
            radius=2,
        )

    def _render_ram_card(self, img: Image.Image, draw: ImageDraw.ImageDraw, snap: TelemetrySnapshot, rect: Tuple[int, int, int, int]):
        x1, y1, x2, y2 = rect
        self._render_card_base(draw, rect, self.C_PURPLE)

        font_label = FontManager.get_font(12, bold=True)
        font_sub = FontManager.get_font(10, bold=False)
        font_huge = FontManager.get_font(30, bold=True)
        font_xs = FontManager.get_font(9, bold=False)

        draw.text((x1 + 10, y1 + 7), "RAM", fill=self.C_PURPLE, font=font_label)
        draw.text((x1 + 42, y1 + 8), f"// TOTAL {snap.ram.total_gb} GB", fill=self.C_MUTED, font=font_sub)

        # Big percentage & used GB
        pct = snap.ram.usage_percent
        pct_color = self.C_RED if pct >= 90 else (self.C_AMBER if pct >= 80 else self.C_TEXT)
        draw.text((x1 + 12, y1 + 26), f"{int(pct)}%", fill=pct_color, font=font_huge)
        draw.text((x1 + 95, y1 + 36), f"USED {snap.ram.used_gb} GB", fill=self.C_MUTED, font=font_sub)

        # 20-segment LED ladder bar
        draw_segmented_bar(
            draw,
            (x1 + 12, y1 + 68, x2 - 12, y1 + 78),
            percent=pct,
            num_segments=20,
            active_color=self.C_PURPLE,
            track_color=self.C_TRACK,
            gap=2,
            radius=2,
        )

        # Memory sub-pill box
        box_y1 = y1 + 86
        draw.rounded_rectangle([(x1 + 12, box_y1), (x2 - 12, y2 - 8)], radius=4, fill=(16, 24, 38))
        draw.text((x1 + 18, box_y1 + 8), f"AVAILABLE:  {snap.ram.available_gb} GB", fill=self.C_TEXT, font=font_xs)
        draw.text((x1 + 18, box_y1 + 23), f"PHYSICAL:   {snap.ram.total_gb} GB DDR5", fill=self.C_MUTED, font=font_xs)

    def _render_net_card(self, img: Image.Image, draw: ImageDraw.ImageDraw, snap: TelemetrySnapshot, rect: Tuple[int, int, int, int]):
        x1, y1, x2, y2 = rect
        self._render_card_base(draw, rect, self.C_AMBER)

        font_label = FontManager.get_font(12, bold=True)
        font_sub = FontManager.get_font(10, bold=False)
        font_speed = FontManager.get_font(14, bold=True)
        font_xs = FontManager.get_font(9, bold=False)

        draw.text((x1 + 10, y1 + 7), "NETWORK", fill=self.C_AMBER, font=font_label)
        draw.text((x1 + 76, y1 + 8), "// LIVE I/O STREAM", fill=self.C_MUTED, font=font_sub)

        def fmt_speed(kb: float) -> str:
            if kb >= 1024.0:
                return f"{kb / 1024.0:.1f} MB/s"
            return f"{int(kb)} KB/s"

        down_str = fmt_speed(snap.net.down_speed_kb)
        up_str = fmt_speed(snap.net.up_speed_kb)

        # Down vector arrow + label
        arr_y1 = y1 + 30
        draw.polygon([(x1 + 12, arr_y1), (x1 + 20, arr_y1), (x1 + 16, arr_y1 + 6)], fill=self.C_CYAN)
        draw.text((x1 + 26, arr_y1 - 3), "DN", fill=self.C_MUTED, font=font_xs)
        draw.text((x1 + 46, arr_y1 - 4), down_str, fill=self.C_TEXT, font=font_speed)

        # Up vector arrow + label
        arr_y2 = y1 + 48
        draw.polygon([(x1 + 16, arr_y2), (x1 + 20, arr_y2 + 6), (x1 + 12, arr_y2 + 6)], fill=self.C_AMBER)
        draw.text((x1 + 26, arr_y2 - 2), "UP", fill=self.C_MUTED, font=font_xs)
        draw.text((x1 + 46, arr_y2 - 3), up_str, fill=self.C_TEXT, font=font_speed)

        # Session Traffic Pill (Right side)
        pill_x1 = x1 + 140
        draw.rounded_rectangle([(pill_x1, y1 + 28), (x2 - 12, y1 + 58)], radius=4, fill=(16, 24, 38))
        draw.text((pill_x1 + 8, y1 + 33), f"RX: {snap.net.total_recv_mb/1024:.1f} GB", fill=self.C_CYAN, font=font_xs)
        draw.text((pill_x1 + 8, y1 + 45), f"TX: {snap.net.total_sent_mb/1024:.1f} GB", fill=self.C_AMBER, font=font_xs)

        # Oscilloscope Sparkline Graph
        sp_x1, sp_y1, sp_x2, sp_y2 = x1 + 12, y1 + 68, x2 - 12, y2 - 8
        draw.rounded_rectangle([(sp_x1, sp_y1), (sp_x2, sp_y2)], radius=4, fill=(14, 20, 32))
        draw.line([(sp_x1, sp_y1 + 18), (sp_x2, sp_y1 + 18)], fill=(22, 32, 50), width=1)

        history = snap.net.down_history
        if history and len(history) >= 2:
            max_v = max(history) if max(history) > 50.0 else 50.0
            sp_w = sp_x2 - sp_x1
            sp_h = sp_y2 - sp_y1
            pts = []
            num_h = len(history)
            for i, v in enumerate(history):
                px = int(sp_x1 + i * (sp_w / (num_h - 1)))
                norm = min(1.0, max(0.0, v / max_v))
                py = int(sp_y2 - 2 - norm * (sp_h - 4))
                pts.append((px, py))

            # Translucent neon fill
            poly = [(sp_x1, sp_y2)] + pts + [(sp_x2, sp_y2)]
            overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            ov_draw = ImageDraw.Draw(overlay)
            ov_draw.polygon(poly, fill=(245, 158, 11, 45))
            img.alpha_composite(overlay)

            # Neon curve line
            draw.line(pts, fill=self.C_AMBER, width=2)
        else:
            draw.line([(sp_x1, sp_y2 - 2), (sp_x2, sp_y2 - 2)], fill=self.C_AMBER, width=1)

    def render_standby(self, message: str = "STANDBY") -> Image.Image:
        img = Image.new("RGBA", (self.width, self.height), (*self.C_BG, 255))
        draw = ImageDraw.Draw(img)
        font_lg = FontManager.get_font(20, bold=True)
        font_sm = FontManager.get_font(12, bold=False)

        cx, cy = self.width // 2, self.height // 2
        draw.rounded_rectangle([cx - 140, cy - 40, cx + 140, cy + 40], radius=8, fill=self.C_CARD, outline=self.C_CARD_BORDER, width=1)
        draw.ellipse([cx - 115, cy - 7, cx - 103, cy + 5], fill=self.C_MUTED)
        draw.text((cx - 90, cy - 22), "RIG COCKPIT", fill=self.C_TEXT, font=font_lg)
        draw.text((cx - 90, cy + 6), f"// {message}", fill=self.C_CYAN, font=font_sm)
        return img.convert("RGB")

