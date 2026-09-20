import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Bot is LIVE on Render!\n\n"
        "Your deployment worked!\n"
        "Send /status to check."
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🟢 Bot running on Render Free Tier\nPocket API will be added next.")

if not BOT_TOKEN:
    print("ERROR: TELEGRAM_BOT_TOKEN not set!")
else:
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    print("Bot starting...")
    app.run_polling()