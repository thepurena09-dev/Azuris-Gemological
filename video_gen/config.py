"""Shared config for the standalone AZURIS TikTok walkthrough video pipeline.

This lives OUTSIDE the web app (backend/frontend untouched). It renders a real
MP4 file for upload to TikTok, using the verified feature map + script.
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "out")
AUDIO_DIR = os.path.join(OUT, "audio")
VIDEO_DIR = os.path.join(OUT, "video")
FINAL = os.path.join(OUT, "azuris_tiktok_walkthrough.mp4")

# Preview app under test (real UI). Read from frontend/.env so we never guess.
def _preview_url():
    try:
        with open("/app/frontend/.env") as f:
            for line in f:
                if line.startswith("REACT_APP_BACKEND_URL="):
                    return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return "http://localhost:3000"

APP_URL = _preview_url()

# 9:16 TikTok
W, H = 1080, 1920

# Voice (OpenAI TTS via Emergent key)
TTS_MODEL = "tts-1-hd"
TTS_VOICE = "onyx"          # deep, professional, trustworthy (luxury brand)
TTS_SPEED = 1.12            # natural energetic pacing tuned to land ~90s total
TTS_FORMAT = "mp3"

# Admin login (recording only — never shown/burned into the video)
ADMIN_EMAIL = "admin@azuris.local"
ADMIN_PASSWORD = "AzurisDev@2026!"

for d in (OUT, AUDIO_DIR, VIDEO_DIR):
    os.makedirs(d, exist_ok=True)
