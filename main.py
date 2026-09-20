import os
import logging
import threading
from http.server import HTTPServer, BaseHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PORT = int(os.environ.get("PORT", 10000))

# Dummy web server for Render
class Handler(BaseHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_web():
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    server.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is LIVE on Render!\nSend /status")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🟢 Running!")

if not BOT_TOKEN:
    print("ERROR: TELEGRAM_BOT_TOKEN not set in Environment!")
else:
    # Start web server in background
    threading.Thread(target=run_web, daemon=True).start()
    print(f"Web server on {PORT}")
    print("Bot starting...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.run_polling()