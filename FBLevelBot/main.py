import discord
from discord.ext import commands
import config
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=config.PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f"Level Bot {bot.user} olarak giriş yaptı!")

async def main():
    async with bot:
        if not os.path.exists("cogs"):
            os.makedirs("cogs")
        await bot.load_extension("cogs.leveling")
        await bot.start(config.TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
