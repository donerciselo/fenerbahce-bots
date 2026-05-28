import discord
from discord.ext import commands
import config
import threading
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=config.PREFIX, intents=intents)

def _start_flask():
    try:
        from app import app
        host = "0.0.0.0"
        port = int(os.getenv("PORT", "5000"))
        app.run(host=host, port=port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"[-] Flask: {e}")

async def load_cogs():
    import os
    for file in os.listdir("cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            try:
                await bot.load_extension(f"cogs.{file[:-3]}")
                print(f"[+] {file}")
            except Exception as e:
                print(f"[-] {file}: {e}")

@bot.event
async def on_ready():
    print(f"{bot.user} ready — {len(bot.guilds)} guilds")

@bot.event
async def setup_hook():
    await load_cogs()

@bot.event
async def on_command_error(ctx, error):
    embed = discord.Embed(title="Hata", color=config.COLOR_CRITICAL)
    embed.description = str(error)
    try:
        await ctx.reply(embed=embed, delete_after=5)
    except:
        pass

if __name__ == "__main__":
    t = threading.Thread(target=_start_flask, daemon=True)
    t.start()
    print("[+] Flask baslatildi (background thread)")
    bot.run(config.TOKEN)
