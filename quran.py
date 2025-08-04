import os
import subprocess
import time

# إعدادات البث إلى يوتيوب
STREAM_KEY = os.getenv("STREAM_KEY")
RTMP_URL = f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"

# إعدادات البروكسي من متغيرات البيئة
http_proxy = os.getenv("HTTP_PROXY")
https_proxy = os.getenv("HTTPS_PROXY")
socks_proxy = os.getenv("SOCKS_PROXY")

# بناء بيئة FFmpeg مع البروكسيات
env = os.environ.copy()
if http_proxy:
    env["http_proxy"] = http_proxy
if https_proxy:
    env["https_proxy"] = https_proxy
if socks_proxy:
    env["all_proxy"] = socks_proxy  # يستخدم لكل أنواع الاتصالات (SOCKS)

def stream_video(image_path, audio_path):
    cmd = [
        "ffmpeg",
        "-y",                    # الكتابة فوق أي ملفات مؤقتة
        "-loop", "1",            # تكرار الصورة باستمرار
        "-i", image_path,        # الصورة
        "-i", audio_path,        # الصوت من ملف mp4
        "-map", "0:v:0",         # الفيديو من الصورة فقط
        "-map", "1:a:0",         # الصوت فقط من mp4
        "-c:v", "libx264",       # ترميز الفيديو
        "-preset", "veryfast",
        "-tune", "stillimage",
        "-c:a", "aac",           # ترميز الصوت
        "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-shortest",             # زمن الفيديو = زمن الصوت
        "-f", "flv",             # صيغة البث المباشر
        RTMP_URL
    ]
    subprocess.run(cmd, env=env)

def main():
    try:
        with open("pages", "r", encoding="utf-8") as f:
            entries = [line.strip().split(",") for line in f if line.strip()]
    except FileNotFoundError:
        print("❌ الملف 'pages' غير موجود.")
        return

    for entry in entries:
        if len(entry) != 2:
            print(f"⚠️ تنسيق غير صالح: {entry}")
            continue

        image_file, audio_file = entry
        image_path = os.path.join("images", image_file)
        audio_path = os.path.join("audio", audio_file)

        if not os.path.exists(image_path) or not os.path.exists(audio_path):
            print(f"❌ ملف مفقود: {image_file} أو {audio_file}")
            continue

        print(f"📡 بدء بث: {image_file} + {audio_file}")
        stream_video(image_path, audio_path)
        print(f"✅ انتهى: {audio_file}")
        time.sleep(5)  # فاصلة بسيطة بين التلاوات

if __name__ == "__main__":
    main()
