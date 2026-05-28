import discord
from discord.ext import commands, tasks
import aiohttp
import xml.etree.ElementTree as ET
import config

class Twitter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_tweet_url = None
        self.check_twitter.start()

    def cog_unload(self):
        self.check_twitter.cancel()

    @tasks.loop(minutes=5)
    async def check_twitter(self):
        # API kullanmadan RSSHub veya benzeri açık kaynaklı proxy'ler üzerinden kontrol
        # Twitter'ın katı kısıtlamalarına takılmamak için RSS tabanlı kontrol yapıyoruz
        rss_url = "https://rsshub.app/twitter/user/Fenerbahce"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(rss_url, timeout=10) as response:
                    if response.status == 200:
                        content = await response.read()
                        root = ET.fromstring(content)
                        
                        # İlk 'item' elementi en son atılan tweettir
                        item = root.find('.//item')
                        if item is not None:
                            title = item.find('title').text
                            link = item.find('link').text
                            
                            # Eğer bot ilk defa açılıyorsa spam yapmaması için son tweeti kaydet
                            if self.last_tweet_url is None:
                                self.last_tweet_url = link
                                return
                                
                            # Yeni bir tweet geldiyse
                            if link != self.last_tweet_url:
                                self.last_tweet_url = link
                                
                                # Eğer maç sonucuysa (MS veya Maç Sonucu kelimeleri geçiyorsa)
                                upper_title = title.upper()
                                if "MS" in upper_title or "MAÇ SONUCU" in upper_title:
                                    channel_id = getattr(config, 'MAC_SONUCU_CHANNEL_ID', None)
                                    if channel_id:
                                        channel = self.bot.get_channel(channel_id)
                                        if channel:
                                            embed = discord.Embed(title="⚽ Maç Sonucu", description=title, color=config.NAVY)
                                            embed.add_field(name="Bağlantı", value=f"[Tweet'e Git]({link})", inline=False)
                                            embed.set_author(name="Fenerbahçe SK", icon_url="https://upload.wikimedia.org/wikipedia/tr/8/86/Fenerbah%C3%A7e_SK.png")
                                            await channel.send(embed=embed)
        except Exception as e:
            # RSSHub rate limit yediğinde konsolu kirletmemek için pass geçebiliriz
            pass

    @check_twitter.before_loop
    async def before_check_twitter(self):
        await self.bot.wait_until_ready()

    @commands.command(name="tweet")
    @commands.has_any_role(*config.MOD_ROLE_NAMES)
    async def mock_tweet(self, ctx, *, icerik: str):
        embed = discord.Embed(title="🐦 Yeni Tweet (Manuel)", description=icerik, color=0x1DA1F2)
        embed.set_author(name="Fenerbahçe SK", icon_url="https://upload.wikimedia.org/wikipedia/tr/8/86/Fenerbah%C3%A7e_SK.png")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Twitter(bot))
