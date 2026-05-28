import discord
from discord.ext import commands
import config
import asyncio
import random

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="cekilis")
    @commands.has_any_role(*config.MOD_ROLE_NAMES)
    async def start_giveaway(self, ctx, sure: int, *, odul: str):
        embed = discord.Embed(title="🎉 Çekiliş Başladı!", description=f"Ödül: **{odul}**\nKatılmak için 🎉 emojisine tıklayın!\nSüre: {sure} saniye", color=config.GOLD)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🎉")
        
        await asyncio.sleep(sure)
        
        new_msg = await ctx.channel.fetch_message(msg.id)
        users = [user async for user in new_msg.reactions[0].users() if not user.bot]
        
        if len(users) == 0:
            await ctx.send("Katılımcı olmadığı için çekiliş iptal edildi.")
            return
            
        winner = random.choice(users)
        await ctx.send(f"Tebrikler {winner.mention}! **{odul}** kazandın! 🎉")

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
