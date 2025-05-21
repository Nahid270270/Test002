import os
from pyrogram import Client
from flask import Flask, request

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
BASE_URL = os.environ.get("BASE_URL")  # example: https://yourapp.onrender.com

app = Flask(__name__)

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.route('/')
def index():
    return "Bot is Running!"

@app.route('/webhook', methods=["POST"])
def webhook():
    update = request.get_json()
    if update:
        bot.process_update(update)
    return "ok"

@app.before_first_request
def set_webhook():
    bot.set_webhook(f"{BASE_URL}/webhook")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
