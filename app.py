from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI(title="Xiaozhi Music Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cấu hình lấy luồng MP3 trực tiếp không bị chặn bot
SC_OPTIONS = {
    'format': 'bestaudio[protocol^=http]/bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'scsearch1:',
}

# Cấu hình dự phòng YouTube client
YT_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch1:',
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'ios']
        }
    }
}

def extract_music(query: str):
    # 1. Thử nguồn nhạc MP3 trực tiếp (Cực nhanh, chuẩn 128k cho ESP32, không bị Cloud IP chặn)
    try:
        with yt_dlp.YoutubeDL(SC_OPTIONS) as ydl:
            info = ydl.extract_info(f"scsearch1:{query}", download=False)
            if info and 'entries' in info and len(info['entries']) > 0:
                video = info['entries'][0]
                audio_url = video.get('url')
                if audio_url:
                    return {
                        "title": video.get('title', query),
                        "artist": video.get('uploader', ''),
                        "audio_url": audio_url,
                        "lyric_url": "",
                        "duration": float(video.get('duration', 0) or 0)
                    }
    except Exception as e:
        print(f"Direct stream notice: {e}")

    # 2. Dự phòng YouTube
    try:
        with yt_dlp.YoutubeDL(YT_OPTIONS) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            if info and 'entries' in info and len(info['entries']) > 0:
                video = info['entries'][0]
                audio_url = video.get('url')
                if audio_url:
                    return {
                        "title": video.get('title', query),
                        "artist": video.get('uploader', ''),
                        "audio_url": audio_url,
                        "lyric_url": "",
                        "duration": float(video.get('duration', 0) or 0)
                    }
    except Exception as e:
        print(f"YouTube fallback notice: {e}")

    return None

@app.get("/")
def root():
    return {"status": "ok", "message": "Xiaozhi Music Server is running"}

@app.get("/stream_pcm")
def stream_pcm(song: str = Query(..., description="Song name"), artist: str = Query("", description="Artist name")):
    query = f"{song} {artist}".strip()
    result = extract_music(query)
    if not result:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài hát")
    return result
