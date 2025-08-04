import os
import subprocess
import requests

# مفتاح البث من متغير بيئة في Render
STREAM_KEY = os.getenv("STREAM_KEY")

# المسار الأساسي للملفات داخل مجلد pages في GitHub
BASE_URL = "https://raw.githubusercontent.com/ashergraysonadams/Quran/main/pages/"

# تحميل ملف من الإنترنت
def download_file(url, filename):
    try:
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        with open(filename, "wb") as f:
            f.write(res.content)
        return True
    except Exception as e:
        print(f"❌ خطأ في تحميل {filename}: {e}")
        return False

# تحميل صورة وصوت حسب الرقم
def prepare_assets(index):
    img_name = f"{index}.jpg"
    aud_name = f"{index}.mp4"

    img_url = BASE_URL + img_name
    aud_url = BASE_URL + aud_name

    success_img = download_file(img_url, img_name)
    success_aud = download_file(aud_url, aud_name)

    return (img_name if success_img else None), (aud_name if success_aud else None)

# بث صورة وصوت باستخدام FFmpeg مع البروكسي فقط أثناء البث
def stream_video(image_path, audio_path):
    env = os.environ.copy()

    # إعدادات البروكسي فقط أثناء البث
    for proxy_var in ["HTTP_PROXY", "HTTPS_PROXY", "SOCKS_PROXY"]:
        value = os.getenv(proxy_var)
        if value:
            env[proxy_var.lower()] = value
            if proxy_var == "SOCKS_PROXY":
                env["all_proxy"] = value

    cmd = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-i", image_path,
        "-i", audio_path,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-f", "flv",
        f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"
    ]

    print(f"🎙️ بدأ البث لـ: {image_path} + {audio_path}")
    subprocess.run(cmd, env=env)
    print(f"✅ تم الانتهاء من البث لـ: {image_path}\n")

# الحلقة الرئيسية: من 1 إلى 604
def main():
    for index in range(1, 605):
        print(f"\n📦 جاري تجهيز الصفحة {index}")
        image, audio = prepare_assets(index)
        if image and audio:
            stream_video(image, audio)
        else:
            print(f"⚠️ تعذر تحميل الملفات للصفحة {index}، سيتم تخطيها.")

if __name__ == "__main__":
    main()
