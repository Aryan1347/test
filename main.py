from fastapi import FastAPI, HTTPException
import subprocess
import tempfile
import os
import json
from pydantic import BaseModel

app = FastAPI(title="ytagent Test Server")

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
        result = subprocess.run(
            ["ytagent", "download", url, "--out-dir", out_dir, "--format", "best[height<=720]/best"],
            capture_output=True,
            text=True,
            timeout=60,
            check=True
        )

        # ytagent downloads to out_dir
        files = os.listdir(out_dir)
        if not files:
            # Fallback: ytagent might use default 'downloads' dir
            default_downloads = "downloads"
            if os.path.isdir(default_downloads) and os.listdir(default_downloads):
                files = os.listdir(default_downloads)
                out_dir = default_downloads
            else:
                raise HTTPException(status_code=500, detail="No files downloaded")

        file_path = os.path.join(out_dir, files[0])
        size = os.path.getsize(file_path)

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
        