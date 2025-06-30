# quran.py
import os
import asyncio
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

# Health‐check endpoint
async def health(request):
    return web.Response(text="OK")

async def start_health_server():
    app = web.Application()
    app.add_routes([web.get("/", health)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

# Telegram handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *تقدمة السيد حيدر الموسوي*\n"
        "بسم الله الرحمن الرحيم، وبه نستعين.\n"
        "يسرنا أن نقدم لكم هذا البوت المبارك لتصفح صفحات القرآن الكريم.\n\n"
        "🌙 أرسل رقم الصفحة (1–620).",
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

def main():
    if not TOKEN:
        print("❌ TOKEN not set.")
        return

    # start health server
    asyncio.create_task(start_health_server())

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print(f"✅ Bot started — health on port {PORT}")
    app.run_polling()

if __name__ == "__main__":
    main()
