import discord
from discord.ext import commands
import os
import config
import asyncio
import json

class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def update_config(self, token, prefix, navy, gold, welcome, log, stats, duyuru, mac, auto_role, mod_roles):
        try:
            content = f'''TOKEN = "{token}"
PREFIX = "{prefix}"
NAVY = {navy}
GOLD = {gold}
WELCOME_CHANNEL_ID = {welcome}
LOG_CHANNEL_ID = {log}
STATS_CHANNEL_ID = {stats}
DUYURU_CHANNEL_ID = {duyuru}
MAC_SONUCU_CHANNEL_ID = {mac}
AUTO_ROLE_NAME = "{auto_role}"
MOD_ROLE_NAMES = {mod_roles}
'''
            with open('./config.py', 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print("Config update failed:", e)

    async def get_or_create_role(self, guild, name, color=None):
        role = discord.utils.get(guild.roles, name=name)
        if not role:
            role = await guild.create_role(name=name, color=color or discord.Color.default())
        return role

    @commands.command(name="temizle")
    @commands.has_permissions(administrator=True)
    async def temizle(self, ctx):
        try:
            silinen = 0
            for channel in ctx.guild.channels:
                if channel.category is None and channel.id != ctx.channel.id:
                    try:
                        await channel.delete(reason="Fenerbahçe Bot Temizlik")
                        silinen += 1
                    except Exception:
                        pass
            embed = discord.Embed(title="🧹 Temizlik Tamamlandı!", description=f"Kategorisi olmayan **{silinen}** adet kanal başarıyla silindi.", color=config.GOLD)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="Hata", description=str(e), color=config.NAVY)
            await ctx.send(embed=embed)

    @commands.command(name="kurulum")
    @commands.has_permissions(administrator=True)
    async def kurulum(self, ctx):
        try:
            embed = discord.Embed(title="⚙️ Ultra Fenerbahçe Bot Kurulumu Başlıyor...", description="Lütfen bekleyin, gönderdiğiniz tasarıma uygun devasa sunucu altyapısı inşa ediliyor... (Bu işlem Discord sınırları nedeniyle yaklaşık 1 dakika sürebilir) 💛💙", color=config.GOLD)
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/tr/8/86/Fenerbah%C3%A7e_SK.png")
            msg = await ctx.send(embed=embed)
            
            guild = ctx.guild

            # ROLLER
            roles = {r.name: r for r in guild.roles}
            if config.MOD_ROLE_NAMES[0] not in roles:
                mod_role = await guild.create_role(name=config.MOD_ROLE_NAMES[0], color=discord.Color(config.NAVY), hoist=True, mentionable=True, permissions=discord.Permissions(manage_channels=True, manage_messages=True, manage_roles=True, kick_members=True, ban_members=True))
            else:
                mod_role = roles[config.MOD_ROLE_NAMES[0]]

            if config.AUTO_ROLE_NAME not in roles:
                auto_role = await guild.create_role(name=config.AUTO_ROLE_NAME, color=discord.Color(config.GOLD), hoist=True)
            else:
                auto_role = roles[config.AUTO_ROLE_NAME]

            role_gfb = await self.get_or_create_role(guild, "💙 Genç Fenerbahçeliler", discord.Color(config.NAVY))
            
            # DİĞER TAKIM ROLLERİ
            await self.get_or_create_role(guild, "❤️ Galatasaray", discord.Color.red())
            await self.get_or_create_role(guild, "🖤 Beşiktaş", discord.Color.dark_theme())
            await self.get_or_create_role(guild, "💙 Trabzonspor", discord.Color.blue())

            # IZINLER
            overwrites_mod = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                mod_role: discord.PermissionOverwrite(read_messages=True)
            }
            overwrites_readonly = {
                guild.default_role: discord.PermissionOverwrite(send_messages=False),
                mod_role: discord.PermissionOverwrite(send_messages=True)
            }
            overwrites_locked_vc = {
                guild.default_role: discord.PermissionOverwrite(connect=False)
            }

            # 1. BİLGİLENDİRME
            cat_bilgi = await guild.create_category("📚・BİLGİLENDİRME")
            await guild.create_text_channel("🤍・anılarımız", category=cat_bilgi)

            # 2. FENERBAHÇE SK #HEDEF29
            cat_hedef = await guild.create_category("🌟・FENERBAHÇE SK #HEDEF29")
            await guild.create_voice_channel("discord.gg/fenerbahce", category=cat_hedef, overwrites=overwrites_locked_vc)
            await guild.create_voice_channel("🟡 19 🔵 07 🌙 29", category=cat_hedef, overwrites=overwrites_locked_vc)
            ch_stats = await guild.create_voice_channel(f"👥 Aktif Üye • {guild.member_count}", category=cat_hedef, overwrites=overwrites_locked_vc)
            await guild.create_voice_channel("🔒 #Hedef29", category=cat_hedef, overwrites=overwrites_locked_vc)

            # 3. BOARD
            cat_board = await guild.create_category("🎯・BOARD")
            ch_welcome = await guild.create_text_channel("👋・hoşgeldin", category=cat_board, overwrites=overwrites_readonly)
            ch_duyuru = await guild.create_text_channel("📢・duyuru", category=cat_board, overwrites=overwrites_readonly)
            ch_log = await guild.create_text_channel("🛡️・mod-log", category=cat_board, overwrites=overwrites_mod)
            await guild.create_text_channel("🎉・çekiliş", category=cat_board)
            ch_rol_al = await guild.create_text_channel("🎭・rol・al", category=cat_board, overwrites=overwrites_readonly)
            await guild.create_text_channel("🚀・booster", category=cat_board)
            await guild.create_text_channel("🚀・booster・ayrıcalık", category=cat_board)
            ch_rol_bilgi = await guild.create_text_channel("🎖️・rol・bilgi", category=cat_board, overwrites=overwrites_readonly)
            await guild.create_text_channel("📌・bump", category=cat_board)

            # 4. TOPLULUK
            cat_topluluk = await guild.create_category("👥・TOPLULUK")
            await guild.create_text_channel("💬・sohbet", category=cat_topluluk)
            await guild.create_text_channel("🤖・bot-komut", category=cat_topluluk)
            await guild.create_text_channel("📞・talep・oluştur", category=cat_topluluk)
            ch_gfb_rol = await guild.create_text_channel("💙・gfb・rol", category=cat_topluluk, overwrites=overwrites_readonly)
            await guild.create_text_channel("🎨・gif・banner・wp", category=cat_topluluk)
            await guild.create_text_channel("🎬・edit", category=cat_topluluk)

            # 5. FENERBAHÇE SK
            cat_fb = await guild.create_category("⚽・FENERBAHÇE SK")
            await guild.create_text_channel("🍻・matchday", category=cat_fb)
            await guild.create_text_channel("🔔・maç・günü", category=cat_fb)
            await guild.create_text_channel("📜・ilk・11", category=cat_fb)
            ch_mac = await guild.create_text_channel("🏟️・maç・sonucu", category=cat_fb, overwrites=overwrites_readonly)
            await guild.create_text_channel("⚽・gollerimiz", category=cat_fb)
            await guild.create_text_channel("🟡・canlı-skor", category=cat_fb)

            # 6. ETKİNLİK
            cat_etkinlik = await guild.create_category("🎄・ETKİNLİK")
            await guild.create_text_channel("⚡・skor-tahmin", category=cat_etkinlik)
            await guild.create_text_channel("⚽・ilk-golü-kim-atar", category=cat_etkinlik)
            await guild.create_text_channel("📊・anket", category=cat_etkinlik)
            await guild.create_text_channel("📌・haftanın-sorusu", category=cat_etkinlik)
            await guild.create_text_channel("🔥・macın-oyuncusu", category=cat_etkinlik)
            await guild.create_text_channel("⭐・kim-daha-iyi", category=cat_etkinlik)
            await guild.create_text_channel("🤔・tahmin", category=cat_etkinlik)
            await guild.create_text_channel("😳・ne-yapardın", category=cat_etkinlik)
            await guild.create_text_channel("🙄・kaç-gol-kaç-asist-yapar", category=cat_etkinlik)
            await guild.create_text_channel("🎖️・etkinlik", category=cat_etkinlik)
            await guild.create_text_channel("🎵・takım-marşları", category=cat_etkinlik)
            await guild.create_text_channel("🧾・quiz", category=cat_etkinlik)
            await guild.create_text_channel("🎬・edit-yarışması", category=cat_etkinlik)
            await guild.create_text_channel("🤍・takımda-en-sevdiğin-oyuncu", category=cat_etkinlik)

            # 7. OYUNLAR
            cat_oyunlar = await guild.create_category("🐱・OYUNLAR")
            await guild.create_text_channel("🎰・owo", category=cat_oyunlar)
            await guild.create_text_channel("🎰・owo・2", category=cat_oyunlar)
            await guild.create_text_channel("⚽・soccer-guru", category=cat_oyunlar)
            await guild.create_text_channel("🎱・sayı・sayma", category=cat_oyunlar)
            await guild.create_text_channel("🚀・kelime・oyunu", category=cat_oyunlar)
            await guild.create_text_channel("🎮・bulmaca", category=cat_oyunlar)
            await guild.create_text_channel("🌷・kamyon-arkası-sözler", category=cat_oyunlar)
            await guild.create_text_channel("🎵・müzik-öneri", category=cat_oyunlar)
            await guild.create_text_channel("🔥・ship", category=cat_oyunlar)

            # CONFIG GÜNCELLEMESİ
            token = config.TOKEN
            prefix = config.PREFIX
            navy = "0x1A1A5E"
            gold = "0xFFD700"
            
            self.update_config(token, prefix, navy, gold, ch_welcome.id, ch_log.id, ch_stats.id, ch_duyuru.id, ch_mac.id, config.AUTO_ROLE_NAME, config.MOD_ROLE_NAMES)
            
            # Update in memory
            config.WELCOME_CHANNEL_ID = ch_welcome.id
            config.LOG_CHANNEL_ID = ch_log.id
            config.STATS_CHANNEL_ID = ch_stats.id
            config.DUYURU_CHANNEL_ID = ch_duyuru.id
            config.MAC_SONUCU_CHANNEL_ID = ch_mac.id

            # AUTO POPULATE (Kanalları Doldurma)
            reaction_data = {}

            # 1. Rol Bilgi Mesajı
            embed_bilgi = discord.Embed(title="🛡️ Sunucu Rol Bilgilendirmesi", description="Aşağıda sunucumuzdaki rollerin ne işe yaradığı açıklanmıştır:\n\n**FB-Yönetici:** Sunucuyu yöneten tam yetkili yöneticiler.\n**FB-Taraftar:** Sunucuya yeni katılan taraftarlarımızın varsayılan rolü.\n**🟡🔵 Fenerbahçe:** Fenerbahçe taraftarları.\n**🔴🟡 Galatasaray:** Galatasaray taraftarları.\n**⚫🤍 Beşiktaş:** Beşiktaş taraftarları.\n**🔵🔵 Trabzonspor:** Trabzonspor taraftarları.\n**⚪ Diğer Takımlar:** Diğer takım taraftarları.\n**💙 Genç Fenerbahçeliler:** GFB taraftar grubu üyeleri.", color=config.GOLD)
            embed_bilgi.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/tr/8/86/Fenerbah%C3%A7e_SK.png")
            await ch_rol_bilgi.send(embed=embed_bilgi)

            # 2. GFB Rol Menüsü
            embed_gfb = discord.Embed(title="💙 Genç Fenerbahçeliler", description="GFB Rolünü almak ve özel kanallara erişmek için aşağıdaki 💙 emojisine tıklayın!", color=config.NAVY)
            msg_gfb = await ch_gfb_rol.send(embed=embed_gfb)
            await msg_gfb.add_reaction("💙")
            
            reaction_data[str(msg_gfb.id)] = {
                "💙": role_gfb.id
            }

            # 4. Duyuru Açılış Mesajı
            embed_duyuru = discord.Embed(title="🚀 Ultra Fenerbahçe Sistemi Aktif!", description="Bu sunucu en üst düzey **Fenerbahçe Botu** tarafından başarıyla yapılandırıldı.\n\nTüm koruma sistemleri, Twitter canlı maç takip sistemleri, otomatik sayaçlar ve kanallar kullanıma hazırdır! 💛💙", color=config.GOLD)
            await ch_duyuru.send(embed=embed_duyuru)

            # Reaction data'yı kaydet
            try:
                with open("reaction_roles.json", "w") as f:
                    json.dump(reaction_data, f, indent=4)
            except Exception as e:
                print("Error saving reaction roles:", e)

            success_embed = discord.Embed(title="✅ Muazzam Kurulum & Auto-Populate Tamamlandı!", description="Kanallar dizildi, roller ayarlandı ve **kanalların içleri otomatik mesajlar ile dolduruldu**! Emojilere tıklayarak rol almayı test edebilirsiniz.", color=config.GOLD)
            await msg.edit(embed=success_embed)

        except Exception as e:
            embed = discord.Embed(title="Kurulum Hatası", description=str(e), color=config.NAVY)
            await ctx.send(embed=embed)

    @commands.command(name="takim-rol")
    @commands.has_permissions(administrator=True)
    async def takim_rol(self, ctx):
        try:
            try:
                with open("reaction_roles.json", "r") as f:
                    reaction_data = json.load(f)
            except:
                reaction_data = {}

            embed_rolal = discord.Embed(title="⚽ Takımını Seç", description="Aşağıdaki emojilere tıklayarak takımınızı seçebilirsiniz:\n\n🟡🔵 : Fenerbahçe\n🔴🟡 : Galatasaray\n⚫🤍 : Beşiktaş\n🔵🔵 : Trabzonspor\n⚪ : Diğer Takımlar", color=config.NAVY)
            msg_rolal = await ctx.send(embed=embed_rolal)
            await msg_rolal.add_reaction("🟡")
            await msg_rolal.add_reaction("🔴")
            await msg_rolal.add_reaction("⚫")
            await msg_rolal.add_reaction("🔵")
            await msg_rolal.add_reaction("⚪")

            reaction_data[str(msg_rolal.id)] = {
                "🟡": 1508840869178904576,
                "🔴": 1508855421211906058,
                "⚫": 1508855422927372308,
                "🔵": 1508855425771245698,
                "⚪": 1508892090904346674
            }

            with open("reaction_roles.json", "w") as f:
                json.dump(reaction_data, f, indent=4)

            await ctx.send("✅ Takım rol menüsü oluşturuldu!", delete_after=5)
        except Exception as e:
            await ctx.send(f"Hata: {e}")

async def setup(bot):
    await bot.add_cog(Setup(bot))
