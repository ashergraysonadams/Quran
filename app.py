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

# تحميل الملف من الإنترنت كـ bytes
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

# تشغيل FFmpeg باستخدام stdin pipe
def stream_direct(image_data, audio_data):
    try:
        proc = subprocess.Popen([
            "ffmpeg", "-y",
            "-loop", "1", "-i", "pipe:0",
            "-i", "pipe:1",
            "-vf", "scale=720:1280:force_original_aspect_ratio=decrease,"
                  "pad=720:1280:(ow-iw)/2:(oh-ih)/2,"
                  "colorlevels=rimin=0.0:gimin=0.0:bimin=0.0:rimax=1.0:gimax=1.0:bimax=1.0,"
                  "setrange=full,format=yuv420p",
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "libx264", "-preset", "ultrafast", "-tune", "stillimage", "-crf", "30",
            "-c:a", "aac", "-b:a", "64k",
            "-pix_fmt", "yuv420p",
            "-shortest", "-f", "flv",
            f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"
        ], stdin=subprocess.PIPE)

        proc.stdin.write(image_data)
        proc.stdin.write(audio_data)
        proc.stdin.close()
        proc.wait()

    except Exception as e:
        print(f"⚠️ خطأ أثناء البث: {e}")

# بث مستمر لدُفعات بدون تخزين
async def stream_loop():
    index = 1
    while True:
        for i in range(index, index + BATCH_SIZE):
            page_num = ((i - 1) % MAX_PAGE) + 1
            img_data, aud_data = fetch_data(page_num)
            if img_data and aud_data:
                print(f"📡 بث الصفحة {page_num}")
                stream_direct(img_data, aud_data)
                await asyncio.sleep(5)  # تأخير لتقليل الضغط على الخادم
        index += BATCH_SIZE

@app.route("/")
def index():
    asyncio.run(stream_loop())
    return "✅ بدأ البث المباشر بدون ملفات مؤقتة وبأقل استهلاك للذاكرة"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
