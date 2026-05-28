import discord
from discord.ext import commands
import random
import config

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="zar")
    async def roll_dice(self, ctx):
        result = random.randint(1, 6)
        await ctx.send(f"🎲 Zar atıldı: **{result}**")

    @commands.command(name="fener")
    async def fenerbahce(self, ctx):
        await ctx.send("💛💙 En büyük FENERBAHÇE!")

async def setup(bot):
    await bot.add_cog(Fun(bot))
