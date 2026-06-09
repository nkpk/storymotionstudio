import os
import subprocess
import shutil
from PIL import Image, ImageDraw, ImageFont
import math

def ease_out(t):
    return 1 - (1 - t) ** 3

def ease_in_out(t):
    return t * t * (3 - 2 * t)

# ── ICON LIBRARY ──
ICONS = {
    # Technology
    "phone": "📱", "laptop": "💻", "computer": "🖥",
    "internet": "🌐", "wifi": "📶", "battery": "🔋",
    "camera": "📷", "video": "🎥", "music": "🎵",
    "headphone": "🎧", "tv": "📺", "radio": "📻",
    "robot": "🤖", "ai": "🧠", "chip": "💾",
    "rocket": "🚀", "satellite": "🛰", "ufo": "🛸",

    # Business
    "money": "💰", "dollar": "💵", "chart": "📈",
    "chartdown": "📉", "bank": "🏦", "briefcase": "💼",
    "handshake": "🤝", "trophy": "🏆", "medal": "🥇",
    "target": "🎯", "idea": "💡", "fire": "🔥",
    "star": "⭐", "diamond": "💎", "crown": "👑",

    # Science
    "atom": "⚛", "dna": "🧬", "microscope": "🔬",
    "telescope": "🔭", "flask": "⚗", "pill": "💊",
    "brain": "🧠", "heart": "❤", "eye": "👁",
    "earth": "🌍", "sun": "☀", "moon": "🌙",
    "star2": "🌟", "comet": "☄", "thunder": "⚡",

    # People
    "person": "👤", "group": "👥", "baby": "👶",
    "man": "👨", "woman": "👩", "family": "👨‍👩‍👧‍👦",
    "teacher": "👨‍🏫", "doctor": "👨‍⚕", "scientist": "👨‍🔬",

    # Nature
    "tree": "🌳", "flower": "🌸", "earth2": "🌏",
    "fire2": "🔥", "water": "💧", "snow": "❄",
    "cloud": "☁", "rain": "🌧", "storm": "⛈",

    # Transport
    "car": "🚗", "plane": "✈", "ship": "🚢",
    "train": "🚂", "bike": "🚲", "rocket2": "🚀",

    # Arrows
    "arrowright": "→", "arrowleft": "←", "arrowup": "↑",
    "arrowdown": "↓", "arrowne": "↗", "arrownw": "↖",
}

def draw_icon_scene(
    output_path: str,
    icon_key: str,
    label: str = "",
    duration: float = 2.0,
    width: int = 1920,
    height: int = 1080,
    fps: int = 25,
    bg_color: tuple = (9, 9, 9),
    animation: str = "zoom",
):
    frames_dir = f"{output_path}_frames"
    os.makedirs(frames_dir, exist_ok=True)
    total_frames = int(duration * fps)
    icon = ICONS.get(icon_key, "⭐")

    for i in range(total_frames):
        t = ease_out(i / max(total_frames - 1, 1))
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        if animation == "zoom":
            scale = t
        elif animation == "fade":
            scale = 1.0
        else:
            scale = t

        # Draw icon
        draw.text(
            (width // 2, height // 2 - 60),
            icon,
            fill=(255, 255, 255),
            anchor="mm",
            font=ImageFont.load_default()
        )

        # Draw label
        if label:
            draw.text(
                (width // 2, height // 2 + 80),
                label,
                fill=(232, 201, 126),
                anchor="mm",
                font=ImageFont.load_default()
            )

        frame_path = f"{frames_dir}/{i:04d}.png"
        img.save(frame_path)

    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", f"{frames_dir}/%04d.png",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        output_path
    ], check=True, capture_output=True)

    shutil.rmtree(frames_dir)

def draw_text_overlay(
    output_path: str,
    lines: list,
    duration: float = 3.0,
    width: int = 1920,
    height: int = 1080,
    fps: int = 25,
    bg_color: tuple = (9, 9, 9),
    text_color: tuple = (255, 255, 255),
    accent_color: tuple = (232, 201, 126),
    animation: str = "slideup",
):
    frames_dir = f"{output_path}_frames"
    os.makedirs(frames_dir, exist_ok=True)
    total_frames = int(duration * fps)

    for i in range(total_frames):
        t = ease_out(i / max(total_frames - 1, 1))
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        total_lines = len(lines)
        line_height = 80
        start_y = height // 2 - (total_lines * line_height) // 2

        for j, line in enumerate(lines):
            if animation == "slideup":
                delay = j / max(total_lines, 1) * 0.5
                line_t = max(0, min(1, (t - delay) * 2))
                offset_y = int((1 - ease_out(line_t)) * 60)
                alpha = int(ease_out(line_t) * 255)
            else:
                offset_y = 0
                alpha = int(t * 255)

            y = start_y + j * line_height + offset_y
            color = accent_color if j == 0 else text_color

            draw.text(
                (width // 2, y),
                line,
                fill=color,
                anchor="mm",
                font=ImageFont.load_default()
            )

        frame_path = f"{frames_dir}/{i:04d}.png"
        img.save(frame_path)

    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", f"{frames_dir}/%04d.png",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        output_path
    ], check=True, capture_output=True)

    shutil.rmtree(frames_dir)

