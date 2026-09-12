#!/usr/bin/env python3
"""
build_recap.py — Day 30's format: a fast-cut clip-show recap built from
already-rendered videos, instead of fresh D3 map scenes like every other
day in the lineup.

Structure: a silent title card (drawtext overlay on the first montage
frame), a rapid montage of short muted snippets pulled from N source
videos (one snippet per video, evenly time-sliced to fill the narration's
measured length), a silent CTA card (drawtext on the last frame) -- with
one continuous narration track (generated the same way as every other
video, via narrate.py) laid over the whole thing, and burned captions
synced to that narration text via caption.py + a timestamp shift (caption.py
always starts a track at t=0; here the narration begins after a lead-in,
so its caption timestamps get shifted forward before burning).

Usage:
    python3 build_recap.py <out.mp4>
"""
import glob
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(HERE, "output")
STYLE_PATH = os.path.join(HERE, "config", "style.json")

TITLE_TEXT = "29 STRANGE BORDERS.\nONE MONTH."
CTA_TEXT = "FOLLOW FOR MORE \U0001F30D"
LEAD_IN = 2.2   # seconds, silent title card before narration starts
TAIL_OUT = 3.0  # seconds, silent CTA card after narration ends

NARRATION_TEXT = (
    "Over the last month, this channel covered some of the strangest places "
    "on Earth. A country completely inside another country. Two nations "
    "sharing one room. An island split by the international date line. "
    "A runway that stops traffic to let a plane land. A border painted "
    "straight through someone's kitchen. Twenty five of the wildest "
    "borders and territories geography has ever produced, all in one "
    "place, right here on the channel. If you missed one, go back and "
    "watch it. And follow, because tomorrow brings a brand new one."
)

# One representative rendered clip per earlier day, in lineup order.
# Days 1-4 and the two bonus videos (Baarle, Diomede) were produced on the
# paid Higgsfield pipeline and only exist on a remote CDN, not local disk,
# so this recap covers the 25 locally-rendered videos (Days 5-29).
CLIP_SLUGS = [
    "smallest-country-on-earth", "country-on-a-sea-fort", "land-no-country-wants",
    "island-split-again", "seven-countries-one-slice-antarctica",
    "dangerous-border-became-a-sanctuary", "spain-has-two-cities-in-africa",
    "runway-that-stops-traffic", "head-of-state-is-president-of-france",
    "oldest-republic-smaller-than-a-city", "island-2000-miles-from-anywhere",
    "move-here-without-a-visa", "territory-almost-no-one-recognizes",
    "country-that-almost-no-one-recognizes", "last-divided-capital-city",
    "city-people-think-is-made-up", "africa-borders-drawn-with-a-ruler",
    "island-at-coordinate-zero-zero", "panmunjom-shared-conference-room",
    "northwest-angle-through-canada", "border-that-moves",
    "kiribati-redrew-the-date-line", "neutral-zone-erased-from-the-map",
    "kazungula-four-countries-almost-meet", "khunjerab-pass-shuts-down-for-winter",
]


def run(cmd, **kw):
    print("+", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True, **kw)


def get_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def load_style():
    with open(STYLE_PATH) as f:
        return json.load(f)


