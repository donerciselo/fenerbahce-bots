import discord
from discord.ext import commands
import config
import datetime
import json

class AutoRecovery(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.backups = {}

    @commands.hybrid_command(name="backup", description="Sunucu yedekleme alır")
    @commands.has_permissions(administrator=True)
    async def backup(self, ctx):
        guild = ctx.guild
        try:
            data = {
                "name": guild.name,
                "icon": str(guild.icon.url) if guild.icon else None,
                "categories": [],
                "channels": [],
                "roles": []
            }
            for cat in guild.categories:
                data["categories"].append({
                    "id": cat.id, "name": cat.name,
                    "position": cat.position,
                    "permissions": [{"id": o.id, "allow": str(p.allow), "deny": str(p.deny)}
                                    for o, p in cat.overwrites.items()]
                })
            for ch in guild.channels:
                if isinstance(ch, discord.CategoryChannel):
                    continue
                data["channels"].append({
                    "id": ch.id, "name": ch.name, "type": str(ch.type),
                    "category_id": ch.category_id,
                    "topic": ch.topic if hasattr(ch, 'topic') else None,
                    "position": ch.position
                })
            for role in guild.roles:
                if role.is_default() or role.managed:
                    continue
                data["roles"].append({
                    "id": role.id, "name": role.name,
                    "color": str(role.color), "hoist": role.hoist,
                    "position": role.position,
                    "permissions": role.permissions.value,
                    "mentionable": role.mentionable
                })
            self.backups[guild.id] = data
            embed = discord.Embed(title="Yedekleme Alındı", color=config.COLOR_NORMAL,
                                  timestamp=datetime.datetime.utcnow())
            embed.description = f"{len(data['categories'])} kategori, {len(data['channels'])} kanal, {len(data['roles'])} rol"
            await ctx.reply(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="Hata", color=config.COLOR_CRITICAL)
            embed.description = str(e)
            await ctx.reply(embed=embed)

    @commands.hybrid_command(name="restore", description="Sunucuyu yedekten geri yükler")
    @commands.has_permissions(administrator=True)
    async def restore(self, ctx):
        guild = ctx.guild
        data = self.backups.get(guild.id)
        if not data:
            embed = discord.Embed(title="Hata", color=config.COLOR_CRITICAL)
            embed.description = "Önce `+backup` ile yedekleme alın."
            await ctx.reply(embed=embed)
            return
        try:
            embed = discord.Embed(title="Geri Yükleme Başladı", color=config.COLOR_WARNING)
            embed.description = "Roller ve kanallar oluşturuluyor..."
            await ctx.reply(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="Hata", color=config.COLOR_CRITICAL)
            embed.description = str(e)
            await ctx.reply(embed=embed)

    @commands.hybrid_command(name="recover", description="Silinen kanal/rolü kurtarmayı dener")
    @commands.has_permissions(administrator=True)
    async def recover(self, ctx, hedef: str = None):
        if not hedef:
            embed = discord.Embed(title="Kullanım", color=config.COLOR_WARNING)
            embed.description = "`+recover <kanal_ismi veya rol_ismi>`"
            await ctx.reply(embed=embed)
            return
        embed = discord.Embed(title="Kurtarma", color=config.COLOR_NORMAL)
        embed.description = f"`{hedef}` kurtarılamadı. Lütfen `+backup` ile yedek almayı deneyin."
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(AutoRecovery(bot))
