import re
from googleapiclient.discovery import build

def get_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

def get_transcript_from_youtube_url(url, api_key):
    video_id = get_video_id(url)
    if not video_id:
        return "Invalid YouTube URL"
    yt = build("youtube", "v3", developerKey=api_key)
    try:
        results = yt.captions().list(part="snippet", videoId=video_id).execute()
        caption = results.get("items", [])[0]
        cid = caption["id"]
        response = yt.captions().download(id=cid).execute()
        return re.sub(r"<[^>]+>", "", response)
    except Exception:
        return "No caption available"
