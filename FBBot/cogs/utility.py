import discord
from discord.ext import commands
import config

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        await ctx.send(f"🏓 Pong! Gecikme: {round(self.bot.latency * 1000)}ms")

    @commands.command(name="avatar")
    async def avatar(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(title=f"{member.name} Avatarı", color=config.NAVY)
        embed.set_image(url=member.display_avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
