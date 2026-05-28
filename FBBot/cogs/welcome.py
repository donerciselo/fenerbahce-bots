import discord
from discord.ext import commands
import config
import json

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel_id = getattr(config, 'WELCOME_CHANNEL_ID', None)
        if not channel_id: return
        channel = self.bot.get_channel(channel_id)
        if not channel: return
        
        try:
            with open('welcome_config.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                msg = data.get('message', "Hoş geldin!")
        except:
            msg = "Fenerbahçe dünyasına hoş geldin!"

        embed = discord.Embed(title="💛💙 Aramıza Yeni Bir Renkdaş Katıldı!", description=f"{member.mention} {msg}", color=config.GOLD)
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

        auto_role_name = getattr(config, 'AUTO_ROLE_NAME', None)
        if auto_role_name:
            role = discord.utils.get(member.guild.roles, name=auto_role_name)
            if role:
                await member.add_roles(role)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
