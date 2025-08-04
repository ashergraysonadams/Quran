import os
import subprocess
import time

# إعدادات البث إلى YouTube Live
STREAM_KEY = os.getenv("STREAM_KEY")
RTMP_URL = f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"

# إعدادات البروكسي من متغيرات البيئة
http_proxy   = os.getenv("HTTP_PROXY")
https_proxy  = os.getenv("HTTPS_PROXY")
socks_proxy  = os.getenv("SOCKS_PROXY")

# تجهيز البيئة لتشغيل FFmpeg عبر subprocess
env = os.environ.copy()
if http_proxy:
    env["http_proxy"] = http_proxy
if https_proxy:
    env["https_proxy"] = https_proxy
if socks_proxy:
    env["all_proxy"] = socks_proxy  # SOCKS يستخدم all_proxy

def stream_video(image_path, audio_path):
    cmd = [
        "ffmpeg",
        "-y",                    # يسمح بالكتابة فوق الملفات المؤقتة
        "-loop", "1",            # تكرار الصورة الثابتة
        "-i", image_path,        # إدخال الصورة
        "-i", audio_path,        # إدخال الصوت من ملف mp4
        "-map", "0:v:0",         # استخدم الفيديو من الصورة فقط
        "-map", "1:a:0",         # استخدم الصوت فقط من ملف mp4
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-shortest",             # مدة الفيديو = مدة الصوت
        "-f", "flv",             # تنسيق البث إلى RTMP
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

    if not entries:
        print("⚠️ لا توجد تلاوات داخل ملف 'pages'.")
        return

    while True:  # إعادة التشغيل إلى ما لا نهاية
        for entry in entries:
            if len(entry) != 2:
                print(f"⚠️ تنسيق غير صالح في السطر: {entry}")
                continue

            image_file, audio_file = entry
            image_path = os.path.join("images", image_file)
            audio_path = os.path.join("audio", audio_file)

            if not os.path.exists(image_path) or not os.path.exists(audio_path):
                print(f"❌ ملف غير موجود: {image_file} أو {audio_file}")
                continue

            print(f"📡 بدء بث: {image_file} + {audio_file}")
            stream_video(image_path, audio_path)
            print(f"✅ تم تشغيل: {audio_file}")
            time.sleep(5)  # فاصل زمني بسيط قبل التلاوة التالية

        print("🔁 تم تشغيل جميع التلاوات. إعادة التشغيل من البداية...")
        time.sleep(3)  # فاصل زمني قبل بدء الحلقة الجديدة

if __name__ == "__main__":
    main()
