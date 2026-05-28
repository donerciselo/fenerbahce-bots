import discord
from discord.ext import commands
import config

class Transfer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="transfer")
    @commands.has_any_role(*config.MOD_ROLE_NAMES)
    async def announce_transfer(self, ctx, oyuncu: str, mevki: str):
        embed = discord.Embed(title="✈️ YENİ TRANSFER!", description=f"Fenerbahçemize Hoş Geldin **{oyuncu}**!", color=config.NAVY)
        embed.add_field(name="Mevki", value=mevki)
        embed.set_image(url="https://upload.wikimedia.org/wikipedia/tr/8/86/Fenerbah%C3%A7e_SK.png")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Transfer(bot))
