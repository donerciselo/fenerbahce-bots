import discord
import os
import json

_env_loaded = False

def _load_env():
    global _env_loaded
    if _env_loaded:
        return
    try:
        with open(".env") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip()
    except FileNotFoundError:
        pass
    _env_loaded = True

_load_env()

TOKEN = os.getenv("DISCORD_TOKEN", "")
PREFIX = "+"

COLOR_CRITICAL = 0xFF0000
COLOR_WARNING = 0xFFA500
COLOR_NORMAL = 0x00FF00

LOG_CHANNEL_ID = None

ALLOWED_USERS = []

ANTI_NUKE = {
    "max_channel_delete": 3,
    "max_role_delete": 3,
    "max_ban_kick": 3,
    "cooldown": 10,
    "punishment": "ban"
}

ANTI_RAID = {
    "join_threshold": 5,
    "join_window": 10,
    "punishment": "kick"
}

ANTI_SPAM = {
    "max_messages": 5,
    "window": 3,
    "punishment": "timeout",
    "timeout_duration": 300
}

WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
BASE_URL = os.getenv("BASE_URL", "http://localhost:5001")
GUILD_INVITE = os.getenv("GUILD_INVITE", "")

BLACK_OPS = {
    "scan_limit": 1000,
    "webhook_purge_batch": 10,
    "flask_host": "0.0.0.0",
    "flask_port": 5000,
    "base_url": "http://localhost:5000"
}
