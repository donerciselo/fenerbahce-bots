import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("KADRO_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="+", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"{bot.user} olarak giriş yapıldı")
    print(f"{len(bot.guilds)} sunucuda aktif")
    await bot.load_extension("cogs.kadro_cog")
    print("Kadro cog yüklendi")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Eksik parametre girdiniz.")
        return
    raise error

bot.run(TOKEN)