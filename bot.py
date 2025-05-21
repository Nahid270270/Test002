import os
import json
from flask import Flask, request
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
BASE_URL = os.environ.get("BASE_URL")  # example: https://yourapp.onrender.com

app = Flask(__name__)

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Data persistence
DATA_FILE = "channels.json"
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"sources": [], "targets": [], "shortener": None}, f)

def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Bot Commands
@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply("Bot is running and ready to auto-forward!")

@bot.on_message(filters.command("connect") & filters.private)
async def connect_source(client, message):
    data = load_data()
    try:
        source = message.text.split()[1]
        if source not in data["sources"]:
            data["sources"].append(source)
            save_data(data)
            await message.reply(f"Connected to source: {source}")
        else:
            await message.reply("Already connected to this source.")
    except:
        await message.reply("Usage: /connect <source_channel>")

@bot.on_message(filters.command("addtarget") & filters.private)
async def add_target(client, message):
    data = load_data()
    try:
        target = message.text.split()[1]
        if target not in data["targets"]:
            data["targets"].append(target)
            save_data(data)
            await message.reply(f"Target added: {target}")
        else:
            await message.reply("Target already exists.")
    except:
        await message.reply("Usage: /addtarget <target_channel>")

@bot.on_message(filters.command("setshortener") & filters.private)
async def set_shortener(client, message):
    data = load_data()
    try:
        short_api = message.text.split(None, 1)[1]
        data["shortener"] = short_api
        save_data(data)
        await message.reply("Shortener API set successfully.")
    except:
        await message.reply("Usage: /setshortener <api_url_with_{{link}}>")

@bot.on_message(filters.command("list") & filters.private)
async def list_all(client, message):
    data = load_data()
    txt = f"Sources: {data['sources']}\nTargets: {data['targets']}\nShortener: {data['shortener']}"
    await message.reply(txt)

# Main auto-forwarder
@bot.on_message(filters.channel)
async def forwarder(client, message: Message):
    data = load_data()
    source_id = str(message.chat.username or message.chat.id)
    if source_id not in data["sources"]:
        return

    text = message.text or message.caption or ""
    shortener = data.get("shortener")
    if shortener:
        words = text.split()
        new_words = []
        for word in words:
            if word.startswith("http"):
                short = shortener.replace("{{link}}", word)
                new_words.append(short)
            else:
                new_words.append(word)
        text = " ".join(new_words)

    for target in data["targets"]:
        try:
            if message.text:
                await client.send_message(target, text)
            elif message.photo:
                await client.send_photo(target, photo=message.photo.file_id, caption=text)
            elif message.video:
                await client.send_video(target, video=message.video.file_id, caption=text)
            else:
                await message.forward(target)
        except Exception as e:
            print(f"Error forwarding to {target}: {e}")

# Flask route for webhook
@app.route("/bot", methods=["POST"])
def webhook():
    update = request.get_json()
    bot.process_new_updates([update])
    return "ok"

@app.route("/")
def index():
    return "Bot is Live."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# Start bot client
bot.start()
bot.set_webhook(f"{BASE_URL}/bot")
