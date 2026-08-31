from fastapi import FastAPI, HTTPException
import subprocess
import tempfile
import os
import json
from pydantic import BaseModel

app = FastAPI(title="yt-dlp Render Test")

class DownloadRequest(BaseModel):
    url: str

@app.get("/")
async def root():
    return {"message": "ytagent test server"}

@app.post("/download")
async def download_video(req: DownloadRequest):
    url = req.url
    out_dir = tempfile.mkdtemp()

    try:
        # Call ytagent CLI to download
        result = subprocess.run(
            ["ytagent", "download", url, "--output", out_dir, "--format", "best[height<=720]/best"],
            capture_output=True,
            text=True,
            timeout=60,
            check=True
        )
        
        # Parse JSON output (ytagent returns a JSON line with info)
        # Actually, ytagent might return the info as stdout; let's assume it prints a JSON object.
        # We'll just look for files.
        files = os.listdir(out_dir)
        if not files:
            raise HTTPException(status_code=500, detail="No files downloaded")
        file_path = os.path.join(out_dir, files[0])
        size = os.path.getsize(file_path)

        # We can also parse the JSON info from stdout
        info = json.loads(result.stdout) if result.stdout else {}
        return {
            "status": "ok",
            "title": info.get("title", "Unknown"),
            "duration": info.get("duration", 0),
            "size_mb": round(size / (1024*1024), 2),
            "file_path": file_path,
        }

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"ytagent error: {e.stderr}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))