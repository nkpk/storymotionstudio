from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uuid
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store jobs in memory for now
jobs = {}

@app.get("/")
def root():
    return {"message": "StoryMotion Studio API is running"}

@app.post("/upload")
async def upload_files(
    images: List[UploadFile] = File(...),
):
    job_id = str(uuid.uuid4())
    
    # Save uploaded images
    os.makedirs(f"uploads/{job_id}", exist_ok=True)
    
    saved_files = []
    for image in images:
        path = f"uploads/{job_id}/{image.filename}"
        with open(path, "wb") as f:
            content = await image.read()
            f.write(content)
        saved_files.append(image.filename)
    
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
    
    # Video generation will go here
    jobs[job_id]["status"] = "done"
    
    return {"job_id": job_id, "status": "done"}

@app.get("/status/{job_id}")
def status(job_id: str):
    if job_id not in jobs:
        return {"error": "Job not found"}
    return jobs[job_id]