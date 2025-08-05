import os
import subprocess
import requests
import re

# إعدادات البث
STREAM_KEY = os.getenv("STREAM_KEY")
BASE_URL = "https://raw.githubusercontent.com/ashergraysonadams/Quran/main/pages/"
LOCAL_DIR = "pages"
os.makedirs(LOCAL_DIR, exist_ok=True)

# استخراج رقم الصفحة من اسم الملف
def extract_number(filename):
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else -1

# تحميل ملف من الإنترنت إذا لم يكن موجودًا
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

# جمع أزواج الصور والصوت مرتبة حسب الرقم
def collect_ordered_pairs():
    pairs = []
    for index in range(1, 605):
        img_name = f"{index}.jpg"
        aud_name = f"{index}.mp4"
        img_path = os.path.join(LOCAL_DIR, img_name)
        aud_path = os.path.join(LOCAL_DIR, aud_name)

        img_url = BASE_URL + img_name
        aud_url = BASE_URL + aud_name

        success_img = download_file(img_url, img_path)
        success_aud = download_file(aud_url, aud_path)

        if success_img and success_aud:
            pairs.append((img_path, aud_path))
        else:
            print(f"⚠️ الصفحة {index} غير مكتملة، تم تخطيها.")
    return pairs

# تنفيذ البث باستخدام FFmpeg مع ضبط القياس إلى 9:16 (1080x1920) وحل تحذيرات pixel format
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
    print(f"🎙️ البث الآن: {os.path.basename(image_path)} + {os.path.basename(audio_path)}")
    subprocess.run(cmd)
    print(f"✅ انتهاء البث\n")

# برنامج التشغيل الرئيسي
def main():
    media_pairs = collect_ordered_pairs()
    for img, aud in media_pairs:
        stream_video(img, aud)

if __name__ == "__main__":
    main()
