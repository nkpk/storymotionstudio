import os
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import math

def ease_out(t):
    return 1 - (1 - t) ** 3

def ease_in_out(t):
    return t * t * (3 - 2 * t)

def draw_counter(
    output_path: str,
    start: int,
    end: int,
    duration: float,
    prefix: str = "",
    suffix: str = "",
    width: int = 1920,
    height: int = 1080,
    fps: int = 25,
    style: str = "default",
    bg_color: tuple = (9, 9, 9),
    text_color: tuple = (232, 201, 126),
    label: str = "",
):
    frames_dir = f"{output_path}_frames"
    os.makedirs(frames_dir, exist_ok=True)
    total_frames = int(duration * fps)

    for i in range(total_frames):
        t = ease_out(i / max(total_frames - 1, 1))
        current_value = int(start + (end - start) * t)

        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        # Format number with commas
        formatted = f"{prefix}{current_value:,}{suffix}"

        # Draw label
        if label:
            draw.text(
                (width // 2, height // 2 - 120),
                label,
                fill=(255, 255, 255, 180),
                anchor="mm",
                font=ImageFont.load_default()
            )

        # Draw main counter number
        # Use large font size by drawing text scaled
        font_size = max(80, min(160, width // 8))

        # Draw counter text centered
        draw.text(
            (width // 2, height // 2),
            formatted,
            fill=text_color,
            anchor="mm",
            font=ImageFont.load_default()
        )

        # Draw progress bar at bottom
        bar_width = int((width * 0.7) * t)
        bar_x = int(width * 0.15)
        bar_y = height // 2 + 100
        draw.rectangle([bar_x, bar_y, bar_x + int(width * 0.7), bar_y + 6], fill=(255, 255, 255, 30))
        draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + 6], fill=text_color)

        frame_path = f"{frames_dir}/{i:04d}.png"
        img.save(frame_path)

    # Convert frames to video
    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", f"{frames_dir}/%04d.png",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        output_path
    ], check=True, capture_output=True)

    # Cleanup frames
    import shutil
    shutil.rmtree(frames_dir)

