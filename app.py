from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI(title="Xiaozhi YouTube Music Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch1',
}

@app.get("/")
def root():
    return {"status": "ok", "message": "Xiaozhi YouTube Music Server is running"}

@app.get("/stream_pcm")
def stream_pcm(song: str = Query(..., description="Song name"), artist: str = Query("", description="Artist name")):
    query = f"{song} {artist}".strip()
    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            if not info or 'entries' not in info or len(info['entries']) == 0:
                raise HTTPException(status_code=404, detail="Song not found")

            video = info['entries'][0]
            audio_url = video.get('url')
            title = video.get('title', song)
            uploader = video.get('uploader', artist)
            duration = video.get('duration', 0)

            return {
                "title": title,
                "artist": uploader,
                "audio_url": audio_url,
                "lyric_url": "",
                "duration": float(duration)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