def draw_comparison(
    output_path: str,
    left_label: str,
    right_label: str,
    left_value: int,
    right_value: int,
    title: str = "",
    duration: float = 3.0,
    width: int = 1920,
    height: int = 1080,
    fps: int = 25,
    bg_color: tuple = (9, 9, 9),
):
    frames_dir = f"{output_path}_frames"
    os.makedirs(frames_dir, exist_ok=True)
    total_frames = int(duration * fps)
    max_val = max(left_value, right_value)

    for i in range(total_frames):
        t = ease_out(i / max(total_frames - 1, 1))
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        if title:
            draw.text((width // 2, 80), title, fill=(255, 255, 255), anchor="mm", font=ImageFont.load_default())

        # Divider line
        draw.line([(width // 2, 150), (width // 2, height - 150)], fill=(255, 255, 255, 30), width=2)

        # Left bar
        left_h = int((left_value / max_val) * (height * 0.4) * t)
        lx1 = int(width * 0.2)
        lx2 = int(width * 0.45)
        ly2 = int(height * 0.75)
        ly1 = ly2 - left_h
        draw.rectangle([lx1, ly1, lx2, ly2], fill=(232, 201, 126))
        draw.text(((lx1 + lx2) // 2, ly2 + 30), left_label, fill=(255, 255, 255), anchor="mm", font=ImageFont.load_default())
        draw.text(((lx1 + lx2) // 2, ly1 - 20), f"{left_value:,}", fill=(232, 201, 126), anchor="mm", font=ImageFont.load_default())

        # Right bar
        right_h = int((right_value / max_val) * (height * 0.4) * t)
        rx1 = int(width * 0.55)
        rx2 = int(width * 0.80)
        ry2 = int(height * 0.75)
        ry1 = ry2 - right_h
        draw.rectangle([rx1, ry1, rx2, ry2], fill=(0, 212, 255))
        draw.text(((rx1 + rx2) // 2, ry2 + 30), right_label, fill=(255, 255, 255), anchor="mm", font=ImageFont.load_default())
        draw.text(((rx1 + rx2) // 2, ry1 - 20), f"{right_value:,}", fill=(0, 212, 255), anchor="mm", font=ImageFont.load_default())

        frame_path = f"{frames_dir}/{i:04d}.png"
        img.save(frame_path)

    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", f"{frames_dir}/%04d.png",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        output_path
    ], check=True, capture_output=True)

    shutil.rmtree(frames_dir)

def draw_progress_bar(
    output_path: str,
    label: str,
    percentage: int,
    duration: float = 2.0,
    width: int = 1920,
    height: int = 1080,
    fps: int = 25,
    bg_color: tuple = (9, 9, 9),
    bar_color: tuple = (232, 201, 126),
):
    frames_dir = f"{output_path}_frames"
    os.makedirs(frames_dir, exist_ok=True)
    total_frames = int(duration * fps)

    for i in range(total_frames):
        t = ease_out(i / max(total_frames - 1, 1))
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        current_pct = int(percentage * t)
        bar_x1 = int(width * 0.1)
        bar_x2 = int(width * 0.9)
        bar_y = height // 2
        bar_h = 40
        bar_fill = int(bar_x1 + (bar_x2 - bar_x1) * (current_pct / 100))

        # Background bar
        draw.rounded_rectangle([bar_x1, bar_y, bar_x2, bar_y + bar_h], radius=20, fill=(255, 255, 255, 20))

        # Fill bar
        if bar_fill > bar_x1:
            draw.rounded_rectangle([bar_x1, bar_y, bar_fill, bar_y + bar_h], radius=20, fill=bar_color)

        # Label
        draw.text((width // 2, bar_y - 60), label, fill=(255, 255, 255), anchor="mm", font=ImageFont.load_default())

        # Percentage
        draw.text((width // 2, bar_y + bar_h + 40), f"{current_pct}%", fill=bar_color, anchor="mm", font=ImageFont.load_default())

        frame_path = f"{frames_dir}/{i:04d}.png"
        img.save(frame_path)

    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", f"{frames_dir}/%04d.png",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        output_path
    ], check=True, capture_output=True)

    shutil.rmtree(frames_dir)