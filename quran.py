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
        "🌙 أرسل رقم الصفحة (1–620) أو اكتب اسم حكم مثل: ن، م، الإخفاء، مد طبيعي، بسملة...",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()

    if "السلام عليكم" in text:
        return await update.message.reply_text("وعليكم السلام ورحمة الله")
    if "صلوات" in text and "محمد" in text:
        return await update.message.reply_text("اللهم صَلِّ عَلَى مُحَمَّدٍ وَآلِ مُحَمَّدٍ")

    if text.isdigit():
        n = int(text)
        if 1 <= n <= 620:
            path = os.path.join(QURAN_PAGES_DIR, f"{n}.jpg")
            if os.path.exists(path):
                with open(path, "rb") as photo:
                    return await update.message.reply_photo(photo=photo)

    if text == "ن":
        return await update.message.reply_text(
            "📘 *أحكام النون الساكنة والتنوين:*\n"
            "1️⃣ الإظهار: ﴿مِنْ هَادٍ﴾\n"
            "2️⃣ الإدغام: ﴿مِنْ مَالٍ﴾ → مِمَّالٍ\n"
            "3️⃣ الإقلاب: ﴿سَمِيعٌ بَصِيرٌ﴾ → سَمِيعٌمْ بَصِيرٌ\n"
            "4️⃣ الإخفاء: ﴿مِنْ صَلَاةٍ﴾ → مِـنْـصَلَاةٍ\n"
            "🧠 كل حكم يُطبّق حسب الحرف التالي للنون أو التنوين.",
            parse_mode="Markdown"
        )

    if "الإخفاء" in text:
        return await update.message.reply_text(
            "🎧 *الإخفاء الحقيقي:*\n"
            "هو نطق النون الساكنة أو التنوين بصوت خافت بين الإظهار والإدغام مع غنة.\n"
            "🧪 أمثلة:\n"
            "• ﴿مِنْ صَلَاةٍ﴾\n"
            "• ﴿أَنْذَرْتَهُمْ﴾\n"
            "• ﴿يُنْفِقُونَ﴾",
            parse_mode="Markdown"
        )

    if text == "م":
        return await update.message.reply_text(
            "📗 *أحكام الميم الساكنة:*\n"
            "1️⃣ الإظهار الشفوي: ﴿لَهُمْ أَجْرٌ﴾\n"
            "2️⃣ الإدغام الشفوي: ﴿كَمْ مِثْلِهِ﴾ → كَمْمِثْلِهِ\n"
            "3️⃣ الإخفاء الشفوي: ﴿تَرْمِيهِمْ بِحِجَارَةٍ﴾ → تَرْمِيهِمْـبِحِجَارَةٍ",
            parse_mode="Markdown"
        )

    if "مد طبيعي" in text:
        return await update.message.reply_text(
            "📏 *المد الطبيعي:*\n"
            "هو المد الأصلي الذي لا يتوقف على سبب.\n"
            "🧪 أمثلة:\n"
            "• ﴿قَالَ﴾\n"
            "• ﴿يَقُولُ﴾\n"
            "• ﴿فِيهِ﴾",
            parse_mode="Markdown"
        )

    if "مد لازم" in text:
        return await update.message.reply_text(
            "📏 *المد اللازم:*\n"
            "يمد 6 حركات إذا جاء بعد حرف المد حرف ساكن أصلي.\n"
            "🧪 أمثلة:\n"
            "• ﴿الضَّالِّينَ﴾\n"
            "• ﴿الصَّاخَّةُ﴾\n"
            "• ﴿الْحَاقَّةُ﴾",
            parse_mode="Markdown"
        )

    if "مد متصل" in text:
        return await update.message.reply_text(
            "📏 *المد المتصل:*\n"
            "يمد 4–5 حركات إذا جاء بعد حرف المد همزة في نفس الكلمة.\n"
            "🧪 أمثلة:\n"
            "• ﴿جَاءَ﴾\n"
            "• ﴿سُوءَ﴾\n"
            "• ﴿بَرِيءٌ﴾",
            parse_mode="Markdown"
        )

    if "مد منفصل" in text:
        return await update.message.reply_text(
            "📏 *المد المنفصل:*\n"
            "يمد 4–5 حركات إذا جاء حرف المد في آخر الكلمة والهمزة في أول الكلمة التالية.\n"
            "🧪 أمثلة:\n"
            "• ﴿يَا أَيُّهَا﴾\n"
            "• ﴿إِنَّا أَنْزَلْنَاهُ﴾",
            parse_mode="Markdown"
        )

    if "بسملة" in text:
        return await update.message.reply_text(
            "🌸 *البسملة:*\n"
            "﴿بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ﴾\n"
            "✅ تُقرأ في بداية كل سورة ما عدا التوبة.\n"
            "🧠 حكمها: مستحب عند بدء التلاوة، وواجبة في الفاتحة.\n"
            "📌 إذا بدأت من وسط السورة، يجوز البدء بها أو بدونها.",
            parse_mode="Markdown"
        )

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

