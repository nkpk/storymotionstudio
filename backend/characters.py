import os
import subprocess
import shutil
from PIL import Image, ImageDraw
import math

def ease_in_out(t):
    return t * t * (3 - 2 * t)

def draw_stick_figure(draw, x, y, scale, pose="idle", color=(255,255,255)):
    # x,y = position of head center
    head_r = int(20 * scale)
    body_len = int(60 * scale)
    limb_len = int(40 * scale)

    # Head
    draw.ellipse([x-head_r, y-head_r, x+head_r, y+head_r], outline=color, width=3)

    # Body
    body_top = (x, y + head_r)
    body_bottom = (x, y + head_r + body_len)
    draw.line([body_top, body_bottom], fill=color, width=3)

    if pose == "walk":
        # Arms
        draw.line([body_top, (x - limb_len, y + head_r + 20)], fill=color, width=3)
        draw.line([body_top, (x + limb_len, y + head_r + 30)], fill=color, width=3)
        # Legs
        draw.line([body_bottom, (x - limb_len*0.7, y + head_r + body_len + limb_len)], fill=color, width=3)
        draw.line([body_bottom, (x + limb_len*0.5, y + head_r + body_len + limb_len)], fill=color, width=3)
    elif pose == "wave":
        draw.line([body_top, (x - limb_len, y + head_r + 20)], fill=color, width=3)
        draw.line([body_top, (x + limb_len, y - 10)], fill=color, width=3)  # raised arm
        draw.line([body_bottom, (x - limb_len*0.5, y + head_r + body_len + limb_len)], fill=color, width=3)
        draw.line([body_bottom, (x + limb_len*0.5, y + head_r + body_len + limb_len)], fill=color, width=3)
    elif pose == "think":
        draw.line([body_top, (x + limb_len*0.5, y + head_r - 10)], fill=color, width=3)  # hand to chin
        draw.line([body_top, (x - limb_len, y + head_r + 30)], fill=color, width=3)
        draw.line([body_bottom, (x - limb_len*0.5, y + head_r + body_len + limb_len)], fill=color, width=3)
        draw.line([body_bottom, (x + limb_len*0.5, y + head_r + body_len + limb_len)], fill=color, width=3)
    else:  # idle
        draw.line([body_top, (x - limb_len*0.6, y + head_r + 40)], fill=color, width=3)
        draw.line([body_top, (x + limb_len*0.6, y + head_r + 40)], fill=color, width=3)
        draw.line([body_bottom, (x - limb_len*0.5, y + head_r + body_len + limb_len)], fill=color, width=3)
        draw.line([body_bottom, (x + limb_len*0.5, y + head_r + body_len + limb_len)], fill=color, width=3)

def draw_character_scene(
    output_path: str,
    action: str = "idle",
    label: str = "",
    duration: float = 3.0,
    width: int = 1920,
    height: int = 1080,
    fps: int = 25,
    bg_color: tuple = (9, 9, 9),
    char_color: tuple = (232, 201, 126),
):
    frames_dir = f"{output_path}_frames"
    os.makedirs(frames_dir, exist_ok=True)
    total_frames = int(duration * fps)

    cx, cy = width // 2, height // 2 - 100
    scale = min(width, height) / 800

    for i in range(total_frames):
        t = i / max(total_frames - 1, 1)
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        # Walking animation - bob up and down
        bob = 0
        x_offset = 0
        if action == "walk":
            bob = int(math.sin(t * math.pi * 8) * 10 * scale)
            x_offset = int((t - 0.5) * 200 * scale)
        elif action == "wave":
            bob = int(math.sin(t * math.pi * 6) * 5 * scale)
        elif action == "think":
            bob = int(math.sin(t * math.pi * 2) * 3 * scale)

        draw_stick_figure(draw, cx + x_offset, cy + bob, scale, pose=action, color=char_color)

        if label:
            draw.text((width // 2, height - 150), label, fill=(255,255,255), anchor="mm", font=None)

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