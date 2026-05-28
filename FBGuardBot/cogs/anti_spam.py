import discord
from discord.ext import commands
import config
from collections import defaultdict
import datetime

class AntiSpam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_messages = defaultdict(list)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        now = datetime.datetime.utcnow()
        uid = message.author.id
        key = (message.guild.id, uid)
        self.user_messages[key].append(now)
        max_msgs = config.ANTI_SPAM.get("max_messages", 5)
        window = config.ANTI_SPAM.get("window", 3)

        self.user_messages[key] = [t for t in self.user_messages[key]
                                    if (now - t).total_seconds() < window]

        if len(self.user_messages[key]) >= max_msgs:
            punishment = config.ANTI_SPAM.get("punishment", "timeout")
            td = config.ANTI_SPAM.get("timeout_duration", 300)
            embed = discord.Embed(title="Anti-Spam: Spam Tespit Edildi",
                                  color=config.COLOR_WARNING,
                                  timestamp=now)
            embed.description = f"{message.author.mention} ({message.author.id}) spam yapıyor."
            embed.add_field(name="Mesaj Sayısı", value=f"{len(self.user_messages[key])} / {window}s")
            embed.add_field(name="Uygulanan", value=punishment)

            if punishment == "timeout":
                try:
                    await message.author.timeout(datetime.timedelta(seconds=td),
                                                  reason=f"Spam: {len(self.user_messages[key])} mesaj/{window}s")
                    embed.add_field(name="Süre", value=f"{td}s")
                except:
                    pass
            elif punishment == "kick":
                try:
                    await message.author.kick(reason="Spam")
                except:
                    pass
            elif punishment == "ban":
                try:
                    await message.author.ban(reason="Spam")
                except:
                    pass

            try:
                await message.delete()
            except:
                pass
            self.user_messages[key] = []

            log_ch = self._get_log_channel(message.guild)
            if log_ch:
                await log_ch.send(embed=embed)

    def _get_log_channel(self, guild):
        if config.LOG_CHANNEL_ID:
            ch = guild.get_channel(config.LOG_CHANNEL_ID)
            if ch: return ch
        for ch in guild.text_channels:
            if "log" in ch.name.lower():
                return ch
        return None

    @commands.hybrid_command(name="spam-ayar", description="Spam koruma ayarlarını gösterir")
    @commands.has_permissions(administrator=True)
    async def spam_ayar(self, ctx):
        embed = discord.Embed(title="Anti-Spam Ayarları", color=config.COLOR_NORMAL)
        embed.add_field(name="Eşik", value=f"{config.ANTI_SPAM.get('max_messages', 5)} mesaj / {config.ANTI_SPAM.get('window', 3)}s")
        embed.add_field(name="Ceza", value=config.ANTI_SPAM.get("punishment", "timeout"))
        embed.add_field(name="Timeout Süresi", value=f"{config.ANTI_SPAM.get('timeout_duration', 300)}s")
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(AntiSpam(bot))
