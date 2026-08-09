"""PHASE 6 — Voice-over. Synthesize Indonesian narration per scene via OpenAI TTS
(Emergent key), then measure real duration with ffprobe. Voice = master timing.
Writes out/audio/scene-XX.mp3 + out/manifest.json (actual per-scene durations).
"""
import asyncio
import json
import os
import subprocess
import sys

from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

from emergentintegrations.llm.openai import OpenAITextToSpeech  # noqa: E402

import config as C  # noqa: E402
from feature_map import default_project  # noqa: E402


def ffprobe_duration(path: str) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path]
    )
    return float(out.strip())


async def main():
    key = os.getenv("EMERGENT_LLM_KEY")
    tts = OpenAITextToSpeech(api_key=key)
    scenes = default_project()["scenes"]
    manifest = {"voice": C.TTS_VOICE, "model": C.TTS_MODEL, "scenes": []}

    cursor = 0.0
    for s in scenes:
        path = os.path.join(C.AUDIO_DIR, f"{s['id']}.mp3")
        audio = await tts.generate_speech(
            text=s["narration"], model=C.TTS_MODEL, voice=C.TTS_VOICE,
            speed=C.TTS_SPEED, response_format=C.TTS_FORMAT,
        )
        with open(path, "wb") as f:
            f.write(audio)
        dur = ffprobe_duration(path)
        # small breath gap between scenes so cuts feel natural (not on scene 1)
        gap = 0.0 if s["index"] == 1 else 0.15
        start = cursor + gap
        end = start + dur
        cursor = end
        manifest["scenes"].append({
            "id": s["id"], "index": s["index"], "segment": s["segment"],
            "narration": s["narration"], "visual": s["visual"], "action": s["action"],
            "route": s["route"], "record_targets": s["record_targets"],
            "audio": path, "gap_before": gap,
            "audio_duration": round(dur, 3),
            "start": round(start, 3), "end": round(end, 3),
        })
        print(f"{s['id']}: {dur:.2f}s  ->  timeline {start:.2f}-{end:.2f}")

    manifest["total_duration"] = round(cursor, 3)
    with open(os.path.join(C.OUT, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"\nTOTAL VOICE-OVER: {cursor:.2f}s  (target 90 ± ~5s)")


if __name__ == "__main__":
    asyncio.run(main())
