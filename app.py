import os
import subprocess
import requests
import asyncio
from flask import Flask

app = Flask(__name__)

STREAM_KEY = os.getenv("STREAM_KEY")
BASE_URL = "https://raw.githubusercontent.com/ashergraysonadams/Quran/main/pages/"
LOCAL_DIR = "pages"
os.makedirs(LOCAL_DIR, exist_ok=True)

BATCH_SIZE = 2
MAX_PAGE = 604

# تحميل ملف من الإنترنت
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

# تنفيذ FFmpeg لبث صورة وصوت
def stream_video(image_path, audio_path):
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio_path,
        "-vf", "scale=720:1280:force_original_aspect_ratio=decrease,"
               "pad=720:1280:(ow-iw)/2:(oh-ih)/2,setrange=full,format=yuv420p",
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "ultrafast", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "96k",
        "-pix_fmt", "yuv420p",
        "-shortest", "-f", "flv",
        f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"
    ]
    subprocess.run(cmd)

# حذف الملفات بعد التشغيل
def delete_cache(*paths):
    for path in paths:
        try:
            os.remove(path)
            print(f"🗑️ حذف: {path}")
        except Exception as e:
            print(f"⚠️ لم يتم حذف {path}: {e}")

# تحميل دفعة من صفحتين فقط
async def fetch_batch(start_index):
    batch = []
    for i in range(start_index, start_index + BATCH_SIZE):
        page_num = ((i - 1) % MAX_PAGE) + 1  # إعادة من البداية بعد 604
        img_name = f"{page_num}.jpg"
        aud_name = f"{page_num}.mp4"
        img_path = os.path.join(LOCAL_DIR, img_name)
        aud_path = os.path.join(LOCAL_DIR, aud_name)
        img_url = BASE_URL + img_name
        aud_url = BASE_URL + aud_name

        if download_file(img_url, img_path) and download_file(aud_url, aud_path):
            batch.append((img_path, aud_path))
        else:
            print(f"⚠️ تخطي الصفحة {page_num}")
    return batch

# تشغيل الدفعات باستمرار، اثنين اثنين، ثم إعادة
async def stream_loop():
    index = 1
    while True:
        batch = await fetch_batch(index)
        for image_path, audio_path in batch:
            print(f"📡 بث: {image_path} + {audio_path}")
            stream_video(image_path, audio_path)
            delete_cache(image_path, audio_path)
        index += BATCH_SIZE

@app.route("/")
def index():
    asyncio.run(stream_loop())
    return "✅ بدأ البث المستمر صفحتين صفحتين مع إدارة ذكية للذاكرة"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
