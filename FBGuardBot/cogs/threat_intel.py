import discord
from discord.ext import commands
import config
import aiohttp
import datetime

class ThreatIntel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.threat_db = {}
        self.known_bot_ids = set()
        self.session = None

    async def get_session(self):
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def cog_unload(self):
        if self.session and not self.session.closed:
            await self.session.close()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        if member.bot:
            flags = []
            if member.public_flags.verified_bot:
                flags.append("Doğrulanmış Bot")
            if member.id in self.known_bot_ids:
                flags.append("Bilinen Güvenli")
            if flags:
                embed = discord.Embed(title="Threat Intel: Bot Katıldı",
                                      color=config.COLOR_NORMAL,
                                      timestamp=datetime.datetime.utcnow())
                embed.add_field(name="Bot", value=member.mention)
                embed.add_field(name="ID", value=f"`{member.id}`")
                embed.add_field(name="Durum", value=", ".join(flags))
            else:
                embed = discord.Embed(title="Threat Intel: Bilinmeyen Bot Katıldı",
                                      color=config.COLOR_WARNING,
                                      timestamp=datetime.datetime.utcnow())
                embed.add_field(name="Bot", value=member.mention)
                embed.add_field(name="ID", value=f"`{member.id}`")
                embed.add_field(name="Öneri", value="Bot güvenilir değilse `+bot-kick @bot` ile atın.")
            log_ch = self._get_log_channel(guild)
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

    @commands.hybrid_command(name="bot-tara", description="Sunucudaki tüm botları tarar")
    @commands.has_permissions(administrator=True)
    async def bot_tara(self, ctx):
        bots = [m for m in ctx.guild.members if m.bot]
        if not bots:
            embed = discord.Embed(title="Bot Taraması", color=config.COLOR_NORMAL)
            embed.description = "Sunucuda bot bulunamadı."
            await ctx.reply(embed=embed)
            return
        embed = discord.Embed(title=f"Bot Taraması ({len(bots)})", color=config.COLOR_WARNING)
        unknown = []
        for bot in bots[:25]:
            tag = "✅ Doğrulanmış" if bot.public_flags.verified_bot else "❌ Doğrulanmamış"
            inviter = "Bilinmiyor"
            if bot.id in self.known_bot_ids:
                tag += " | Bilinen"
            embed.add_field(name=bot.name, value=f"ID: `{bot.id}`\nDurum: {tag}", inline=False)
            if not bot.public_flags.verified_bot and bot.id not in self.known_bot_ids:
                unknown.append(bot.id)
        if len(bots) > 25:
            embed.set_footer(text=f"+{len(bots)-25} bot daha")
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="bot-safe", description="Botu güvenli listesine ekler")
    @commands.has_permissions(administrator=True)
    async def bot_safe(self, ctx, bot: discord.Member):
        self.known_bot_ids.add(bot.id)
        embed = discord.Embed(title="Bot Güvenli Listeye Eklendi", color=config.COLOR_NORMAL)
        embed.description = f"{bot.mention} güvenli listesine eklendi."
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="bot-kick", description="Botu sunucudan atar")
    @commands.has_permissions(kick_members=True)
    async def bot_kick(self, ctx, bot: discord.Member):
        if not bot.bot:
            embed = discord.Embed(title="Hata", color=config.COLOR_CRITICAL)
            embed.description = "Bu komut sadece botlar için."
            await ctx.reply(embed=embed)
            return
        try:
            await bot.kick(reason=f"{ctx.author} tarafından atıldı")
            embed = discord.Embed(title="Bot Atıldı", color=config.COLOR_NORMAL)
            embed.description = f"{bot.mention} (`{bot.id}`) sunucudan atıldı."
            await ctx.reply(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="Hata", color=config.COLOR_CRITICAL)
            embed.description = str(e)
            await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(ThreatIntel(bot))
