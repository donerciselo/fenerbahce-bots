import discord
from discord.ext import commands
import config
import datetime

class WebhookGuard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.known_webhooks = {}

    @commands.Cog.listener()
    async def on_webhooks_update(self, channel):
        guild = channel.guild
        try:
            webhooks = await channel.webhooks()
            for wh in webhooks:
                if wh.id not in self.known_webhooks.get(guild.id, set()):
                    embed = discord.Embed(title="Webhook Guard: Yeni Webhook Oluşturuldu",
                                          color=config.COLOR_WARNING,
                                          timestamp=datetime.datetime.utcnow())
                    embed.add_field(name="Kanal", value=channel.mention)
                    embed.add_field(name="Webhook", value=wh.name)
                    log_ch = self._get_log_channel(guild)
                    if log_ch:
                        await log_ch.send(embed=embed)
                    if guild.id not in self.known_webhooks:
                        self.known_webhooks[guild.id] = set()
                    self.known_webhooks[guild.id].add(wh.id)
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

    @commands.hybrid_command(name="webhook-list", description="Sunucudaki tüm webhook'ları listeler")
    @commands.has_permissions(manage_webhooks=True)
    async def webhook_list(self, ctx):
        try:
            webhooks = await ctx.guild.webhooks()
            if not webhooks:
                embed = discord.Embed(title="Webhook Listesi", color=config.COLOR_NORMAL)
                embed.description = "Sunucuda webhook bulunamadı."
                await ctx.reply(embed=embed)
                return
            embed = discord.Embed(title=f"Webhook Listesi ({len(webhooks)})", color=config.COLOR_WARNING)
            for wh in webhooks[:20]:
                ch_text = f"#{wh.channel.name}" if wh.channel else "Silinmiş Kanal"
                embed.add_field(name=wh.name, value=f"Kanal: {ch_text}\nID: `{wh.id}`", inline=False)
            if len(webhooks) > 20:
                embed.set_footer(text=f"+{len(webhooks)-20} webhook daha")
            await ctx.reply(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="Hata", color=config.COLOR_CRITICAL)
            embed.description = str(e)
            await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(WebhookGuard(bot))
