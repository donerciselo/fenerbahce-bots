import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("LEVEL_TOKEN")
PREFIX = "."
NAVY = 0x1A1A5E
GOLD = 0xFFD700
COOLDOWN_SECONDS = 60
MIN_XP = 15
MAX_XP = 25
