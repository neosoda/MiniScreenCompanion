from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

def get_auto_mood(hour: int) -> Tuple[str, str]:
    if 23 <= hour or hour < 7:
        return "sleep", "Zzz..."
    elif 7 <= hour < 10:
        return "run", "Ça vib"
    elif 10 <= hour < 12:
        return "desk", "En plein hack"
    elif 12 <= hour < 14:
        return "coffee", "Pause café"
    elif 14 <= hour < 18:
        return "desk", "Dans le flow"
    elif 18 <= hour < 20:
        return "pet", "Câlin chat"
    elif 20 <= hour < 23:
        return "desk", "Ça code fort"
    else:
        return "sleep", "Mode veille"

def draw_chibi_head(d: ImageDraw.ImageDraw, x: int, y: int, bob: int = 0, expression: str = "normal", blink: bool = False):
    """Draws a cute anime chibi face with fair skin, pink blush, and fluffy brown hair."""
    c_skin = (252, 222, 202, 255)
    c_blush = (252, 175, 175, 255)
    c_hair = (92, 58, 36, 255)
    c_hair_hl = (130, 85, 55, 255)
    c_eye = (24, 24, 28, 255)

    # Face base
    d.rounded_rectangle([x + 2, y + 3 - bob, x + 14, y + 13 - bob], radius=3, fill=c_skin)
    # Pink blush on cheeks
    d.point((x + 3, y + 9 - bob), fill=c_blush)
    d.point((x + 13, y + 9 - bob), fill=c_blush)

    # Eyes
    if blink:
        d.line([x + 6, y + 7 - bob, x + 8, y + 7 - bob], fill=c_eye, width=1)
        d.line([x + 10, y + 7 - bob, x + 12, y + 7 - bob], fill=c_eye, width=1)
    elif expression == "happy":
        # Curved happy eyes ^_^
        d.point((x + 6, y + 6 - bob), fill=c_eye)
        d.point((x + 7, y + 7 - bob), fill=c_eye)
        d.point((x + 11, y + 6 - bob), fill=c_eye)
        d.point((x + 12, y + 7 - bob), fill=c_eye)
    else:
        # Anime eye with specular glint
        d.rectangle([x + 6, y + 6 - bob, x + 7, y + 8 - bob], fill=c_eye)
        d.point((x + 6, y + 6 - bob), fill=(255, 255, 255, 255))
        d.rectangle([x + 10, y + 6 - bob, x + 11, y + 8 - bob], fill=c_eye)
        d.point((x + 10, y + 6 - bob), fill=(255, 255, 255, 255))

    # Cute mouth
    d.point((x + 8, y + 10 - bob), fill=(180, 110, 90, 255))

    # Fluffy hair
    d.rounded_rectangle([x + 1, y - bob, x + 15, y + 5 - bob], radius=3, fill=c_hair)
    d.ellipse([x - 1, y + 1 - bob, x + 6, y + 9 - bob], fill=c_hair)
    d.ellipse([x + 11, y + 1 - bob, x + 17, y + 8 - bob], fill=c_hair)
    d.point((x + 5, y + 1 - bob), fill=c_hair_hl)
    d.point((x + 6, y + 1 - bob), fill=c_hair_hl)
    d.point((x + 9, y + 1 - bob), fill=c_hair_hl)