def draw_bar_chart(
    output_path: str,
    labels: list,
    values: list,
    duration: float,
    title: str = "",
    width: int = 1920,
    height: int = 1080,
    fps: int = 25,
    bg_color: tuple = (9, 9, 9),
    colors: list = None,
):
    frames_dir = f"{output_path}_frames"
    os.makedirs(frames_dir, exist_ok=True)
    total_frames = int(duration * fps)

    if colors is None:
        colors = [
            (232, 201, 126),
            (0, 212, 255),
            (124, 255, 107),
            (255, 92, 135),
            (245, 200, 66),
            (255, 100, 100),
        ]

    max_val = max(values)
    n = len(labels)
    chart_left = int(width * 0.1)
    chart_right = int(width * 0.9)
    chart_top = int(height * 0.15)
    chart_bottom = int(height * 0.82)
    chart_width = chart_right - chart_left
    chart_height = chart_bottom - chart_top
    bar_spacing = 20
    bar_width = (chart_width - (bar_spacing * (n + 1))) // n

    for i in range(total_frames):
        t = ease_out(i / max(total_frames - 1, 1))
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        # Title
        if title:
            draw.text((width // 2, 60), title, fill=(255, 255, 255), anchor="mm", font=ImageFont.load_default())

        # Draw bars
        for j, (label, value) in enumerate(zip(labels, values)):
            bar_h = int((value / max_val) * chart_height * t)
            x1 = chart_left + bar_spacing + j * (bar_width + bar_spacing)
            x2 = x1 + bar_width
            y2 = chart_bottom
            y1 = y2 - bar_h

            color = colors[j % len(colors)]
            draw.rectangle([x1, y1, x2, y2], fill=color)

            # Label below bar
            draw.text(
                ((x1 + x2) // 2, chart_bottom + 20),
                label,
                fill=(255, 255, 255),
                anchor="mm",
                font=ImageFont.load_default()
            )

            # Value above bar
            if bar_h > 20:
                draw.text(
                    ((x1 + x2) // 2, y1 - 15),
                    f"{value:,}",
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

    import shutil
    shutil.rmtree(frames_dir)

def draw_pie_chart(
    output_path: str,
    labels: list,
    values: list,
    duration: float,
    title: str = "",
    width: int = 1920,
    height: int = 1080,
    fps: int = 25,
    bg_color: tuple = (9, 9, 9),
    colors: list = None,
):
    frames_dir = f"{output_path}_frames"
    os.makedirs(frames_dir, exist_ok=True)
    total_frames = int(duration * fps)

    if colors is None:
        colors = [
            (232, 201, 126),
            (0, 212, 255),
            (124, 255, 107),
            (255, 92, 135),
            (245, 200, 66),
        ]

    total = sum(values)
    percentages = [v / total * 100 for v in values]

    cx, cy = width // 2, height // 2
    radius = min(width, height) // 3

    for i in range(total_frames):
        t = ease_in_out(i / max(total_frames - 1, 1))
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        if title:
            draw.text((width // 2, 60), title, fill=(255, 255, 255), anchor="mm", font=ImageFont.load_default())

        start_angle = -90
        for j, (label, pct) in enumerate(zip(labels, percentages)):
            sweep = pct / 100 * 360 * t
            end_angle = start_angle + sweep
            color = colors[j % len(colors)]

            if sweep > 0:
                draw.pieslice(
                    [cx - radius, cy - radius, cx + radius, cy + radius],
                    start=start_angle,
                    end=end_angle,
                    fill=color,
                    outline=tuple(bg_color)
                )

            # Label
            mid_angle = math.radians(start_angle + sweep / 2)
            label_r = radius * 1.25
            lx = cx + label_r * math.cos(mid_angle)
            ly = cy + label_r * math.sin(mid_angle)
            draw.text((lx, ly), f"{label}\n{pct:.0f}%", fill=color, anchor="mm", font=ImageFont.load_default())

            start_angle = end_angle

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

    import shutil
    shutil.rmtree(frames_dir)

def draw_timeline(
    output_path: str,
    events: list,
    duration: float,
    title: str = "",
    width: int = 1920,
    height: int = 1080,
    fps: int = 25,
    bg_color: tuple = (9, 9, 9),
    accent_color: tuple = (232, 201, 126),
):
    frames_dir = f"{output_path}_frames"
    os.makedirs(frames_dir, exist_ok=True)
    total_frames = int(duration * fps)
    n = len(events)

    for i in range(total_frames):
        t = i / max(total_frames - 1, 1)
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        if title:
            draw.text((width // 2, 60), title, fill=(255, 255, 255), anchor="mm", font=ImageFont.load_default())

        # Timeline line
        line_y = height // 2
        line_x1 = int(width * 0.08)
        line_x2 = int(width * 0.92)
        line_progress = int(line_x1 + (line_x2 - line_x1) * t)
        draw.line([(line_x1, line_y), (line_x2, line_y)], fill=(255, 255, 255, 40), width=2)
        draw.line([(line_x1, line_y), (line_progress, line_y)], fill=accent_color, width=3)

        # Events
        for j, event in enumerate(events):
            ex = line_x1 + (line_x2 - line_x1) * j // max(n - 1, 1)
            event_t = j / max(n - 1, 1)
            visible = t >= event_t

            if visible:
                # Dot
                dot_r = 10
                draw.ellipse([ex - dot_r, line_y - dot_r, ex + dot_r, line_y + dot_r], fill=accent_color)

                # Year above
                year = event.get("year", "")
                label = event.get("label", "")

                draw.text((ex, line_y - 35), year, fill=accent_color, anchor="mm", font=ImageFont.load_default())
                draw.text((ex, line_y + 40), label, fill=(255, 255, 255), anchor="mm", font=ImageFont.load_default())

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

    import shutil
    shutil.rmtree(frames_dir)