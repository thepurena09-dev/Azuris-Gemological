"""PHASE 8-10 — Render. Trim each real-UI recording to its voice-over length,
build synced Indonesian subtitles (ASS, TikTok safe area), concatenate, and mux
with the voice-over into the final 1080x1920 MP4. Modular: re-run render only.

The voice-over is the master clock. Each scene clip length = audio + tiny gap.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C  # noqa: E402

GAP = 0.08          # tiny breath between scenes
START_TRIM = 0.25   # skip the first-frame white flash of each recording
TMP = os.path.join(C.OUT, "tmp")
os.makedirs(TMP, exist_ok=True)


def run(cmd):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if r.returncode != 0:
        print(r.stdout.decode()[-1500:])
        raise SystemExit(f"ffmpeg failed: {' '.join(cmd[:6])} ...")


def ass_time(t):
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def wrap(text, width=26):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= width:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return "\\N".join(lines[:2]) if len(lines) <= 2 else "\\N".join([" ".join(lines[:len(lines)//2]), " ".join(lines[len(lines)//2:])])


def chunk_words(text, size=9):
    words = text.split()
    return [" ".join(words[i:i + size]) for i in range(0, len(words), size)] or [text]


def build_ass(scenes, timeline):
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {C.W}
PlayResY: {C.H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,DejaVu Sans,52,&H00FFFFFF,&H00FFFFFF,&H00201810,&HB4000000,1,0,0,0,100,100,0,0,3,6,0,2,90,90,470,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for s, (cstart, clen) in zip(scenes, timeline):
        chunks = chunk_words(s["narration"], size=9)
        adur = s["audio_duration"]
        per = adur / len(chunks)
        for i, ch in enumerate(chunks):
            st = cstart + i * per
            en = cstart + (i + 1) * per if i < len(chunks) - 1 else cstart + adur
            events.append(f"Dialogue: 0,{ass_time(st)},{ass_time(en)},Sub,,0,0,0,,{wrap(ch)}")
    path = os.path.join(C.OUT, "subs.ass")
    with open(path, "w") as f:
        f.write(header + "\n".join(events) + "\n")
    return path


def main():
    with open(os.path.join(C.OUT, "manifest.json")) as f:
        scenes = json.load(f)["scenes"]

    vlist, alist, timeline = [], [], []
    cstart = 0.0
    for idx, s in enumerate(scenes):
        gap = 0.0 if idx == len(scenes) - 1 else GAP
        clip_len = round(s["audio_duration"] + gap, 3)
        src = os.path.join(C.VIDEO_DIR, f"scene-{s['index']:02d}.webm")

        vout = os.path.join(TMP, f"v{s['index']:02d}.mp4")
        run(["ffmpeg", "-y", "-ss", str(START_TRIM), "-i", src, "-t", str(clip_len),
             "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p",
             "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", vout])

        aout = os.path.join(TMP, f"a{s['index']:02d}.m4a")
        run(["ffmpeg", "-y", "-i", s["audio"],
             "-af", f"apad=pad_dur={gap + 0.5},loudnorm=I=-16:TP=-1.5:LRA=11",
             "-t", str(clip_len), "-ar", "48000", "-ac", "2", "-c:a", "aac", "-b:a", "192k", aout])

        vlist.append(vout)
        alist.append(aout)
        timeline.append((cstart, clip_len))
        cstart += clip_len

    # concat lists
    vtxt = os.path.join(TMP, "v.txt")
    atxt = os.path.join(TMP, "a.txt")
    with open(vtxt, "w") as f:
        f.write("\n".join(f"file '{p}'" for p in vlist))
    with open(atxt, "w") as f:
        f.write("\n".join(f"file '{p}'" for p in alist))

    vall = os.path.join(TMP, "video_all.mp4")
    aall = os.path.join(TMP, "audio_all.m4a")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", vtxt, "-c", "copy", vall])
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", atxt, "-c", "copy", aall])

    subs = build_ass(scenes, timeline)

    run(["ffmpeg", "-y", "-i", vall, "-i", aall,
         "-vf", f"ass={subs}",
         "-map", "0:v:0", "-map", "1:a:0",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", C.FINAL])

    dur = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", C.FINAL]).strip().decode()
    print(f"\nFINAL: {C.FINAL}  ({float(dur):.2f}s, {C.W}x{C.H})")


if __name__ == "__main__":
    main()
