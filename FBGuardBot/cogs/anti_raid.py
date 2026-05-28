import discord
from discord.ext import commands
import config
from collections import defaultdict, deque
import datetime

class AntiRaid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.join_times = defaultdict(deque)
        self.raid_mode = {}

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        now = datetime.datetime.utcnow()
        self.join_times[guild.id].append(now)
        threshold = config.ANTI_RAID.get("join_threshold", 5)
        window = config.ANTI_RAID.get("join_window", 10)
        punishment = config.ANTI_RAID.get("punishment", "kick")

        while self.join_times[guild.id] and (now - self.join_times[guild.id][0]).total_seconds() > window:
            self.join_times[guild.id].popleft()

        if len(self.join_times[guild.id]) >= threshold:
            embed = discord.Embed(title="Anti-Raid: Toplu Katılım Tespit Edildi",
                                  color=config.COLOR_CRITICAL,
                                  timestamp=now)
            embed.description = f"{len(self.join_times[guild.id])} katılım / {window}s (eşik: {threshold})"
            embed.add_field(name="Son Katılan", value=member.mention, inline=False)
            embed.add_field(name="Uygulanan", value=punishment, inline=True)

            log_ch = self._get_log_channel(guild)
            if log_ch:
                await log_ch.send(embed=embed)

            if punishment == "kick":
                try:
                    await member.kick(reason="Anti-Raid: Toplu katılım")
                except:
                    pass
            elif punishment == "ban":
                try:
                    await member.ban(reason="Anti-Raid: Toplu katılım")
                except:
                    pass

    def _get_log_channel(self, guild):
        if config.LOG_CHANNEL_ID:
            ch = guild.get_channel(config.LOG_CHANNEL_ID)
            if ch: return ch
        for ch in guild.text_channels:
            if "log" in ch.name.lower():
                return ch
        return None

    @commands.hybrid_command(name="raidmode", description="Raid modunu açar/kapatır")
    @commands.has_permissions(administrator=True)
    async def raidmode(self, ctx, durum: str = None):
        gid = ctx.guild.id
        if durum and durum.lower() in ("on", "aç", "true"):
            self.raid_mode[gid] = True
            self.join_times[gid].clear()
            embed = discord.Embed(title="Raid Modu Açıldı", color=config.COLOR_WARNING)
            embed.description = "Yeni katılımlar yakından izleniyor."
            await ctx.reply(embed=embed)
        elif durum and durum.lower() in ("off", "kapat", "false"):
            self.raid_mode[gid] = False
            self.join_times[gid].clear()
            embed = discord.Embed(title="Raid Modu Kapatıldı", color=config.COLOR_NORMAL)
            await ctx.reply(embed=embed)
        else:
            durum_text = "Aktif" if self.raid_mode.get(gid) else "Pasif"
            embed = discord.Embed(title="Raid Modu", color=config.COLOR_WARNING)
            embed.add_field(name="Durum", value=durum_text)
            embed.add_field(name="Eşik", value=f"{config.ANTI_RAID.get('join_threshold', 5)} katılım / {config.ANTI_RAID.get('join_window', 10)}s")
            await ctx.reply(embed=embed)

    @raidmode.error
    async def raidmode_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title="Yetki Yok", color=config.COLOR_CRITICAL)
            embed.description = "Bu komutu kullanmak için **Yönetici** yetkisi gerekli."
            await ctx.reply(embed=embed, delete_after=5)

async def setup(bot):
    await bot.add_cog(AntiRaid(bot))
