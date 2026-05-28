import discord
from discord.ext import commands
import config
from collections import defaultdict
import datetime

class AntiNuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_deletes = defaultdict(list)
        self.role_deletes = defaultdict(list)
        self.ban_kick_events = defaultdict(list)
        self.snapshot = {}

    def get_max(self, key, guild_id):
        return config.ANTI_NUKE.get(key, {}).get(guild_id, config.ANTI_NUKE.get(key, 3))

    def get_cooldown(self, guild_id):
        return config.ANTI_NUKE.get("cooldown", {}).get(guild_id, config.ANTI_NUKE.get("cooldown", 10))

    def _check_threshold(self, records, max_count, cooldown):
        now = datetime.datetime.utcnow()
        records[:] = [t for t in records if (now - t).total_seconds() < cooldown]
        return len(records) >= max_count

    def _get_log_channel(self, guild):
        if config.LOG_CHANNEL_ID:
            ch = guild.get_channel(config.LOG_CHANNEL_ID)
            if ch: return ch
        for ch in guild.text_channels:
            if "log" in ch.name.lower():
                return ch
        return None

    async def _log(self, guild, title, desc, color=config.COLOR_WARNING):
        embed = discord.Embed(title=title, description=desc, color=color, timestamp=datetime.datetime.utcnow())
        ch = self._get_log_channel(guild)
        if ch:
            await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        guild = channel.guild
        if not guild:
            return
        now = datetime.datetime.utcnow()
        self.channel_deletes[guild.id].append(now)
        max_del = self.get_max("max_channel_delete", guild.id)
        cd = self.get_cooldown(guild.id)
        if self._check_threshold(self.channel_deletes[guild.id], max_del, cd):
            await self._log(guild, "Anti-Nuke: Kanal Silme Saldırısı",
                           f"{channel.name} silindi. Eşik aşıldı ({max_del} kanal / {cd}s).")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        guild = role.guild
        if not guild:
            return
        now = datetime.datetime.utcnow()
        self.role_deletes[guild.id].append(now)
        max_del = self.get_max("max_role_delete", guild.id)
        cd = self.get_cooldown(guild.id)
        if self._check_threshold(self.role_deletes[guild.id], max_del, cd):
            await self._log(guild, "Anti-Nuke: Rol Silme Saldırısı",
                           f"{role.name} silindi. Eşik aşıldı ({max_del} rol / {cd}s).")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        now = datetime.datetime.utcnow()
        self.ban_kick_events[guild.id].append(now)
        max_bk = self.get_max("max_ban_kick", guild.id)
        cd = self.get_cooldown(guild.id)
        if self._check_threshold(self.ban_kick_events[guild.id], max_bk, cd):
            await self._log(guild, "Anti-Nuke: Ban/Kick Saldırısı",
                           f"{user} banlandı. Eşik aşıldı ({max_bk} işlem / {cd}s).")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild
        if guild.me.guild_permissions.view_audit_log:
            try:
                async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
                    if entry.target.id == member.id:
                        now = datetime.datetime.utcnow()
                        self.ban_kick_events[guild.id].append(now)
                        break
            except:
                pass

    @commands.hybrid_command(name="snapshot", description="Sunucu yapılandırmasının yedeğini alır")
    @commands.has_permissions(administrator=True)
    async def snapshot(self, ctx):
        guild = ctx.guild
        snap = {
            "channels": [(c.id, c.name, c.type, c.category_id) for c in guild.channels],
            "roles": [(r.id, r.name, r.permissions.value) for r in guild.roles],
            "settings": {"name": guild.name, "icon": str(guild.icon.url) if guild.icon else None}
        }
        self.snapshot[guild.id] = snap
        embed = discord.Embed(title="Snapshot Alındı", color=config.COLOR_NORMAL)
        embed.description = f"{len(snap['channels'])} kanal, {len(snap['roles'])} rol kaydedildi."
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(AntiNuke(bot))
