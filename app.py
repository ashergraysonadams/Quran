import os
import subprocess
import requests
import re
from flask import Flask

app = Flask(__name__)

STREAM_KEY = os.getenv("STREAM_KEY")
BASE_URL = "https://raw.githubusercontent.com/ashergraysonadams/Quran/main/pages/"
LOCAL_DIR = "pages"
os.makedirs(LOCAL_DIR, exist_ok=True)

def download_file(url, path):
    if os.path.exists(path):
        return True
    try:
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        with open(path, "wb") as f:
            f.write(res.content)
        return True
    except Exception as e:
        print(f"❌ فشل تحميل {path}: {e}")
        return False

def stream_video(image_path, audio_path):
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio_path,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,"
               "pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setrange=full",
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-shortest", "-f", "flv",
        f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"
    ]
    subprocess.run(cmd)

@app.route("/")
def index():
    image_path = os.path.join(LOCAL_DIR, "1.jpg")
    audio_path = os.path.join(LOCAL_DIR, "1.mp4")

    img_url = BASE_URL + "1.jpg"
    aud_url = BASE_URL + "1.mp4"

    success_img = download_file(img_url, image_path)
    success_aud = download_file(aud_url, audio_path)

    if success_img and success_aud:
        stream_video(image_path, audio_path)
        return "✅ بدأ البث من الصفحة الأولى"
    else:
        return "⚠️ الملفات غير موجودة أو فشل التحميل"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
