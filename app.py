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

BATCH_SIZE = 10

# ✅ تحميل ملف واحد (صورة أو صوت)
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

# ✅ تشغيل ffmpeg لبث الصورة والصوت مباشرة
def stream_video(image_path, audio_path):
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio_path,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,"
               "pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setrange=full,format=yuv420p",
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-shortest", "-f", "flv",
        f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"
    ]
    subprocess.run(cmd)

# ✅ حذف الكاش (الملف بعد البث)
def delete_cache(image_path, audio_path):
    for path in [image_path, audio_path]:
        try:
            os.remove(path)
            print(f"🗑️ تم حذف الكاش: {path}")
        except Exception as e:
            print(f"⚠️ فشل حذف {path}: {e}")

# ✅ تحميل دفعة من الملفات (صور وصوت)
async def fetch_batch(start_index):
    batch = []
    for i in range(start_index, start_index + BATCH_SIZE):
        img_name = f"{i}.jpg"
        aud_name = f"{i}.mp4"
        img_path = os.path.join(LOCAL_DIR, img_name)
        aud_path = os.path.join(LOCAL_DIR, aud_name)
        img_url = BASE_URL + img_name
        aud_url = BASE_URL + aud_name

        success_img = download_file(img_url, img_path)
        success_aud = download_file(aud_url, aud_path)

        if success_img and success_aud:
            batch.append((img_path, aud_path))
        else:
            print(f"⚠️ فشل تحميل الصفحة {i}")
    return batch

# ✅ تشغيل دفعة الصور والصوت، وتحميل التالية قبل انتهاء الأخيرة
async def stream_batches():
    index = 1
    current_batch = await fetch_batch(index)
    index += BATCH_SIZE

    while current_batch:
        # بدء تحميل الدفعة التالية أثناء تشغيل الدفعة الحالية
        next_batch_task = asyncio.create_task(fetch_batch(index))
        index += BATCH_SIZE

        for i, (image_path, audio_path) in enumerate(current_batch):
            print(f"🎬 بدء بث الصفحة: {image_path} + {audio_path}")
            stream_video(image_path, audio_path)
            delete_cache(image_path, audio_path)

        print("✅ انتهاء الدفعة، ننتقل للتالية...")
        current_batch = await next_batch_task

# ✅ نقطة دخول السيرفر
@app.route("/")
def index():
    asyncio.run(stream_batches())
    return "📡 بدأ البث التلقائي عبر دفعات الصور والصوت"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
