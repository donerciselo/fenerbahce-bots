import discord
from discord.ext import commands
import config
import datetime

class PermissionGuard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.role_snapshot = {}

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        guild = after.guild
        if before.permissions == after.permissions:
            return
        if not guild.me.guild_permissions.view_audit_log:
            return
        try:
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.role_update):
                if entry.target.id == after.id:
                    changer = entry.user
                    added = after.permissions.value & ~before.permissions.value
                    removed = before.permissions.value & ~after.permissions.value
                    if added or removed:
                        embed = discord.Embed(title="Permission Guard: Yetki Değişikliği",
                                              color=config.COLOR_CRITICAL,
                                              timestamp=datetime.datetime.utcnow())
                        embed.add_field(name="Rol", value=after.mention)
                        embed.add_field(name="Değiştiren", value=changer.mention if changer else "Bilinmiyor")
                        if added:
                            perms = [p for p, v in discord.Permissions(added) if v]
                            embed.add_field(name="Eklenen Yetkiler", value=", ".join(perms) or "Yok", inline=False)
                        if removed:
                            perms = [p for p, v in discord.Permissions(removed) if v]
                            embed.add_field(name="Kaldırılan Yetkiler", value=", ".join(perms) or "Yok", inline=False)
                        log_ch = self._get_log_channel(guild)
                        if log_ch and changer and changer.id != guild.me.id:
                            await log_ch.send(embed=embed)
                    break
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

    @commands.hybrid_command(name="yetki-tara", description="Tüm rollerin yetkilerini tarar")
    @commands.has_permissions(administrator=True)
    async def yetki_tara(self, ctx):
        embed = discord.Embed(title="Yetki Taraması", color=config.COLOR_WARNING)
        dangerous = []
        for role in ctx.guild.roles:
            if role.permissions.administrator or role.permissions.ban_members or role.permissions.kick_members or role.permissions.manage_guild:
                if not role.managed:
                    dangerous.append(f"{role.mention} - {len(role.members)} üye")
        if dangerous:
            embed.description = "Tehlikeli yetkilere sahip roller:"
            for r in dangerous[:20]:
                embed.add_field(name="⚠️", value=r, inline=False)
        else:
            embed.description = "Tehlikeli yetkiye sahip rol bulunamadı."
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(PermissionGuard(bot))
