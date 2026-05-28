import discord
from discord.ext import commands
import config

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ban")
    @commands.has_any_role(*config.MOD_ROLE_NAMES)
    async def ban_user(self, ctx, member: discord.Member, *, reason="Sebep belirtilmedi."):
        await member.ban(reason=reason)
        await ctx.send(f"{member.mention} sunucudan banlandı! Sebep: {reason}")

    @commands.command(name="kick")
    @commands.has_any_role(*config.MOD_ROLE_NAMES)
    async def kick_user(self, ctx, member: discord.Member, *, reason="Sebep belirtilmedi."):
        await member.kick(reason=reason)
        await ctx.send(f"{member.mention} sunucudan atıldı! Sebep: {reason}")

    @commands.command(name="sil")
    @commands.has_any_role(*config.MOD_ROLE_NAMES)
    async def clear_messages(self, ctx, amount: int = 10):
        await ctx.channel.purge(limit=amount + 1)
        msg = await ctx.send(f"🧹 {amount} mesaj silindi.")
        await msg.delete(delay=3)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
