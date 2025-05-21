import os
import json
from flask import Flask, request
from pyrogram import Client, filters

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
BASE_URL = os.environ.get("BASE_URL")  # example: https://yourapp.onrender.com

app = Flask(__name__)
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

DATA_FILE = "channels.json"

# Ensure data file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"sources": [], "targets": []}, f)

def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Start Command
@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply("Bot is running!\nUse /connect <source_channel> to add source channel.\nUse /addtarget <target_channel> to add target channel.\nUse /list to see current channels.")

# Connect source channel
@bot.on_message(filters.command("connect") & filters.private)
async def connect_source(client, message):
    data = load_data()
    try:
        source = message.text.split()[1]
        if source not in data["sources"]:
            data["sources"].append(source)
            save_data(data)
            await message.reply(f"Source channel {source} added!")
        else:
            await message.reply("Source channel already added.")
    except:
        await message.reply("Usage: /connect <source_channel>")

# Add target channel
@bot.on_message(filters.command("addtarget") & filters.private)
async def add_target(client, message):
    data = load_data()
    try:
        target = message.text.split()[1]
        if target not in data["targets"]:
            data["targets"].append(target)
            save_data(data)
            await message.reply(f"Target channel {target} added!")
        else:
            await message.reply("Target channel already added.")
    except:
        await message.reply("Usage: /addtarget <target_channel>")

# List channels
@bot.on_message(filters.command("list") & filters.private)
async def list_channels(client, message):
    data = load_data()
    text = f"Sources:\n" + "\n".join(data["sources"]) + "\n\nTargets:\n" + "\n".join(data["targets"])
    await message.reply(text)

# Forward messages from sources to targets
@bot.on_message(filters.channel)
async def forward_messages(client, message):
    data = load_data()
    chat_username = "@" + message.chat.username if message.chat.username else str(message.chat.id)
    if chat_username in data["sources"]:
        for target in data["targets"]:
            try:
                await message.forward(target)
            except Exception as e:
                print(f"Failed to forward to {target}: {e}")

# Flask routes
@app.route("/", methods=["GET"])
def index():
    return "Bot is running!"

@app.route("/bot", methods=["POST"])
def webhook():
    update = request.get_json()
    bot.process_new_updates([update])
    return "ok"

if __name__ == "__main__":
    bot.start()
    bot.set_webhook(f"{BASE_URL}/bot")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