def shift_ass(ass_path, offset_sec):
    """Shift every Dialogue timestamp in an ASS file forward by offset_sec."""
    time_re = re.compile(r"(\d+):(\d{2}):(\d{2}\.\d{2})")

    def shift_match(m):
        h, mi, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
        total = h * 3600 + mi * 60 + s + offset_sec
        h2 = int(total // 3600)
        mi2 = int((total % 3600) // 60)
        s2 = total % 60
        return f"{h2:d}:{mi2:02d}:{s2:05.2f}"

    with open(ass_path) as f:
        lines = f.readlines()
    out = []
    for line in lines:
        if line.startswith("Dialogue:"):
            parts = line.split(",", 9)
            parts[1] = time_re.sub(shift_match, parts[1])
            parts[2] = time_re.sub(shift_match, parts[2])
            line = ",".join(parts)
        out.append(line)
    with open(ass_path, "w") as f:
        f.writelines(out)


def main():
    if len(sys.argv) != 2:
        print("usage: build_recap.py <out.mp4>", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]
    style = load_style()
    vid = style["video"]

    missing = [s for s in CLIP_SLUGS if not os.path.exists(os.path.join(OUTPUT_DIR, f"{s}.mp4"))]
    if missing:
        print(f"ERROR: missing rendered clips: {missing}", file=sys.stderr)
        sys.exit(1)

    with tempfile.TemporaryDirectory() as td:
        # 1. Narration (same engine as every other video: narrate.py -> google TTS).
        narration_wav = os.path.join(td, "narration.wav")
        run(["python3", os.path.join(HERE, "narrate.py"), NARRATION_TEXT, narration_wav])
        narration_dur = get_duration(narration_wav)
        total_dur = LEAD_IN + narration_dur + TAIL_OUT
        print(f"narration: {narration_dur:.2f}s, total video: {total_dur:.2f}s")

        # 2. Captions for the narration, shifted forward by LEAD_IN.
        ass_path = os.path.join(td, "recap.ass")
        run(["python3", os.path.join(HERE, "caption.py"), NARRATION_TEXT, str(narration_dur), ass_path])
        shift_ass(ass_path, LEAD_IN)

        # 3. Full audio track: silence(LEAD_IN) + narration + silence(TAIL_OUT).
        silence_lead = os.path.join(td, "silence_lead.wav")
        silence_tail = os.path.join(td, "silence_tail.wav")
        for path, dur in [(silence_lead, LEAD_IN), (silence_tail, TAIL_OUT)]:
            run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi",
                 "-i", f"anullsrc=r=44100:cl=mono", "-t", str(dur), path])
        audio_concat_list = os.path.join(td, "audio_concat.txt")
        with open(audio_concat_list, "w") as f:
            for p in [silence_lead, narration_wav, silence_tail]:
                f.write(f"file '{p}'\n")
        full_audio = os.path.join(td, "full_audio.wav")
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
             "-i", audio_concat_list, full_audio])

        # 4. Silent muted montage: one evenly-sized snippet per clip, sized so
        #    the montage's total length equals the audio's total length.
        n = len(CLIP_SLUGS)
        montage_dur = total_dur
        snippet_dur = montage_dur / n
        snippet_paths = []
        for i, slug in enumerate(CLIP_SLUGS):
            src = os.path.join(OUTPUT_DIR, f"{slug}.mp4")
            snippet = os.path.join(td, f"snip{i:02d}.mp4")
            run(["ffmpeg", "-y", "-loglevel", "error", "-i", src,
                 "-t", str(snippet_dur), "-an",
                 "-vf", f"scale={vid['width']}:{vid['height']},setsar=1",
                 "-r", str(vid.get("fps", 30)),
                 "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                 "-pix_fmt", "yuv420p", snippet])
            snippet_paths.append(snippet)

        video_concat_list = os.path.join(td, "video_concat.txt")
        with open(video_concat_list, "w") as f:
            for p in snippet_paths:
                f.write(f"file '{p}'\n")
        montage = os.path.join(td, "montage.mp4")
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
             "-i", video_concat_list, "-c", "copy", montage])

        # 5. Mux montage + full audio, burn captions + title/CTA drawtext overlays.
        colors = style["colors"]
        title_lines = TITLE_TEXT.split("\n")
        cta_end = total_dur
        cta_start = total_dur - TAIL_OUT
        drawtext_filters = []
        for i, line in enumerate(title_lines):
            y = f"(h/2-80)+{i*90}"
            drawtext_filters.append(
                f"drawtext=text='{line}':fontcolor=white:fontsize=68:"
                f"box=1:boxcolor=black@0.55:boxborderw=20:"
                f"x=(w-text_w)/2:y={y}:enable='lt(t,{LEAD_IN})'"
            )
        drawtext_filters.append(
            f"drawtext=text='{CTA_TEXT}':fontcolor=white:fontsize=60:"
            f"box=1:boxcolor=black@0.55:boxborderw=20:"
            f"x=(w-text_w)/2:y=(h/2-40):enable='gte(t,{cta_start})'"
        )
        vf = ",".join(drawtext_filters) + f",ass={ass_path}"

        run(["ffmpeg", "-y", "-loglevel", "error",
             "-i", montage, "-i", full_audio,
             "-vf", vf,
             "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart",
             out_path])

    print(json.dumps({"out": out_path, "narration_dur": narration_dur, "total_dur": total_dur}))


if __name__ == "__main__":
    main()
