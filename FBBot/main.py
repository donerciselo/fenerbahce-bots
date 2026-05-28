import discord
from discord.ext import commands, tasks
import config
import os
import json

intents = discord.Intents.all()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=config.PREFIX, intents=intents)

async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'Loaded cog: {filename[:-3]}')
            except Exception as e:
                print(f'Failed to load cog {filename[:-3]}: {e}')

@bot.event
async def setup_hook():
    await load_cogs()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title="Hata", description="Bu komutu kullanmak için gerekli yetkilere sahip değilsiniz.", color=config.NAVY)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRole):
        embed = discord.Embed(title="Yetki Hatası", description=f"Bu komutu kullanabilmek için **{error.missing_role}** rolüne sahip olmalısınız!", color=config.NAVY)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title="Hata", description="Eksik argüman. Lütfen tüm gerekli argümanları sağlayın.", color=config.NAVY)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.CommandNotFound):
        pass # Ignore command not found errors
    else:
        embed = discord.Embed(title="Hata", description=f"Bir hata oluştu: {error}", color=config.NAVY)
        await ctx.send(embed=embed)

bot.run(config.TOKEN)
