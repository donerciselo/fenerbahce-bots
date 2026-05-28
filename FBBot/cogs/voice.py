import discord
from discord.ext import commands
import config

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tasi")
    @commands.has_any_role(*config.MOD_ROLE_NAMES)
    async def move_all(self, ctx, channel: discord.VoiceChannel):
        if not ctx.author.voice:
            await ctx.send("Önce bir ses kanalında olmalısınız.")
            return
            
        moved = 0
        for member in ctx.author.voice.channel.members:
            try:
                await member.move_to(channel)
                moved += 1
            except discord.Forbidden:
                pass
                
        await ctx.send(f"✅ {moved} kullanıcı {channel.mention} kanalına taşındı.")

async def setup(bot):
    await bot.add_cog(Voice(bot))
