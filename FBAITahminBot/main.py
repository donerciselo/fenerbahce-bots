import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='+', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot {bot.user} olarak giriş yaptı!')
    await bot.load_extension("cogs.tahmin")
    print("Tahmin cog yüklendi.")

if __name__ == "__main__":
    bot.run(os.getenv("TAHMIN_TOKEN"))
