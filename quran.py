import os
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

# Health check endpoint
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
# Telegram handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*تقدمة السيد حيدر الموسوي*\n"
        "بسم الله الرحمن الرحيم، وبه نستعين.\n\n"
        "📖 أرسل رقم الصفحة (1–620) لعرض صورة المصحف.\n"
        "🎧 أو اكتب: `ترتيل 45` لسماع التلاوة فقط.\n"
        "🧠 أو اكتب اسم حكم مثل: `ن الإظهار`، `مد طبيعي`، `البسملة`\n"
        "❓ اكتب `مساعدة` أو `الأوامر` لعرض القائمة الكاملة.",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_text = update.message.text.strip()
    text = raw_text

    if text == "السلام عليكم":
        return await update.message.reply_text("وعليكم السلام ورحمة الله وبركاته")

    if "صلوات" in text and "محمد" in text:
        return await update.message.reply_text("اللهم صَلِّ عَلَى مُحَمَّدٍ وَآلِ مُحَمَّدٍ")
    if text.isdigit():
        n = int(text)
        if 1 <= n <= 620:
            image_path = os.path.join(QURAN_PAGES_DIR, f"{n}.jpg")
            if os.path.exists(image_path):
                with open(image_path, "rb") as photo:
                    return await update.message.reply_photo(photo=photo)

    if raw_text.startswith("ترتيل "):
        parts = raw_text.split()
        if len(parts) == 2 and parts[1].isdigit():
            n = int(parts[1])
            if 1 <= n <= 604:
                audio_path = os.path.join(QURAN_PAGES_DIR, f"{n}.mp4")
                if os.path.exists(audio_path):
                    with open(audio_path, "rb") as audio:
                        return await update.message.reply_voice(voice=audio)

    if text == "البسملة":
        return await update.message.reply_text(
            "*البسملة:*\n"
            "﴿بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ﴾\n\n"
            "*تعريفها:*\n"
            "آية من الفاتحة، وتُقرأ في بداية كل سورة ما عدا التوبة.\n"
            "*أحكامها:*\n"
            "• لا يجوز وصل آخر السورة بالبسملة ثم الوقوف.\n"
            "• تُقال عند بدء التلاوة.\n"
            "*مثال:* ﴿بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ * الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ﴾",
            parse_mode="Markdown"
        )
        
    if text == "ن الإظهار":
        return await update.message.reply_text(
            "*الإظهار الحلقي:*\n"
            "الحروف: (ء، هـ، ع، ح، غ، خ)\n"
            "أمثلة: ﴿مِنْ هَادٍ﴾، ﴿إِنْ هُوَ﴾، ﴿مِنْ عِلْمٍ﴾",
            parse_mode="Markdown"
        )

    if text == "ن الإدغام":
        return await update.message.reply_text(
            "*الإدغام:*\n"
            "الحروف: (ي، ر، م، ل، و، ن)\n"
            "• بغنة: (ي، ن، م، و)\n"
            "• بغير غنة: (ر، ل)\n"
            "أمثلة: ﴿مِنْ مَالٍ﴾، ﴿مِنْ يَقُولُ﴾، ﴿غَفُورٌ رَّحِيمٌ﴾",
            parse_mode="Markdown"
        )

    if text == "ن الإقلاب":
        return await update.message.reply_text(
            "*الإقلاب:*\n"
            "الحرف: (ب)\n"
            "أمثلة: ﴿مِنْ بَعْدِ﴾، ﴿إِنْ بُعِثَ﴾",
            parse_mode="Markdown"
        )

    if text == "ن الإخفاء":
        return await update.message.reply_text(
            "*الإخفاء الحقيقي:*\n"
            "الحروف: باقي الحروف (15) ما عدا الإظهار والإدغام والإقلاب\n"
            "أمثلة: ﴿مِنْ صَلَاةٍ﴾، ﴿يُنْفِقُونَ﴾",
            parse_mode="Markdown"
        )
    if text == "م الإظهار":
        return await update.message.reply_text(
            "*الإظهار الشفوي:*\n"
            "الحروف: جميع الحروف ما عدا (ب، م)\n"
            "أمثلة: ﴿لَهُمْ أَجْرٌ﴾، ﴿فَهُمْ خَالِدُونَ﴾",
            parse_mode="Markdown"
        )

    if text == "م الإدغام":
        return await update.message.reply_text(
            "*الإدغام الشفوي:*\n"
            "الحرف: (م)\n"
            "أمثلة: ﴿كَمْ مِثْلِهِ﴾ → كَمْمِثْلِهِ، ﴿فَهُمْ مَغْفِرَةٌ﴾ → فَهُمْمَغْفِرَةٌ",
            parse_mode="Markdown"
        )

    if text == "م الإخفاء":
        return await update.message.reply_text(
            "*الإخفاء الشفوي:*\n"
            "الحرف: (ب)\n"
            "أمثلة: ﴿تَرْمِيهِمْ بِحِجَارَةٍ﴾، ﴿هُمْ بِرَبِّهِمْ﴾",
            parse_mode="Markdown"
        )
    if text == "مد طبيعي":
        return await update.message.reply_text(
            "*المد الطبيعي:*\n"
            "حروف المد: (ا، و، ي) بدون سبب.\n"
            "أمثلة: ﴿قَالَ﴾، ﴿فِيهِ﴾، ﴿يَقُولُ﴾",
            parse_mode="Markdown"
        )

    if text == "مد متصل":
        return await update.message.reply_text(
            "*المد المتصل:*\n"
            "حرف مد + همزة في نفس الكلمة.\n"
            "أمثلة: ﴿جَاءَ﴾، ﴿سُوءَ﴾، ﴿السماء﴾",
            parse_mode="Markdown"
        )

    if text == "مد منفصل":
        return await update.message.reply_text(
            "*المد المنفصل:*\n"
            "حرف مد في آخر الكلمة، والهمزة في أول الكلمة التالية.\n"
            "أمثلة: ﴿يَا أَيُّهَا﴾، ﴿إِنَّا أَنْزَلْنَاهُ﴾",
            parse_mode="Markdown"
        )

    if text == "مد لازم":
        return await update.message.reply_text(
            "*المد اللازم:*\n"
            "يأتي بعده حرف ساكن أصلي ويُمد 6 حركات.\n"
            "أمثلة: ﴿الضَّالِّينَ﴾، ﴿الْحَاقَّةُ﴾، ﴿الصَّاخَّةُ﴾",
            parse_mode="Markdown"
        )
    if text in ["مساعدة", "الأوامر", "الاوامر"]:
        return await update.message.reply_text(
            "*قائمة الأوامر:*\n\n"
            "📖 *عرض صفحات المصحف:*\n"
            "أرسل رقم الصفحة من 1 إلى 620\n\n"
            "🎧 *تشغيل التلاوة:* `ترتيل 45`\n\n"
            "🧠 *أحكام النون الساكنة والتنوين:*\n"
            "`ن الإظهار`، `ن الإدغام`، `ن الإقلاب`، `ن الإخفاء`\n\n"
            "🧠 *أحكام الميم الساكنة:*\n"
            "`م الإظهار`، `م الإدغام`، `م الإخفاء`\n\n"
            "📏 *المدود:*\n"
            "`مد طبيعي`، `مد متصل`، `مد منفصل`، `مد لازم`\n\n"
            "🌸 *أوامر إضافية:*\n"
            "`البسملة`، `السلام عليكم`، `صلوات على محمد`",
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
