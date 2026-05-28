import discord
from discord.ext import commands
import json

class Reaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot: return
        try:
            with open("reaction_roles.json", "r") as f:
                data = json.load(f)
        except:
            return

        msg_id = str(payload.message_id)
        if msg_id in data:
            emoji_name = payload.emoji.name
            if emoji_name in data[msg_id]:
                role_id = data[msg_id][emoji_name]
                guild = self.bot.get_guild(payload.guild_id)
                role = guild.get_role(role_id)
                if role:
                    await payload.member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        try:
            with open("reaction_roles.json", "r") as f:
                data = json.load(f)
        except:
            return

        msg_id = str(payload.message_id)
        if msg_id in data:
            emoji_name = payload.emoji.name
            if emoji_name in data[msg_id]:
                role_id = data[msg_id][emoji_name]
                guild = self.bot.get_guild(payload.guild_id)
                member = guild.get_member(payload.user_id)
                role = guild.get_role(role_id)
                if role and member:
                    await member.remove_roles(role)

async def setup(bot):
    await bot.add_cog(Reaction(bot))
