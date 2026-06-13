from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List, Optional
import uuid
import os
import subprocess
import shutil

from graphics import draw_counter, draw_bar_chart, draw_pie_chart, draw_timeline
from assets import draw_icon_scene, draw_text_overlay, draw_comparison, draw_progress_bar
from ai import generate_script, generate_narration_text
from hf_images import generate_image

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

jobs = {}

def get_transition(style: str):
    transitions = {
        "Horror Cinematic": "fade",
        "Anime Recap": "wipeleft",
        "Documentary": "fade",
        "Science Explainer": "wipeup",
        "Luxury Storytelling": "fadeblack",
        "Viral Shorts": "slideleft",
    }
    return transitions.get(style, "fade")

def get_zoom_filter(intensity: str, width: int, height: int):
    zooms = {
        "Low Motion": f"zoompan=z='min(zoom+0.0005,1.1)':d=125:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height},fps=25",
        "Medium Motion": f"zoompan=z='min(zoom+0.001,1.2)':d=125:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height},fps=25",
        "High Motion": f"zoompan=z='min(zoom+0.0015,1.3)':d=125:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height},fps=25",
        "Cinematic": f"zoompan=z='min(zoom+0.001,1.2)':d=125:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height},fps=25",
    }
    return zooms.get(intensity, zooms["Medium Motion"])

def get_style_filter(style: str):
    filters = {
        "Horror Cinematic": (
            "curves=vintage,"
            "colorchannelmixer=rr=1.3:rg=0:rb=0:gr=0:gg=0.7:gb=0:br=0:bg=0:bb=0.7,"
            "vignette=PI/4,"
            "noise=alls=8:allf=t"
        ),
        "Anime Recap": (
            "eq=saturation=1.8:contrast=1.2:brightness=0.05,"
            "unsharp=5:5:1.5:5:5:0.0"
        ),
        "Documentary": (
            "eq=saturation=0.85:contrast=1.1:brightness=0.0,"
            "curves=psych"
        ),
        "Science Explainer": (
            "eq=saturation=1.2:contrast=1.15:brightness=0.05,"
            "colorchannelmixer=rr=0.8:rg=0:rb=0:gr=0:gg=0.9:gb=0:br=0:bg=0:bb=1.3"
        ),
        "Luxury Storytelling": (
            "eq=saturation=0.9:contrast=1.05:brightness=0.02,"
            "colorchannelmixer=rr=1.1:rg=0:rb=0:gr=0:gg=0.95:gb=0:br=0:bg=0:bb=0.8"
        ),
        "Viral Shorts": (
            "eq=saturation=1.6:contrast=1.3:brightness=0.05,"
            "unsharp=3:3:1.0:3:3:0.0"
        ),
    }
    return filters.get(style, "eq=saturation=1.0")

def get_caption_style(style: str, position: str):
    positions = {
        "top": "Alignment=8",
        "center": "Alignment=5",
        "bottom": "Alignment=2",
    }
    align = positions.get(position, "Alignment=2")
    styles = {
        "Horror Cinematic": f"FontName=Arial,FontSize=24,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,{align}",
        "Anime Recap": f"FontName=Arial,FontSize=28,PrimaryColour=&H00FFFFFF,OutlineColour=&H000000FF,BorderStyle=1,Outline=3,{align}",
        "Documentary": f"FontName=Arial,FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=1,{align}",
        "Science Explainer": f"FontName=Arial,FontSize=24,PrimaryColour=&H0000FF00,OutlineColour=&H00000000,BorderStyle=1,Outline=2,{align}",
        "Luxury Storytelling": f"FontName=Arial,FontSize=22,PrimaryColour=&H007EC9E8,OutlineColour=&H00000000,BorderStyle=1,Outline=1,{align}",
        "Viral Shorts": f"FontName=Arial,FontSize=30,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=3,{align}",
    }
    return styles.get(style, styles["Documentary"])

def get_resolution(aspect_ratio: str):
    ratios = {
        "16:9": (1920, 1080),
        "9:16": (1080, 1920),
        "1:1": (1080, 1080),
    }
    return ratios.get(aspect_ratio, (1920, 1080))

