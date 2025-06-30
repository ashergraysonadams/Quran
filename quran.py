from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os

# 🔐 جلب التوكن من متغير البيئة
TOKEN = os.environ.get("TOKEN")

# 📁 مسار مجلد الصور
QURAN_PAGES_DIR = os.path.join(os.path.dirname(__file__), 'pages')

# 🟢 دالة بدء المحادثة
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *تقدمة السيد حيدر الموسوي*\n"
        "بسم الله الرحمن الرحيم، وبه نستعين.\n"
        "يسرنا أن نقدم لكم هذا البوت المبارك الذي يتيح لكم تصفح صفحات القرآن الكريم بكل سهولة ويسر.\n\n"
        "🌙 أرسل رقم الصفحة (من 1 إلى 620) وسأرسل لك صورة الصفحة مباشرة.",
        parse_mode='Markdown'
    )

# 📤 دالة استقبال الرسائل والرد على المستخدم
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.strip().lower()

    # ✅ رد السلام
    if "السلام عليكم" in message and "ورحمة الله" in message:
        await update.message.reply_text("وعليكم السلام ورحمة الله")
        return

    # ✅ رد الصلوات
    if "صلوات" in message and "محمد" in message and "آل" in message:
        await update.message.reply_text("اللهم صَلِّ عَلَى مُحَمَّدٍ وَآلِ مُحَمَّدٍ")
        return

    # ✅ إرسال صورة الصفحة
    if message.isdigit():
        page_number = int(message)
        if 1 <= page_number <= 620:
            file_path = os.path.join(QURAN_PAGES_DIR, f"{page_number}.jpg")
            if os.path.exists(file_path):
                with open(file_path, 'rb') as photo:
                    await update.message.reply_photo(photo=photo)
        return  # لا ترد إذا الرقم خارج النطاق

    # ❌ تجاهل أي رسالة أخرى
    return

# 🚀 تشغيل البوت
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ البوت يعمل الآن... انتظر الرسائل من تيليغرام.")
    app.run_polling()

if __name__ == '__main__':
    main()