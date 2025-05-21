import os
import json
from pyrogram import Client, filters

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

bot = Client("forwarder", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

DATA_FILE = "channels.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"sources": [], "targets": []}, f)

def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply("Bot is running!\nUse /connect <source_channel>\n/addtarget <target_channel>\n/list")

@bot.on_message(filters.command("connect") & filters.private)
async def connect_source(client, message):
    data = load_data()
    try:
        source = message.text.split()[1]
        if source not in data["sources"]:
            data["sources"].append(source)
            save_data(data)
            await message.reply(f"Source {source} added!")
        else:
            await message.reply("Source already added.")
    except:
        await message.reply("Usage: /connect @sourcechannel")

@bot.on_message(filters.command("addtarget") & filters.private)
async def add_target(client, message):
    data = load_data()
    try:
        target = message.text.split()[1]
        if target not in data["targets"]:
            data["targets"].append(target)
            save_data(data)
            await message.reply(f"Target {target} added!")
        else:
            await message.reply("Target already added.")
    except:
        await message.reply("Usage: /addtarget @targetchannel")

@bot.on_message(filters.command("list") & filters.private)
async def list_all(client, message):
    data = load_data()
    sources = "\n".join(data["sources"]) or "No source yet"
    targets = "\n".join(data["targets"]) or "No target yet"
    await message.reply(f"**Sources:**\n{sources}\n\n**Targets:**\n{targets}")

@bot.on_message(filters.channel)
async def forward(client, message):
    data = load_data()
    chat_username = "@" + message.chat.username if message.chat.username else str(message.chat.id)
    if chat_username in data["sources"]:
        for target in data["targets"]:
            try:
                await message.forward(target)
            except Exception as e:
                print(f"Error forwarding to {target}: {e}")

print("Bot starting...")
bot.run()
