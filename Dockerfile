# استخدم صورة Python الرسمية
FROM python:3.11-slim

# تثبيت FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# إنشاء مجلد المشروع
WORKDIR /app

# نسخ السكربت والملفات المطلوبة
COPY . .

# تثبيت أي مكتبات Python (اختياري)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# تشغيل السكربت عند بدء الحاوية
CMD ["python", "quran.py"]