def render_room_1_3_background(
    user_name: str,
    status_message: str,
    time_str: str,
    font_mono_hdr: ImageFont.ImageFont,
    font_ui_stat: ImageFont.ImageFont,
    font_mono_clock: ImageFont.ImageFont,
    show_stool: bool = True,
    is_night: bool = False
) -> Image.Image:
    """Renders the top 1/3 (y=0 to 78) cozy pixel room with day or night atmosphere."""
    img = Image.new("RGBA", (240, 78), (7, 11, 26, 255))
    d = ImageDraw.Draw(img)

    # Wallpaper (Warm cream day, or soft cozy twilight night)
    wall_color = (245, 238, 226, 255) if not is_night else (220, 214, 206, 255)
    d.rectangle([0, 0, 240, 56], fill=wall_color)

    if not is_night:
        # Sunlight beam
        sunlight = Image.new("RGBA", (240, 78), (0, 0, 0, 0))
        d_sun = ImageDraw.Draw(sunlight)
        d_sun.polygon([(165, 0), (210, 0), (140, 56), (70, 56)], fill=(255, 248, 215, 60))
        d_sun.polygon([(180, 0), (220, 0), (170, 56), (110, 56)], fill=(255, 252, 230, 40))
        img = Image.alpha_composite(img, sunlight)
        d = ImageDraw.Draw(img)

    # Window (x=172 to 212, y=8 to 38)
    if is_night:
        # Dark night sky with stars and yellow crescent moon
        d.rectangle([172, 8, 212, 38], fill=(15, 23, 42, 255), outline=(100, 65, 35, 255), width=2)
        # Crescent Moon
        d.ellipse([180, 12, 192, 24], fill=(253, 224, 71, 255))
        d.ellipse([183, 11, 195, 23], fill=(15, 23, 42, 255))
        # Twinkling Stars
        d.point((198, 14), fill=(255, 255, 255, 240))
        d.point((204, 22), fill=(255, 255, 255, 240))
        d.point((176, 26), fill=(255, 255, 255, 240))
    else:
        # Daytime blue sky with white cloud
        d.rectangle([172, 8, 212, 38], fill=(186, 230, 253, 255), outline=(139, 90, 45, 255), width=2)
        d.ellipse([176, 12, 188, 17], fill=(255, 255, 255, 220))
        d.ellipse([184, 10, 196, 16], fill=(255, 255, 255, 220))

    # Window panes
    win_frame_col = (100, 65, 35, 255) if is_night else (139, 90, 45, 255)
    d.line([192, 8, 192, 38], fill=win_frame_col, width=1)
    d.line([172, 23, 212, 23], fill=win_frame_col, width=1)

    # Bookshelf on left (x=8 to 36, y=10 to 56)
    d.rectangle([8, 10, 36, 56], fill=(165, 110, 60, 255), outline=(107, 66, 38, 255), width=1)
    d.line([8, 30, 36, 30], fill=(107, 66, 38, 255), width=1)
    # Books
    d.rectangle([12, 14, 16, 29], fill=(220, 38, 38, 255))
    d.rectangle([17, 16, 21, 29], fill=(37, 99, 235, 255))
    d.rectangle([22, 13, 26, 29], fill=(22, 163, 74, 255))
    d.rectangle([27, 17, 32, 29], fill=(234, 179, 8, 255))
    # Plant on bookshelf
    d.ellipse([10, 4, 20, 10], fill=(34, 197, 94, 255))
    d.ellipse([18, 3, 28, 9], fill=(74, 222, 128, 255))

    # Potted plant on right (x=218 to 230, y=42 to 56)
    d.rectangle([218, 42, 230, 56], fill=(240, 245, 250, 255), outline=(203, 213, 225, 255), width=1)
    d.ellipse([214, 32, 224, 44], fill=(34, 197, 94, 255))
    d.ellipse([222, 30, 232, 43], fill=(22, 163, 74, 255))

    # Wooden parquet floor (y=56 to 78)
    d.rectangle([0, 56, 240, 58], fill=(115, 72, 38, 255))
    d.rectangle([0, 59, 240, 78], fill=(218, 158, 105, 255))
    for px in [40, 90, 140, 190]:
        d.line([px, 59, px, 78], fill=(185, 125, 75, 255), width=1)

    # Top status pills
    if user_name and user_name.strip():
        u_str = user_name.strip().upper()
        bbox_u = font_mono_hdr.getbbox(u_str)
        uw = bbox_u[2] - bbox_u[0]
        bbox_s = font_ui_stat.getbbox(f"·  {status_message}")
        sw = bbox_s[2] - bbox_s[0]
        pill_w = uw + sw + 20
        d.rounded_rectangle([6, 3, min(160, 6 + pill_w), 18], radius=3, fill=(8, 14, 38, 240), outline=(42, 65, 115, 255), width=1)
        d.text((10, 4), u_str, fill=(147, 197, 253, 255), font=font_mono_hdr)
        d.text((10 + uw + 6, 4), f"·  {status_message}", fill=(240, 245, 255, 255), font=font_ui_stat)
    else:
        bbox_s = font_ui_stat.getbbox(status_message)
        sw = bbox_s[2] - bbox_s[0]
        d.rounded_rectangle([6, 3, 16 + sw, 18], radius=3, fill=(8, 14, 38, 240), outline=(42, 65, 115, 255), width=1)
        d.text((11, 4), status_message, fill=(240, 245, 255, 255), font=font_ui_stat)

    # Clock pill
    d.rounded_rectangle([186, 3, 234, 18], radius=3, fill=(8, 14, 38, 240), outline=(42, 65, 115, 255), width=1)
    d.text((192, 4), time_str, fill=(148, 163, 184, 255), font=font_mono_clock)

    return img

