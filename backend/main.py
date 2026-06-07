from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uuid
import os
import subprocess

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

jobs = {}

@app.get("/")
def root():
    return {"message": "StoryMotion Studio API is running"}

@app.post("/upload")
async def upload_files(
    images: List[UploadFile] = File(...),
):
    job_id = str(uuid.uuid4())
    os.makedirs(f"uploads/{job_id}", exist_ok=True)
    
    saved_files = []
    for i, image in enumerate(images):
        ext = image.filename.split(".")[-1]
        path = f"uploads/{job_id}/{i:04d}.{ext}"
        with open(path, "wb") as f:
            content = await image.read()
            f.write(content)
        saved_files.append(path)
    
    jobs[job_id] = {
        "status": "uploaded",
        "images": saved_files,
        "style": None,
        "intensity": None,
    }
    
    return {"job_id": job_id, "files": saved_files}

@app.post("/generate/{job_id}")
def generate(job_id: str, style: str, intensity: str):
    if job_id not in jobs:
        return {"error": "Job not found"}
    
    jobs[job_id]["status"] = "processing"
    jobs[job_id]["style"] = style
    jobs[job_id]["intensity"] = intensity
    
    images = jobs[job_id]["images"]
    output_dir = f"outputs/{job_id}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Duration per image based on intensity
    durations = {
        "Low Motion": 6,
        "Medium Motion": 4,
        "High Motion": 3,
        "Cinematic": 5,
    }
    duration = durations.get(intensity, 4)
    
    try:
        # Step 1: Resize all images to 1920x1080
        resized_dir = f"uploads/{job_id}/resized"
        os.makedirs(resized_dir, exist_ok=True)
        
        for i, img_path in enumerate(images):
            resized_path = f"{resized_dir}/{i:04d}.jpg"
            subprocess.run([
                "ffmpeg", "-y",
                "-i", img_path,
                "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black",
                resized_path
            ], check=True, capture_output=True)
        
        # Step 2: Create video from images
        output_path = f"{output_dir}/video.mp4"
        subprocess.run([
            "ffmpeg", "-y",
            "-framerate", f"1/{duration}",
            "-i", f"{resized_dir}/%04d.jpg",
            "-vf", "zoompan=z='min(zoom+0.001,1.3)':d=125:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',fps=25",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-t", str(len(images) * duration),
            output_path
        ], check=True, capture_output=True)
        
        jobs[job_id]["status"] = "done"
        jobs[job_id]["output"] = output_path
        
        return {"job_id": job_id, "status": "done", "output": output_path}
    
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
    from fastapi.responses import FileResponse
    if job_id not in jobs:
        return {"error": "Job not found"}
    if jobs[job_id]["status"] != "done":
        return {"error": "Video not ready yet"}
    return FileResponse(
        jobs[job_id]["output"],
        media_type="video/mp4",
        filename="storymotionstudio.mp4"
    )