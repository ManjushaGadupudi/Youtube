#!/usr/bin/env python3
"""
caption.py — generate word-timed burned captions for one narration beat.

Preferred method (locked in config/style.json as the *intended* method):
faster-whisper CPU forced-alignment/transcription for real word-level
timestamps. UNAVAILABLE in this sandbox: faster-whisper's model weights are
fetched from huggingface.co at first use, and this sandbox's egress proxy
blocks huggingface.co (403 on CONNECT) as well as the openaipublic
Azure mirror used by openai-whisper. Both were verified blocked before
falling back.

Fallback method actually used (config: captions.method = "even_time_slicing"):
we already KNOW the exact script text (it's pre-written, not transcribed),
so we split it into small word-chunks and distribute those chunks evenly
across the beat's MEASURED audio duration (from ffprobe). This is not true
forced alignment -- timing can drift a little around punctuation/pauses --
but it's deterministic, fully offline, and close enough for a calm,
evenly-paced narrator reading short pre-tuned lines.

Usage:
    python3 caption.py "VO text here." 9.79 out.ass
"""
import argparse
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
STYLE_PATH = os.path.join(HERE, "config", "style.json")

ASS_HEADER = """[Script Info]
ScriptType: v4.00+
WrapStyle: 0
PlayResX: {width}
PlayResY: {height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,{font},{fontsize},{primary},&H000000FF,{outline},&H00000000,-1,0,0,0,100,100,0,0,1,{outline_w},2,2,60,60,{marginv},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def hex_to_ass_color(hex_color):
    """#RRGGBB -> ASS &H00BBGGRR"""
    h = hex_color.lstrip("#")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H00{b}{g}{r}".upper()


def to_ass_time(t):
    if t < 0:
        t = 0.0
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"


def tokenize(text):
    # Keep words with attached punctuation for natural reading chunks.
    return [w for w in re.split(r"\s+", text.strip()) if w]


def chunk_words(words, chunk_size):
    return [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]


def build_ass(text, duration, out_path, style, on_screen_text=None):
    words = tokenize(text)
    chunk_size = style["captions"].get("words_per_chunk", 3)
    chunks = chunk_words(words, chunk_size)
    n = len(chunks)
    if n == 0:
        raise ValueError("No words to caption")

    # Even time-slicing across the measured audio duration, weighted by each
    # chunk's word count so short trailing chunks don't get an oversized slot.
    total_words = sum(len(c) for c in chunks)
    colors = style["colors"]
    vid = style["video"]

    header = ASS_HEADER.format(
        width=vid["width"],
        height=vid["height"],
        font=style["fonts"]["captionFamily"],
        fontsize=style["captions"]["fontSizePx"],
        primary=hex_to_ass_color(colors["captionText"]),
        outline=hex_to_ass_color(colors["captionOutline"]),
        outline_w=4,
        marginv=style["captions"]["marginBottomPx"],
    )

    lines = [header]
    t = 0.0
    word_cursor = 0
    cue_words = []
    for chunk in chunks:
        frac = len(chunk) / total_words
        chunk_dur = duration * frac
        start = t
        end = min(t + chunk_dur, duration)
        txt = " ".join(chunk).upper()
        txt = txt.replace("{", "").replace("}", "")
        lines.append(
            f"Dialogue: 0,{to_ass_time(start)},{to_ass_time(end)},Caption,,0,0,0,,{txt}"
        )
        cue_words.append({"text": " ".join(chunk), "start": start, "end": end})
        t = end

    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")

    return cue_words


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text")
    ap.add_argument("duration", type=float)
    ap.add_argument("out_ass")
    ap.add_argument("--style", default=STYLE_PATH)
    args = ap.parse_args()

    with open(args.style) as f:
        style = json.load(f)

    cues = build_ass(args.text, args.duration, args.out_ass, style)
    print(json.dumps({"ass": args.out_ass, "method": "even_time_slicing", "cues": cues}))


if __name__ == "__main__":
    main()