def generate_captions(audio_path: str, output_dir: str, caption_type: str):
    try:
        import whisper
        model = whisper.load_model("tiny")
        result = model.transcribe(audio_path)
        srt_path = f"{output_dir}/captions.srt"

        with open(srt_path, "w") as f:
            counter = 1
            for segment in result["segments"]:
                start = segment["start"]
                end = segment["end"]
                text = segment["text"].strip()

                def to_srt_time(seconds):
                    h = int(seconds // 3600)
                    m = int((seconds % 3600) // 60)
                    s = int(seconds % 60)
                    ms = int((seconds % 1) * 1000)
                    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

                if caption_type == "word":
                    words = text.split()
                    word_duration = (end - start) / max(len(words), 1)
                    for j, word in enumerate(words):
                        w_start = start + j * word_duration
                        w_end = w_start + word_duration
                        f.write(f"{counter}\n")
                        f.write(f"{to_srt_time(w_start)} --> {to_srt_time(w_end)}\n")
                        f.write(f"{word}\n\n")
                        counter += 1
                else:
                    f.write(f"{counter}\n")
                    f.write(f"{to_srt_time(start)} --> {to_srt_time(end)}\n")
                    f.write(f"{text}\n\n")
                    counter += 1

        return srt_path
    except Exception as e:
        print(f"Caption error: {e}")
        return None

@app.get("/")
def root():
    return {"message": "StoryMotion Studio API is running"}

@app.post("/upload")
async def upload_files(
    images: List[UploadFile] = File(...),
    audio: Optional[UploadFile] = File(None),
    music: Optional[UploadFile] = File(None),
):
    job_id = str(uuid.uuid4())
    os.makedirs(f"uploads/{job_id}", exist_ok=True)

    saved_images = []
    for i, image in enumerate(images):
        ext = image.filename.split(".")[-1]
        path = f"uploads/{job_id}/{i:04d}.{ext}"
        with open(path, "wb") as f:
            content = await image.read()
            f.write(content)
        saved_images.append(path)

    audio_path = None
    if audio:
        audio_ext = audio.filename.split(".")[-1]
        audio_path = f"uploads/{job_id}/narration.{audio_ext}"
        with open(audio_path, "wb") as f:
            content = await audio.read()
            f.write(content)

    music_path = None
    if music:
        music_ext = music.filename.split(".")[-1]
        music_path = f"uploads/{job_id}/music.{music_ext}"
        with open(music_path, "wb") as f:
            content = await music.read()
            f.write(content)

    jobs[job_id] = {
        "status": "uploaded",
        "images": saved_images,
        "audio": audio_path,
        "music": music_path,
        "progress": 0,
    }

    return {"job_id": job_id, "images": saved_images, "audio": audio_path, "music": music_path}

@app.post("/generate/{job_id}")
def generate(
    job_id: str,
    style: str,
    intensity: str,
    aspect_ratio: str = "16:9",
    caption_position: str = "bottom",
    caption_type: str = "sentence",
):
    if job_id not in jobs:
        return {"error": "Job not found"}

    jobs[job_id]["status"] = "processing"
    jobs[job_id]["progress"] = 0

    images = jobs[job_id]["images"]
    audio_path = jobs[job_id]["audio"]
    music_path = jobs[job_id]["music"]
    output_dir = f"outputs/{job_id}"
    os.makedirs(output_dir, exist_ok=True)

    width, height = get_resolution(aspect_ratio)

    durations = {
        "Low Motion": 6,
        "Medium Motion": 4,
        "High Motion": 3,
        "Cinematic": 5,
    }
    duration = durations.get(intensity, 4)

    try:
        # Step 1 — Resize images
        jobs[job_id]["progress"] = 10
        resized_dir = f"uploads/{job_id}/resized"
        os.makedirs(resized_dir, exist_ok=True)

        for i, img_path in enumerate(images):
            resized_path = f"{resized_dir}/{i:04d}.jpg"
            subprocess.run([
                "ffmpeg", "-y",
                "-i", img_path,
                "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black",
                resized_path
            ], check=True, capture_output=True)

        # Step 2 — Get audio duration
        jobs[job_id]["progress"] = 20
        total_duration = len(images) * duration
        if audio_path:
            result = subprocess.run([
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                audio_path
            ], capture_output=True, text=True)
            try:
                total_duration = float(result.stdout.strip())
                duration = total_duration / len(images)
            except:
                pass

        # Step 3 — Generate captions
        jobs[job_id]["progress"] = 30
        srt_path = None
        if audio_path:
            srt_path = generate_captions(audio_path, output_dir, caption_type)

        # Step 4 — Create clips with zoom + style filter
        jobs[job_id]["progress"] = 50
        clips_dir = f"uploads/{job_id}/clips"
        os.makedirs(clips_dir, exist_ok=True)
        zoom_filter = get_zoom_filter(intensity, width, height)
        style_filter = get_style_filter(style)
        combined_filter = f"{zoom_filter},{style_filter}"

        for i in range(len(images)):
            clip_path = f"{clips_dir}/{i:04d}.mp4"
            subprocess.run([
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", f"{resized_dir}/{i:04d}.jpg",
                "-vf", combined_filter,
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-t", str(duration),
                clip_path
            ], check=True, capture_output=True)

        # Step 5 — Concatenate with transitions
        jobs[job_id]["progress"] = 65
        if len(images) == 1:
            concat_video = f"{clips_dir}/0000.mp4"
        else:
            transition = get_transition(style)
            transition_duration = 0.5
            filter_parts = []
            prev = "[0:v]"

            for i in range(1, len(images)):
                offset = (duration * i) - (transition_duration * i)
                curr = f"[{i}:v]"
                out = f"[v{i}]" if i < len(images) - 1 else "[vout]"
                filter_parts.append(
                    f"{prev}{curr}xfade=transition={transition}:duration={transition_duration}:offset={offset}{out}"
                )
                prev = f"[v{i}]"

            filter_complex = ";".join(filter_parts)
            concat_video = f"{output_dir}/concat.mp4"

            cmd = ["ffmpeg", "-y"]
            for i in range(len(images)):
                cmd += ["-i", f"{clips_dir}/{i:04d}.mp4"]
            cmd += [
                "-filter_complex", filter_complex,
                "-map", "[vout]",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                concat_video
            ]
            subprocess.run(cmd, check=True, capture_output=True)

        # Step 6 — Mix audio + music
        jobs[job_id]["progress"] = 75
        audio_video = f"{output_dir}/with_audio.mp4"

        if audio_path and music_path:
            subprocess.run([
                "ffmpeg", "-y",
                "-i", concat_video,
                "-i", audio_path,
                "-i", music_path,
                "-filter_complex",
                "[2:a]volume=0.3[music];[1:a][music]amix=inputs=2:duration=first[aout]",
                "-map", "0:v",
                "-map", "[aout]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                audio_video
            ], check=True, capture_output=True)
        elif audio_path:
            subprocess.run([
                "ffmpeg", "-y",
                "-i", concat_video,
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                audio_video
            ], check=True, capture_output=True)
        elif music_path:
            subprocess.run([
                "ffmpeg", "-y",
                "-i", concat_video,
                "-i", music_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                audio_video
            ], check=True, capture_output=True)
        else:
            shutil.copy(concat_video, audio_video)

        # Step 7 — Burn captions
        jobs[job_id]["progress"] = 90
        output_path = f"{output_dir}/video.mp4"
        if srt_path and os.path.exists(srt_path):
            caption_style = get_caption_style(style, caption_position)
            subprocess.run([
                "ffmpeg", "-y",
                "-i", audio_video,
                "-vf", f"subtitles={srt_path}:force_style='{caption_style}'",
                "-c:a", "copy",
                output_path
            ], check=True, capture_output=True)
        else:
            shutil.copy(audio_video, output_path)

        jobs[job_id]["status"] = "done"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["output"] = output_path

        return {"job_id": job_id, "status": "done"}

    except Exception as e:
        jobs[job_id]["status"] = "error"
        return {"job_id": job_id, "status": "error", "error": str(e)}

@app.get("/status/{job_id}")
def status(job_id: str):
    if job_id not in jobs:
        return {"error": "Job not found"}
    return jobs[job_id]

@app.get("/download/{job_id}")
def download(job_id: str):
    if job_id not in jobs:
        return {"error": "Job not found"}
    if jobs[job_id]["status"] != "done":
        return {"error": "Video not ready yet"}
    return FileResponse(
        jobs[job_id]["output"],
        media_type="video/mp4",
        filename="storymotionstudio.mp4"
    )

@app.post("/graphics/counter")
def create_counter(
    start: int = 0,
    end: int = 1000000,
    duration: float = 3.0,
    prefix: str = "",
    suffix: str = "",
    label: str = "",
    style: str = "default",
    aspect_ratio: str = "16:9",
):
    job_id = str(uuid.uuid4())
    output_dir = f"outputs/{job_id}"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/counter.mp4"
    width, height = get_resolution(aspect_ratio)

    draw_counter(
        output_path=output_path,
        start=start,
        end=end,
        duration=duration,
        prefix=prefix,
        suffix=suffix,
        label=label,
        style=style,
        width=width,
        height=height,
    )

    jobs[job_id] = {"status": "done", "output": output_path}
    return {"job_id": job_id, "status": "done"}

@app.post("/graphics/barchart")
def create_bar_chart(
    labels: str = "India,China,USA",
    values: str = "1400,1410,340",
    title: str = "",
    duration: float = 3.0,
    aspect_ratio: str = "16:9",
):
    job_id = str(uuid.uuid4())
    output_dir = f"outputs/{job_id}"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/barchart.mp4"
    width, height = get_resolution(aspect_ratio)

    draw_bar_chart(
        output_path=output_path,
        labels=labels.split(","),
        values=[int(v) for v in values.split(",")],
        title=title,
        duration=duration,
        width=width,
        height=height,
    )

    jobs[job_id] = {"status": "done", "output": output_path}
    return {"job_id": job_id, "status": "done"}

@app.post("/graphics/piechart")
def create_pie_chart(
    labels: str = "Category A,Category B,Category C",
    values: str = "50,30,20",
    title: str = "",
    duration: float = 3.0,
    aspect_ratio: str = "16:9",
):
    job_id = str(uuid.uuid4())
    output_dir = f"outputs/{job_id}"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/piechart.mp4"
    width, height = get_resolution(aspect_ratio)

    draw_pie_chart(
        output_path=output_path,
        labels=labels.split(","),
        values=[int(v) for v in values.split(",")],
        title=title,
        duration=duration,
        width=width,
        height=height,
    )

    jobs[job_id] = {"status": "done", "output": output_path}
    return {"job_id": job_id, "status": "done"}

@app.post("/graphics/timeline")
def create_timeline(
    events: str = '2007:iPhone,2010:Instagram,2022:ChatGPT',
    title: str = "",
    duration: float = 4.0,
    aspect_ratio: str = "16:9",
):
    job_id = str(uuid.uuid4())
    output_dir = f"outputs/{job_id}"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/timeline.mp4"
    width, height = get_resolution(aspect_ratio)

    parsed_events = []
    for e in events.split(","):
        parts = e.split(":")
        if len(parts) == 2:
            parsed_events.append({"year": parts[0], "label": parts[1]})

    draw_timeline(
        output_path=output_path,
        events=parsed_events,
        title=title,
        duration=duration,
        width=width,
        height=height,
    )

    jobs[job_id] = {"status": "done", "output": output_path}
    return {"job_id": job_id, "status": "done"}

@app.post("/assets/icon")
def create_icon(
    icon: str = "rocket",
    label: str = "",
    duration: float = 2.0,
    animation: str = "zoom",
    aspect_ratio: str = "16:9",
):
    job_id = str(uuid.uuid4())
    output_dir = f"outputs/{job_id}"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/icon.mp4"
    width, height = get_resolution(aspect_ratio)
    draw_icon_scene(
        output_path=output_path,
        icon_key=icon,
        label=label,
        duration=duration,
        width=width,
        height=height,
        animation=animation,
    )
    jobs[job_id] = {"status": "done", "output": output_path}
    return {"job_id": job_id, "status": "done"}

@app.post("/assets/text")
def create_text_overlay(
    lines: str = "StoryMotion Studio,Universal Content Engine,Built for Creators",
    duration: float = 3.0,
    animation: str = "slideup",
    aspect_ratio: str = "16:9",
):
    job_id = str(uuid.uuid4())
    output_dir = f"outputs/{job_id}"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/text.mp4"
    width, height = get_resolution(aspect_ratio)
    draw_text_overlay(
        output_path=output_path,
        lines=lines.split(","),
        duration=duration,
        width=width,
        height=height,
        animation=animation,
    )
    jobs[job_id] = {"status": "done", "output": output_path}
    return {"job_id": job_id, "status": "done"}

@app.post("/assets/comparison")
def create_comparison(
    left_label: str = "Before",
    right_label: str = "After",
    left_value: int = 100,
    right_value: int = 850,
    title: str = "Comparison",
    duration: float = 3.0,
    aspect_ratio: str = "16:9",
):
    job_id = str(uuid.uuid4())
    output_dir = f"outputs/{job_id}"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/comparison.mp4"
    width, height = get_resolution(aspect_ratio)
    draw_comparison(
        output_path=output_path,
        left_label=left_label,
        right_label=right_label,
        left_value=left_value,
        right_value=right_value,
        title=title,
        duration=duration,
        width=width,
        height=height,
    )
    jobs[job_id] = {"status": "done", "output": output_path}
    return {"job_id": job_id, "status": "done"}

@app.post("/assets/progressbar")
def create_progress_bar(
    label: str = "Market Share",
    percentage: int = 75,
    duration: float = 2.0,
    aspect_ratio: str = "16:9",
):
    job_id = str(uuid.uuid4())
    output_dir = f"outputs/{job_id}"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/progressbar.mp4"
    width, height = get_resolution(aspect_ratio)
    draw_progress_bar(
        output_path=output_path,
        label=label,
        percentage=percentage,
        duration=duration,
        width=width,
        height=height,
    )
    jobs[job_id] = {"status": "done", "output": output_path}
    return {"job_id": job_id, "status": "done"}        

@app.post("/ai/script")
def create_script(
    topic: str = "Why do airplanes survive lightning?",
    style: str = "Science Explainer",
    duration: int = 60,
):
    try:
        script = generate_script(topic=topic, style=style, duration=duration)
        return {"status": "done", "script": script}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/ai/generate")
def ai_generate(
    topic: str = "Why do airplanes survive lightning?",
    style: str = "Science Explainer",
    duration: int = 60,
    aspect_ratio: str = "16:9",
):
    try:
        job_id = str(uuid.uuid4())
        output_dir = f"outputs/{job_id}"
        os.makedirs(output_dir, exist_ok=True)

        jobs[job_id] = {"status": "processing", "progress": 5}

        # Step 1 — Generate script
        script = generate_script(topic=topic, style=style, duration=duration)
        scenes = script.get("scenes", [])
        clip_paths = []

        width, height = get_resolution(aspect_ratio)
        jobs[job_id]["progress"] = 15

        total_scenes = len(scenes)

        # Step 2 — Generate each scene
        for i, scene in enumerate(scenes):
            clip_path = f"{output_dir}/scene_{i:04d}.mp4"
            asset_type = scene.get("asset_type", "graphic")
            graphic_type = scene.get("graphic_type")
            graphic_data = scene.get("graphic_data", {}) or {}
            scene_duration = scene.get("duration", 5)

            jobs[job_id]["progress"] = 15 + int((i / max(total_scenes, 1)) * 70)

            if asset_type == "image":
                # Generate AI image for this scene
                img_path = f"{output_dir}/scene_{i:04d}.png"
                visual_prompt = scene.get("visual", scene.get("narration", topic))
                result = generate_image(visual_prompt, img_path, style=style)

                if result and os.path.exists(img_path):
                    # Resize and apply zoom + style filter
                    zoom_filter = get_zoom_filter("Medium Motion", width, height)
                    style_filter = get_style_filter(style)
                    subprocess.run([
                        "ffmpeg", "-y",
                        "-loop", "1",
                        "-i", img_path,
                        "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black,{zoom_filter},{style_filter}",
                        "-c:v", "libx264",
                        "-pix_fmt", "yuv420p",
                        "-t", str(scene_duration),
                        clip_path
                    ], check=True, capture_output=True)
                else:
                    # Fallback to text overlay if image generation fails
                    draw_text_overlay(
                        output_path=clip_path,
                        lines=[scene.get("visual", "Scene")],
                        duration=scene_duration,
                        width=width,
                        height=height,
                    )

            elif asset_type == "graphic" and graphic_type:
                if graphic_type == "counter":
                    draw_counter(
                        output_path=clip_path,
                        start=graphic_data.get("start", 0),
                        end=graphic_data.get("end", 1000000),
                        duration=scene_duration,
                        prefix=graphic_data.get("prefix", ""),
                        suffix=graphic_data.get("suffix", ""),
                        label=graphic_data.get("label", ""),
                        width=width,
                        height=height,
                    )
                elif graphic_type == "barchart":
                    draw_bar_chart(
                        output_path=clip_path,
                        labels=str(graphic_data.get("labels", "A,B,C")).split(","),
                        values=[int(v) for v in str(graphic_data.get("values", "100,200,300")).split(",")],
                        title=graphic_data.get("title", ""),
                        duration=scene_duration,
                        width=width,
                        height=height,
                    )
                elif graphic_type == "piechart":
                    draw_pie_chart(
                        output_path=clip_path,
                        labels=str(graphic_data.get("labels", "A,B,C")).split(","),
                        values=[int(v) for v in str(graphic_data.get("values", "50,30,20")).split(",")],
                        title=graphic_data.get("title", ""),
                        duration=scene_duration,
                        width=width,
                        height=height,
                    )
                elif graphic_type == "timeline":
                    events_raw = str(graphic_data.get("events", "2020:Event"))
                    parsed_events = []
                    for e in events_raw.split(","):
                        parts = e.split(":")
                        if len(parts) == 2:
                            parsed_events.append({"year": parts[0], "label": parts[1]})
                    draw_timeline(
                        output_path=clip_path,
                        events=parsed_events,
                        title=graphic_data.get("title", ""),
                        duration=scene_duration,
                        width=width,
                        height=height,
                    )
                elif graphic_type == "text":
                    draw_text_overlay(
                        output_path=clip_path,
                        lines=str(graphic_data.get("lines", "Text")).split(","),
                        duration=scene_duration,
                        width=width,
                        height=height,
                    )
                elif graphic_type == "progressbar":
                    draw_progress_bar(
                        output_path=clip_path,
                        label=graphic_data.get("label", "Progress"),
                        percentage=int(graphic_data.get("percentage", 75)),
                        duration=scene_duration,
                        width=width,
                        height=height,
                    )
                elif graphic_type == "icon":
                    draw_icon_scene(
                        output_path=clip_path,
                        icon_key=graphic_data.get("icon", "star"),
                        label=graphic_data.get("label", ""),
                        duration=scene_duration,
                        width=width,
                        height=height,
                    )
                else:
                    draw_text_overlay(
                        output_path=clip_path,
                        lines=[scene.get("visual", "Scene")],
                        duration=scene_duration,
                        width=width,
                        height=height,
                    )
            else:
                draw_text_overlay(
                    output_path=clip_path,
                    lines=[scene.get("visual", "Scene")],
                    duration=scene_duration,
                    width=width,
                    height=height,
                )

            clip_paths.append(clip_path)

        jobs[job_id]["progress"] = 88

        # Step 3 — Concatenate all scenes
        if len(clip_paths) == 1:
            concat_video = clip_paths[0]
        else:
            concat_file = f"{output_dir}/concat.txt"
            with open(concat_file, "w") as f:
                for cp in clip_paths:
                    f.write(f"file '{os.path.abspath(cp)}'\n")

            concat_video = f"{output_dir}/concat.mp4"
            subprocess.run([
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                concat_video
            ], check=True, capture_output=True)

        jobs[job_id]["progress"] = 95

        # Step 4 — Add narration voice if needed (TTS) — skipped for now, silent video
        final_video = f"{output_dir}/video.mp4"
        shutil.copy(concat_video, final_video)

        jobs[job_id] = {
            "status": "done",
            "output": final_video,
            "script": script,
            "progress": 100,
        }

        return {
            "job_id": job_id,
            "status": "done",
            "title": script.get("title", ""),
            "scenes": len(scenes),
        }

    except Exception as e:
        jobs[job_id] = {"status": "error", "error": str(e)}
        return {"status": "error", "error": str(e)}