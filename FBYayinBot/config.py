import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("YAYIN_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
FB_CHANNEL_ID = os.getenv("FB_CHANNEL_ID")
def _env_int(key):
    v = os.getenv(key, "").strip()
    return int(v) if v else None

TEXT_CHANNEL_ID = _env_int("TEXT_CHANNEL_ID")
VOICE_CHANNEL_ID = _env_int("VOICE_CHANNEL_ID")
WAITING_CHANNEL_ID = _env_int("WAITING_CHANNEL_ID")
