import discord
from discord.ext import tasks
from discord import app_commands
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
GUILD_ID = int(os.getenv("GUILD_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

notified_5min = False
notified_spawn = False

BASE_SPAWN = datetime.now().replace(hour=1, minute=30, second=0, microsecond=0)

def get_next_spawn():
    now = datetime.now()
    spawn = BASE_SPAWN
    while spawn <= now:
        spawn += timedelta(hours=2)
    return spawn

@tree.command(name="boss", description="Час до боса", guild=discord.Object(id=GUILD_ID))
async def boss(interaction: discord.Interaction):
    next_spawn = get_next_spawn()
    unix_time = int(next_spawn.timestamp())
    
    await interaction.response.send_message(
        f"⏳ До боса: <t:{unix_time}:R>\n"
        f"🕒 Спавн о: <t:{unix_time}:t>"
    )

@client.event
async def on_ready():
    print(f"Запущений як {client.user}")
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    check_boss.start()

@tasks.loop(seconds=30)
async def check_boss():
    global notified_5min, notified_spawn

    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("Канал не знайдено!")
        return

    now = datetime.now()
    next_spawn = get_next_spawn()
    diff = (next_spawn - now).total_seconds()

    if 270 <= diff <= 330 and not notified_5min:
        await channel.send("⚠️ Босс через 5 мин! @everyone")
        notified_5min = True

    if diff <= 30 and not notified_spawn:
        await channel.send("⚔️ Спавн Босса! @everyone")
        notified_spawn = True

    if diff > 60:
        notified_5min = False
        notified_spawn = False

client.run(TOKEN)