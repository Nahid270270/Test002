import os
import json
import re
import requests
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

DATA_FILE = "channels.json"

# Init JSON
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"sources": [], "targets": [], "shortener": ""}, f)

def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def shorten_links(text):
    data = load_data()
    short_api = data.get("shortener", "")
    urls = re.findall(r'(https?://\S+)', text)
    for url in urls:
        if short_api and "{{link}}" in short_api:
            try:
                api_url = short_api.replace("{{link}}", url)
                r = requests.get(api_url)
                short_url = r.json().get("shortenedUrl") or r.json().get("short") or url
                text = text.replace(url, short_url)
            except:
                continue
    return text

app = Client("autoforward_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Connect source
@app.on_message(filters.command("connect") & filters.private)
def connect_channel(client, message: Message):
    data = load_data()
    if len(message.command) < 2:
        return message.reply("Usage: /connect <channel_username or ID>")
    channel = message.command[1]
    if channel not in data["sources"]:
        data["sources"].append(channel)
        save_data(data)
        message.reply(f"✅ Connected to source: `{channel}`")
    else:
        message.reply("Already connected.")

# Disconnect
@app.on_message(filters.command("disconnect") & filters.private)
def disconnect_channel(client, message: Message):
    data = load_data()
    if len(message.command) < 2:
        return message.reply("Usage: /disconnect <channel_username or ID>")
    channel = message.command[1]
    if channel in data["sources"]:
        data["sources"].remove(channel)
        save_data(data)
        message.reply(f"❌ Disconnected from: `{channel}`")
    else:
        message.reply("Not found.")

# Add target
@app.on_message(filters.command("addtarget") & filters.private)
def add_target(client, message: Message):
    data = load_data()
    if len(message.command) < 2:
        return message.reply("Usage: /addtarget <channel_username or ID>")
    channel = message.command[1]
    if channel not in data["targets"]:
        data["targets"].append(channel)
        save_data(data)
        message.reply(f"✅ Added target: `{channel}`")
    else:
        message.reply("Already added.")

# Remove target
@app.on_message(filters.command("removetarget") & filters.private)
def remove_target(client, message: Message):
    data = load_data()
    if len(message.command) < 2:
        return message.reply("Usage: /removetarget <channel_username or ID>")
    channel = message.command[1]
    if channel in data["targets"]:
        data["targets"].remove(channel)
        save_data(data)
        message.reply(f"❌ Removed target: `{channel}`")
    else:
        message.reply("Not found.")

# List channels
@app.on_message(filters.command("list") & filters.private)
def list_channels(client, message: Message):
    data = load_data()
    text = "**✅ Connected Source Channels:**\n"
    text += "\n".join([f"• `{src}`" for src in data["sources"]]) or "None"
    text += "\n\n**📤 Target Channels:**\n"
    text += "\n".join([f"• `{tgt}`" for tgt in data["targets"]]) or "None"
    message.reply(text)

# Set shortener
@app.on_message(filters.command("setshortener") & filters.private)
def set_shortener(client, message: Message):
    if len(message.command) < 2:
        return message.reply("Usage:\n/setshortener <api_url_with_{{link}}>")
    short_url = message.command[1]
    if "{{link}}" not in short_url:
        return message.reply("Error: must include `{{link}}`")
    data = load_data()
    data["shortener"] = short_url
    save_data(data)
    message.reply("✅ Shortener API set successfully.")

# Show shortener
@app.on_message(filters.command("shortener") & filters.private)
def show_shortener(client, message: Message):
    data = load_data()
    short_api = data.get("shortener", "")
    if short_api:
        message.reply(f"Current Shortener:\n`{short_api}`")
    else:
        message.reply("No shortener set yet.")

# Forward handler
@app.on_message(filters.channel)
def auto_forward(client, message: Message):
    data = load_data()
    src_id = str(message.chat.id)
    src_uname = message.chat.username
    if src_id in data["sources"] or src_uname in data["sources"]:
        text = message.text or message.caption or ""
        text = shorten_links(text)
        for tgt in data["targets"]:
            try:
                if message.text:
                    client.send_message(tgt, text)
                elif message.caption and message.media:
                    client.copy_message(tgt, message.chat.id, message.id, caption=text)
                else:
                    client.copy_message(tgt, message.chat.id, message.id)
            except Exception as e:
                print(f"Error to {tgt}: {e}")

app.run()
