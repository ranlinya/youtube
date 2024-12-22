from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
import yt_dlp
import json
import os
import asyncio
import uuid
from datetime import datetime

app = FastAPI()

# 挂载静态文件和模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 确保视频目录存在
VIDEOS_DIR = "static/videos"
os.makedirs(VIDEOS_DIR, exist_ok=True)

# 存储视频信息的JSON文件
VIDEOS_INFO_FILE = "videos_info.json"

def load_videos_info():
    if os.path.exists(VIDEOS_INFO_FILE):
        with open(VIDEOS_INFO_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_videos_info(info):
    with open(VIDEOS_INFO_FILE, 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

@app.get("/")
async def home(request: Request):
    videos = load_videos_info()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "videos": videos}
    )

@app.post("/download")
async def download_video(request: Request):
    form = await request.form()
    url = form.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    video_id = str(uuid.uuid4())
    
    # yt-dlp配置
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{VIDEOS_DIR}/{video_id}/%(title)s.%(ext)s',
        'quiet': True,
    }
    
    try:
        # 获取视频信息
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # 开始下载
            await asyncio.to_thread(ydl.download, [url])
            
            # 保存视频信息
            video_info = {
                'id': video_id,
                'title': info['title'],
                'duration': info['duration'],
                'uploader': info['uploader'],
                'description': info['description'],
                'file_path': f'/static/videos/{video_id}/{info["title"]}.{info["ext"]}',
                'download_date': datetime.now().isoformat(),
                'filesize': os.path.getsize(f'{VIDEOS_DIR}/{video_id}/{info["title"]}.{info["ext"]}'),
            }
            
            videos_info = load_videos_info()
            videos_info[video_id] = video_info
            save_videos_info(videos_info)
            
            return video_info
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/videos")
async def list_videos():
    return load_videos_info() 