def create_runner_avatar(frame_idx: int) -> Image.Image:
    """Cute chibi runner with athletic stride and bobbing hair."""
    im = Image.new("RGBA", (36, 34), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    c_shirt = (30, 58, 138, 255)
    c_pants = (30, 41, 59, 255)
    c_shoe = (250, 250, 252, 255)

    cycles = [
        (0,  7, 25, -5, 21, -3,  3),
        (2,  4, 26, -2, 23, -2,  2),
        (3,  1, 24,  1, 25,  0,  0),
        (1, -2, 22,  4, 26,  2, -2),
        (0, -5, 21,  7, 25,  3, -3),
        (2, -2, 23,  4, 26,  2, -2),
        (3,  1, 25,  1, 24,  0,  0),
        (1,  4, 26, -2, 22, -2,  2),
    ]
    bob, fx, fy, bx, by, af, ab = cycles[frame_idx % 8]
    blink = (frame_idx % 8 == 4)

    # Floor shadow
    d.ellipse([10, 29, 28, 33], fill=(0, 0, 0, 45))

    # Back arm
    d.line([15, 13 - bob, 15 + ab, 18 - bob], fill=c_shirt, width=2)
    d.point((16 + ab, 17 - bob), fill=(252, 222, 202, 255))

    # Back leg & shoe
    d.line([15, 19 - bob, 15 + bx, by], fill=c_pants, width=3)
    d.rectangle([14 + bx, by - 1, 19 + bx, by + 2], fill=c_shoe)

    # Torso
    d.polygon([(12, 12 - bob), (20, 12 - bob), (18, 21 - bob), (12, 21 - bob)], fill=c_shirt)

    # Head
    draw_chibi_head(d, 10, 1, bob=bob, expression="happy" if frame_idx in (2, 6) else "normal", blink=blink)

    # Front leg & shoe
    d.line([17, 19 - bob, 17 + fx, fy], fill=c_pants, width=3)
    d.rectangle([16 + fx, fy - 1, 21 + fx, fy + 2], fill=c_shoe)

    # Front arm
    d.line([18, 13 - bob, 18 + af, 18 - bob], fill=c_shirt, width=2)
    d.point((19 + af, 17 - bob), fill=(252, 222, 202, 255))

    return im

def create_desk_avatar(frame_idx: int) -> Image.Image:
    """Cute chibi coding at laptop with screen glow and steaming coffee."""
    im = Image.new("RGBA", (52, 34), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    c_shirt = (30, 58, 138, 255)
    c_pants = (30, 41, 59, 255)
    c_shoe = (250, 250, 252, 255)

    bob = 1 if frame_idx % 2 == 1 else 0
    blink = (frame_idx % 8 == 5)

    # Shadow
    d.ellipse([8, 28, 46, 33], fill=(0, 0, 0, 45))

    # Desk
    d.rectangle([24, 15, 46, 18], fill=(160, 105, 55, 255), outline=(110, 70, 35, 255), width=1)
    d.rectangle([40, 18, 43, 30], fill=(110, 70, 35, 255))

    # Laptop with screen glow and syntax code lines
    d.line([27, 15, 37, 15], fill=(148, 163, 184, 255), width=2)
    d.line([30, 8, 30, 15], fill=(100, 116, 139, 255), width=2)
    glow_col = (56, 189, 248, 255) if frame_idx % 4 < 2 else (74, 222, 128, 255)
    d.point((31, 9), fill=glow_col)
    d.point((31, 11), fill=(244, 114, 182, 255)) # pink syntax
    d.point((31, 13), fill=glow_col)

    # Coffee mug on desk
    d.rectangle([39, 11, 44, 15], fill=(245, 245, 245, 255))
    steam_steps = [[(41, 8)], [(42, 7), (41, 5)], [(42, 6)], [(41, 7)]]
    for sx, sy in steam_steps[frame_idx % len(steam_steps)]:
        d.point((sx, sy), fill=(255, 255, 255, 190))

    # Stool
    d.rectangle([10, 20, 20, 23], fill=(140, 92, 48, 255))
    d.rectangle([14, 23, 16, 30], fill=(110, 70, 32, 255))

    # Character sitting
    d.rectangle([14, 19, 22, 25], fill=c_pants)
    d.rectangle([20, 25, 23, 29], fill=c_pants)
    d.rectangle([20, 28, 25, 30], fill=c_shoe)

    # Torso
    d.rectangle([11, 11 + bob, 19, 21 + bob], fill=c_shirt)

    # Arms typing
    arm_x = 22 if frame_idx % 2 == 0 else 23
    d.rectangle([15, 14 + bob, arm_x, 17 + bob], fill=c_shirt)
    d.rectangle([arm_x, 16 + bob, 27, 18 + bob], fill=(252, 222, 202, 255))

    # Head
    draw_chibi_head(d, 9, 1, bob=bob, expression="normal", blink=blink)

    return im

def create_coffee_avatar(frame_idx: int) -> Image.Image:
    """Cute chibi enjoying coffee break."""
    im = Image.new("RGBA", (36, 34), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    c_shirt = (30, 58, 138, 255)
    c_pants = (30, 41, 59, 255)
    c_shoe = (250, 250, 252, 255)

    bob = 1 if frame_idx % 4 in (1, 2) else 0

    # Shadow
    d.ellipse([10, 28, 26, 33], fill=(0, 0, 0, 45))

    # Legs
    d.rectangle([13, 19, 16, 28], fill=c_pants)
    d.rectangle([18, 19, 21, 28], fill=c_pants)
    d.rectangle([12, 28, 17, 30], fill=c_shoe)
    d.rectangle([17, 28, 22, 30], fill=c_shoe)

    # Torso
    d.rectangle([12, 11 + bob, 21, 21 + bob], fill=c_shirt)

    # Arms holding mug
    d.rectangle([10, 14 + bob, 14, 18 + bob], fill=c_shirt)
    d.rectangle([19, 14 + bob, 23, 18 + bob], fill=c_shirt)
    d.rectangle([14, 16 + bob, 19, 18 + bob], fill=(252, 222, 202, 255))

    # Yellow coffee mug
    d.rectangle([15, 14 + bob, 20, 18 + bob], fill=(234, 179, 8, 255))
    steam_steps = [[(17, 11 + bob)], [(18, 10 + bob), (17, 8 + bob)], [(17, 9 + bob)], [(18, 10 + bob)]]
    for sx, sy in steam_steps[frame_idx % len(steam_steps)]:
        d.point((sx, sy), fill=(255, 255, 255, 190))

    # Head (happy smiling ^_^)
    draw_chibi_head(d, 9, 1, bob=bob, expression="happy", blink=False)

    return im

def create_pet_avatar(frame_idx: int) -> Image.Image:
    """Cute chibi sitting and petting an orange cat with a swaying tail."""
    im = Image.new("RGBA", (50, 34), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    c_shirt = (30, 58, 138, 255)
    c_pants = (30, 41, 59, 255)
    c_shoe = (250, 250, 252, 255)
    c_cat = (249, 115, 22, 255)
    c_cat_stripe = (194, 65, 12, 255)

    bob = 1 if frame_idx % 2 == 1 else 0

    # Shadow
    d.ellipse([8, 28, 44, 33], fill=(0, 0, 0, 45))

    # Sitting character
    d.rectangle([10, 23, 22, 29], fill=c_pants)
    d.rectangle([14, 27, 20, 30], fill=c_shoe)
    d.rectangle([10, 14 + bob, 18, 24 + bob], fill=c_shirt)

    # Arm petting cat
    arm_y = 19 + bob if frame_idx % 4 < 2 else 20 + bob
    d.rectangle([14, 16 + bob, 24, arm_y], fill=c_shirt)
    d.rectangle([24, arm_y - 1, 29, arm_y + 1], fill=(252, 222, 202, 255)) # hand on cat

    # Head (happy face looking at cat)
    draw_chibi_head(d, 7, 3, bob=bob, expression="happy", blink=False)

    # Cute Orange Cat
    d.ellipse([28, 21, 40, 29], fill=c_cat)
    d.line([32, 21, 32, 25], fill=c_cat_stripe, width=1)
    d.line([36, 21, 36, 25], fill=c_cat_stripe, width=1)
    # Head
    d.ellipse([27, 17, 33, 24], fill=c_cat)
    # Ears
    d.polygon([(27, 17), (29, 14), (30, 17)], fill=c_cat)
    d.polygon([(30, 17), (32, 14), (33, 17)], fill=c_cat)
    # Pink ear inside
    d.point((29, 16), fill=(252, 175, 175, 255))
    d.point((31, 16), fill=(252, 175, 175, 255))
    # Closed happy eyes (cat purring ^_^)
    d.point((29, 20), fill=(24, 24, 28, 255))
    # Tail swaying
    tail_y = [17, 19, 22, 19][frame_idx % 4]
    d.line([40, 24, 44, tail_y], fill=c_cat, width=2)

    return im

def create_sleep_avatar(frame_idx: int) -> Image.Image:
    """Cute chibi sleeping on round rug under blanket with floating 'z Z z'."""
    im = Image.new("RGBA", (50, 34), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    c_hair = (92, 58, 36, 255)
    c_skin = (252, 222, 202, 255)
    c_blanket = (59, 130, 246, 255)

    breathe = 1 if frame_idx in (2, 3, 4) else 0

    # Rug
    d.ellipse([4, 21, 46, 33], fill=(226, 232, 240, 255), outline=(203, 213, 225, 255), width=1)
    # Pillow
    d.rounded_rectangle([8, 19, 18, 27], radius=2, fill=(255, 255, 255, 255))
    # Head sleeping
    d.rectangle([10, 18, 17, 25], fill=c_skin)
    d.rectangle([9, 16, 17, 21], fill=c_hair)
    d.line([13, 22, 15, 22], fill=(24, 24, 28, 255), width=1) # closed eye

    # Blanket
    d.rounded_rectangle([15, 17 - breathe, 35, 29], radius=3, fill=c_blanket)

    # Floating 'z' and 'Z'
    z_frames = [
        [(20, 11, "z")],
        [(22, 9, "z"), (25, 5, "Z")],
        [(24, 7, "z"), (27, 3, "Z")],
        [(25, 5, "z")],
        [(20, 12, "z")]
    ]
    cur_z = z_frames[frame_idx % len(z_frames)]
    for zx, zy, char in cur_z:
        d.text((zx, zy), char, fill=(147, 197, 253, 220))

    return im

def load_custom_frames(assets_dir: Path) -> Optional[List[Image.Image]]:
    avatar_dir = assets_dir / "avatar"
    if not avatar_dir.is_dir():
        return None

    custom_gif = avatar_dir / "custom.gif"
    if custom_gif.is_file():
        try:
            gif = Image.open(custom_gif)
            frames = []
            for i in range(getattr(gif, "n_frames", 1)):
                gif.seek(i)
                f = gif.convert("RGBA").resize((36, 34), Image.Resampling.NEAREST)
                frames.append(f)
            if frames:
                return frames
        except Exception:
            pass

    png_frames = sorted(avatar_dir.glob("frame_*.png"))
    if png_frames:
        try:
            frames = [Image.open(p).convert("RGBA").resize((36, 34), Image.Resampling.NEAREST) for p in png_frames]
            if frames:
                return frames
        except Exception:
            pass

    return None
