import yt_dlp
import whisper

def download_audio(youtube_url, output_path="audio/audio.mp3"):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    return output_path

def transcribe_audio(audio_path):
    model = whisper.load_model("base")  # or "small" for faster but less accurate
    result = model.transcribe(audio_path)
    return result["text"]
