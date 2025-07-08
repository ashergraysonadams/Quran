import os
import re
import asyncio
import threading
from aiohttp import web
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.environ.get("TOKEN")
QURAN_PAGES_DIR = os.path.join(os.path.dirname(__file__), "pages")
PORT = int(os.environ.get("PORT", 10000))

# —— Health‐check endpoint
async def health(request):
    return web.Response(text="OK")

async def start_health_server():
    app = web.Application()
    app.add_routes([web.get("/", health)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

def spawn_health_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_health_server())
    loop.run_forever()

# —— Telegram handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *تقدمة السيد حيدر الموسوي*\n"
        "بسم الله الرحمن الرحيم، وبه نستعين.\n"
        "🌙 أرسل رقم الصفحة (1–620) لعرض صورة المصحف.\n"
        "🎧 أو اكتب: `ترتيل 45` لسماع التلاوة فقط.\n"
        "🧠 أو اكتب اسم حكم مثل: `ن الإظهار`، `مد طبيعي`، `البسملة`\n"
        "❓ اكتب `مساعدة` أو `الأوامر` لعرض القائمة الكاملة.",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "السلام عليكم":
        return await update.message.reply_text("وعليكم السلام ورحمة الله وبركاته")

    if "صلوات" in text and "محمد" in text:
        return await update.message.reply_text("اللهم صَلِّ عَلَى مُحَمَّدٍ وَآلِ مُحَمَّدٍ")

    # ✅ إرسال صورة الصفحة فقط عند كتابة رقم
    if text.isdigit():
        n = int(text)
        if 1 <= n <= 620:
            image_path = os.path.join(QURAN_PAGES_DIR, f"{n}.jpg")
            if os.path.exists(image_path):
                with open(image_path, "rb") as photo:
                    return await update.message.reply_photo(photo=photo)

    # ✅ إرسال الصوت فقط عند كتابة "ترتيل X" مع فراغ
    if text.startswith("ترتيل "):
        parts = text.split()
        if len(parts) == 2 and parts[1].isdigit():
            n = int(parts[1])
            if 1 <= n <= 604:
                audio_path = os.path.join(QURAN_PAGES_DIR, f"{n}.ogg")
                if os.path.exists(audio_path):
                    with open(audio_path, "rb") as audio:
                        return await update.message.reply_voice(voice=audio)

    # ✅ البسملة (يدعم "البسملة" و"بسملة")
    if text in ["البسملة", "بسملة"]:
        return await update.message.reply_text(
            "🌸 *البسملة:*\n"
            "﴿بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ﴾\n\n"
            "📖 *تعريفها:*\n"
            "آية من الفاتحة، وتُقرأ في بداية كل سورة ما عدا التوبة.\n"
            "📌 *أحكامها:*\n"
            "• لا يجوز وصل آخر السورة بالبسملة ثم الوقوف.\n"
            "• تُقال عند بدء التلاوة.\n"
            "🧪 *مثال:* ﴿بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ * الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ﴾",
            parse_mode="Markdown"
        )

    if text == "ن الإظهار":
        return await update.message.reply_text(
            "🔹 *الإظهار الحلقي (في النون الساكنة والتنوين):*\n"
            "هو نطق النون الساكنة أو التنوين بوضوح دون غنة، إذا جاء بعدها أحد حروف الحلق.\n"
            "🧠 الحروف: (ء، هـ، ع، ح، غ، خ)\n"
            "🧪 *أمثلة:*\n"
            "• ﴿مِنْ هَادٍ﴾\n"
            "• ﴿إِنْ هُوَ﴾\n"
            "• ﴿مِنْ عِلْمٍ﴾",
            parse_mode="Markdown"
        )

    if text == "ن الإدغام":
        return await update.message.reply_text(
            "🔄 *الإدغام (في النون الساكنة والتنوين):*\n"
            "هو إدخال النون أو التنوين في الحرف التالي، بحيث يصيران حرفًا واحدًا مشددًا.\n"
            "🧠 الحروف: (ي، ر، م، ل، و، ن)\n"
            "• إدغام بغنة: (ي، ن، م، و)\n"
            "• إدغام بغير غنة: (ر، ل)\n"
            "🧪 *أمثلة:*\n"
            "• ﴿مِنْ مَالٍ﴾ → مِمَّالٍ\n"
            "• ﴿مِنْ يَقُولُ﴾ → مِـيَّقُولُ\n"
            "• ﴿غَفُورٌ رَّحِيمٌ﴾ → غَفُورُرَّحِيمٌ",
            parse_mode="Markdown"
        )
    if text == "ن الإقلاب":
        return await update.message.reply_text(
            "🔁 *الإقلاب (في النون الساكنة والتنوين):*\n"
            "هو قلب النون الساكنة أو التنوين إلى ميم خفيفة إذا جاء بعدها حرف الباء.\n"
            "🧪 *أمثلة:*\n"
            "• ﴿مِنْ بَعْدِ﴾ → مِمْ بَعْدِ",
            parse_mode="Markdown"
        )

    if text == "ن الإخفاء":
        return await update.message.reply_text(
            "🎧 *الإخفاء الحقيقي:* نطق النون أو التنوين بصوت خافت مع غنة.\n"
            "🧪 *أمثلة:*\n"
            "• ﴿مِنْ صَلَاةٍ﴾\n"
            "• ﴿يُنْفِقُونَ﴾",
            parse_mode="Markdown"
        )

    if text == "مد طبيعي":
        return await update.message.reply_text(
            "📏 *المد الطبيعي:* يُمد حركتين دون سبب.\n"
            "🧪 *أمثلة:*\n"
            "• ﴿قَالَ﴾\n"
            "• ﴿فِيهِ﴾",
            parse_mode="Markdown"
        )

    if text in ["مساعدة", "الأوامر"]:
        return await update.message.reply_text(
            "📜 *قائمة الأوامر:*\n"
            "• `ترتيل 45` لإرسال الصوت فقط\n"
            "• أرسل رقم الصفحة لعرض الصورة\n"
            "• `البسملة`، `ن الإظهار`، `مد طبيعي`، وغيرها",
            parse_mode="Markdown"
        )

# —— تشغيل البوت
def main():
    if not TOKEN:
        print("❌ TOKEN not set.")
        return

    threading.Thread(target=spawn_health_server, daemon=True).start()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print(f"✅ Bot started — health endpoint on port {PORT}")
    app.run_polling()

if __name__ == "__main__":
    main()
