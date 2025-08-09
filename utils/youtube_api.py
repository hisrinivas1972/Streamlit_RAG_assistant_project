from googleapiclient.discovery import build
import re

def get_video_id(url):
    # Extract video ID from URL
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_youtube_captions(youtube_url, api_key):
    video_id = get_video_id(youtube_url)
    if not video_id:
        return None

    youtube = build('youtube', 'v3', developerKey=api_key)

    try:
        captions = youtube.captions().list(
            part="snippet",
            videoId=video_id
        ).execute()

        # Find English or auto-generated captions
        caption_id = None
        for item in captions.get("items", []):
            if item["snippet"]["language"] == "en":
                caption_id = item["id"]
                break
        if not caption_id and captions.get("items"):
            caption_id = captions["items"][0]["id"]

        if not caption_id:
            return None

        caption_response = youtube.captions().download(id=caption_id).execute()
        # The response is XML; strip tags simply here
        text = re.sub('<.*?>', '', caption_response)
        return text

    except Exception:
        return None
