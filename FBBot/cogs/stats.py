import discord
from discord.ext import commands, tasks
import config

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_stats.start()

    def cog_unload(self):
        self.update_stats.cancel()

    @tasks.loop(minutes=10)
    async def update_stats(self):
        if hasattr(config, 'STATS_CHANNEL_ID'):
            channel = self.bot.get_channel(config.STATS_CHANNEL_ID)
            if channel and isinstance(channel, discord.VoiceChannel):
                try:
                    await channel.edit(name=f"👥 Aktif Üye • {channel.guild.member_count}")
                except Exception:
                    pass

    @update_stats.before_loop
    async def before_update_stats(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Stats(bot))
