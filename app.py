import os
import subprocess
import requests
import asyncio
from flask import Flask

app = Flask(__name__)

STREAM_KEY = os.getenv("STREAM_KEY")
BASE_URL = "https://raw.githubusercontent.com/ashergraysonadams/Quran/main/pages/"
MAX_PAGE = 604
BATCH_SIZE = 2

# بث عنصر (صورة + صوت) باستخدام FFmpeg عبر stdin
def stream_direct(image_data, audio_data):
    image_pipe = subprocess.Popen(["ffmpeg", "-y", "-loop", "1", "-i", "pipe:0",
                                   "-i", "pipe:1",
                                   "-vf", "scale=720:1280:force_original_aspect_ratio=decrease,"
                                          "pad=720:1280:(ow-iw)/2:(oh-ih)/2,setrange=full,format=yuv420p",
                                   "-map", "0:v:0", "-map", "1:a:0",
                                   "-c:v", "libx264", "-preset", "ultrafast", "-tune", "stillimage",
                                   "-c:a", "aac", "-b:a", "96k",
                                   "-pix_fmt", "yuv420p",
                                   "-shortest", "-f", "flv",
                                   f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"],
                                  stdin=subprocess.PIPE)

    try:
        image_pipe.stdin.write(image_data)
        image_pipe.stdin.close()
        audio_pipe = image_pipe.stdin
        audio_pipe.write(audio_data)
        audio_pipe.close()
        image_pipe.wait()
    except Exception as e:
        print(f"⚠️ خطأ أثناء البث: {e}")

# تحميل صورة وصوت مباشرة كـ bytes
def fetch_data(page_num):
    img_url = BASE_URL + f"{page_num}.jpg"
    aud_url = BASE_URL + f"{page_num}.mp4"
    try:
        img_res = requests.get(img_url, timeout=15)
        aud_res = requests.get(aud_url, timeout=30)
        img_res.raise_for_status()
        aud_res.raise_for_status()
        return img_res.content, aud_res.content
    except Exception as e:
        print(f"❌ فشل تحميل الصفحة {page_num}: {e}")
        return None, None

# بث الدفعات باستخدام pipe
async def stream_loop():
    index = 1
    while True:
        for i in range(index, index + BATCH_SIZE):
            page_num = ((i - 1) % MAX_PAGE) + 1
            img_data, aud_data = fetch_data(page_num)
            if img_data and aud_data:
                print(f"📡 بث الصفحة {page_num}")
                stream_direct(img_data, aud_data)
                await asyncio.sleep(1)  # يمكن تغييره حسب الحاجة
        index += BATCH_SIZE

@app.route("/")
def index():
    asyncio.run(stream_loop())
    return "✅ بدأ البث المباشر بدون تخزين ملفات، باستخدام stdin pipe"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
