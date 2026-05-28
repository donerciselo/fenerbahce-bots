import discord
from discord.ext import commands
import config
import json

class Protection(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        
        # Check for link protection
        try:
            with open("protection_config.json", "r") as f:
                data = json.load(f)
                if not data.get("anti_link", False):
                    return
        except:
            return
            
        if "http://" in message.content or "https://" in message.content:
            is_mod = False
            for role_name in getattr(config, 'MOD_ROLE_NAMES', []):
                role = discord.utils.get(message.guild.roles, name=role_name)
                if role in message.author.roles:
                    is_mod = True
                    break
            
            if not is_mod:
                await message.delete()
                await message.channel.send(f"{message.author.mention}, bu sunucuda link paylaşmak yasaktır!", delete_after=3)

async def setup(bot):
    await bot.add_cog(Protection(bot))
