import discord
from discord.ext import commands, tasks
import aiohttp
from datetime import datetime
import config
import asyncio

class YoutubeAlarm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.text_channel_id = bot.TEXT_CHANNEL_ID if hasattr(bot, 'TEXT_CHANNEL_ID') else None
        self.voice_channel_id = bot.VOICE_CHANNEL_ID if hasattr(bot, 'VOICE_CHANNEL_ID') else None
        self.waiting_channel_id = bot.WAITING_CHANNEL_ID if hasattr(bot, 'WAITING_CHANNEL_ID') else None
        self.is_live = False
        self.current_video_id = None
        self.live_check_loop.start()

    def cog_unload(self):
        self.live_check_loop.cancel()

    async def check_youtube_live(self):
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={self.bot.FB_CHANNEL_ID}&type=video&eventType=live&key={self.bot.YOUTUBE_API_KEY}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("items"):
                        return data["items"][0]
        return None

    @tasks.loop(seconds=60)
    async def live_check_loop(self):
        if not self.text_channel_id or not self.voice_channel_id or not self.waiting_channel_id:
            return

        live_data = await self.check_youtube_live()

        if live_data and not self.is_live:
            self.is_live = True
            self.current_video_id = live_data["id"]["videoId"]
            title = live_data["snippet"]["title"]
            thumbnail = live_data["snippet"]["thumbnails"]["high"]["url"]
            url = f"https://www.youtube.com/watch?v={self.current_video_id}"

            text_channel = self.bot.get_channel(self.text_channel_id)
            if text_channel:
                embed = discord.Embed(title="🔴 CANLI YAYIN BAŞLADI!", description=f"**[{title}]({url})**\n\nYayın başladı, hemen katıl!", color=0xFF0000, timestamp=datetime.utcnow())
                embed.set_thumbnail(url=thumbnail)
                embed.set_image(url=thumbnail)
                embed.set_footer(text="Fenerbahçe • YouTube Canlı")
                await text_channel.send("@everyone", embed=embed)

            voice_channel = self.bot.get_channel(self.voice_channel_id)
            if voice_channel:
                for guild in self.bot.guilds:
                    for member in guild.members:
                        if member.voice and member.voice.channel:
                            try:
                                await member.move_to(voice_channel)
                            except discord.Forbidden:
                                pass

        elif not live_data and self.is_live:
            self.is_live = False
            self.current_video_id = None

            text_channel = self.bot.get_channel(self.text_channel_id)
            if text_channel:
                embed = discord.Embed(title="⏹️ YAYIN SONA ERDİ", description="Fenerbahçe canlı yayını sona erdi. Bir sonraki yayında görüşmek üzere!", color=0x000080, timestamp=datetime.utcnow())
                embed.set_footer(text="Fenerbahçe • YouTube Canlı")
                await text_channel.send(embed=embed)

            waiting_channel = self.bot.get_channel(self.waiting_channel_id)
            if waiting_channel:
                for guild in self.bot.guilds:
                    for member in guild.members:
                        if member.voice and member.voice.channel and member.voice.channel.id == self.voice_channel_id:
                            try:
                                await member.move_to(waiting_channel)
                            except discord.Forbidden:
                                pass

    @commands.command(name="yayin-ayarla")
    @commands.has_permissions(administrator=True)
    async def yayin_ayarla(self, ctx, text_channel: discord.TextChannel, voice_channel: discord.VoiceChannel, waiting_channel: discord.VoiceChannel):
        self.text_channel_id = text_channel.id
        self.voice_channel_id = voice_channel.id
        self.waiting_channel_id = waiting_channel.id

        # Kalıcılık için bot nesnesine de kaydet
        self.bot.TEXT_CHANNEL_ID = text_channel.id
        self.bot.VOICE_CHANNEL_ID = voice_channel.id
        self.bot.WAITING_CHANNEL_ID = waiting_channel.id

        embed = discord.Embed(title="✅ Yayın Kanalları Ayarlandı", color=0x000080)
        embed.add_field(name="📢 Duyuru Kanalı", value=text_channel.mention)
        embed.add_field(name="🔊 Yayın Sesi", value=voice_channel.mention)
        embed.add_field(name="🛋️ Bekleme Alanı", value=waiting_channel.mention)
        embed.set_footer(text="Fenerbahçe • Yayın Botu")
        await ctx.send(embed=embed)

    @commands.command(name="yayin-kontrol")
    @commands.has_permissions(administrator=True)
    async def yayin_kontrol(self, ctx):
        embed = discord.Embed(title="🔍 Yayın Kontrolü", color=0xFFD700)
        live_data = await self.check_youtube_live()
        if live_data:
            title = live_data["snippet"]["title"]
            url = f"https://www.youtube.com/watch?v={live_data['id']['videoId']}"
            embed.description = f"**[{title}]({url})**"
            embed.add_field(name="Durum", value="🔴 **CANLI YAYINDA**")
        else:
            embed.description = "Şu anda aktif bir canlı yayın bulunamadı."
            embed.add_field(name="Durum", value="⚫ Yayın Yok")
        embed.set_footer(text="Fenerbahçe • Yayın Botu")
        await ctx.send(embed=embed)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="+", intents=intents)
bot.TEXT_CHANNEL_ID = None
bot.VOICE_CHANNEL_ID = None
bot.WAITING_CHANNEL_ID = None
bot.FB_CHANNEL_ID = config.FB_CHANNEL_ID
bot.YOUTUBE_API_KEY = config.YOUTUBE_API_KEY

@bot.event
async def on_ready():
    print(f"Bot {bot.user} olarak giriş yaptı!")

async def main():
    async with bot:
        await bot.add_cog(YoutubeAlarm(bot))
        await bot.start(config.TOKEN)

if __name__ == "__main__":
    asyncio.run(main())