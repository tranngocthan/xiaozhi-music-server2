from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse
import yt_dlp
import requests

app = FastAPI(title="XiaoZhi Music Server")

@app.get("/stream_pcm")
def search_and_get_info(song: str = Query(...), artist: str = Query("")):
    query = f"{song} {artist}".strip()
    ydl_opts = {
        'format': 'bestaudio/best',
        'default_search': 'scsearch1:',  # Tìm trên SoundCloud (không bị chặn bot)
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info and len(info['entries']) > 0:
                entry = info['entries'][0]
            else:
                entry = info
            
            # Trả về URL stream trực tiếp hoặc qua endpoint proxy của server
            audio_url = entry.get('url')
            return {
                "title": entry.get('title', song),
                "artist": entry.get('uploader', artist),
                "audio_url": audio_url,
                "lyric_url": "",
                "duration": entry.get('duration', 0)
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
