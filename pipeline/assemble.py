#!/usr/bin/env python3
"""
assemble.py — mux each scene's silent video with its narration audio, burn
that beat's word-timed ASS captions, concatenate all beats, and output one
final vertical MP4.

Uses the system ffmpeg (apt-installed: full libx264/aac/mp4 build) -- NOT
the stripped-down ffmpeg-linux binary bundled with Playwright at
/opt/pw-browsers/ffmpeg-1011, which only has webm/vp8/png/mjpeg support
(it exists purely to encode Playwright's own screen-capture frames into
webm, confirmed via `ffmpeg -encoders`/`-muxers`) and cannot decode WAV,
encode AAC/H.264, or mux MP4 at all.

Usage:
    python3 assemble.py --work-dir <dir with beat1.webm/.wav/.ass ... beatN.*> \
        --num-beats 6 --out final.mp4
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STYLE_PATH = os.path.join(HERE, "config", "style.json")


def run(cmd):
    print("+ " + " ".join(cmd), file=sys.stderr)
    subprocess.run(cmd, check=True)


def mux_beat(webm_path, wav_path, ass_path, out_path, width, height):
    """Transcode webm(vp8, no audio) + wav -> one h264/aac mp4 with burned ASS captions."""
    vf = f"scale={width}:{height},setsar=1,ass={ass_path}"
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", webm_path,
        "-i", wav_path,
        "-vf", vf,
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k",
        "-shortest",
        "-r", "30",
        out_path,
    ]
    run(cmd)


def concat_beats(mp4_paths, out_path):
    n = len(mp4_paths)
    inputs = []
    for p in mp4_paths:
        inputs += ["-i", p]
    filter_parts = "".join(f"[{i}:v:0][{i}:a:0]" for i in range(n))
    filter_complex = f"{filter_parts}concat=n={n}:v=1:a=1[outv][outa]"
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[outv]", "-map", "[outa]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k",
        "-movflags", "+faststart",
        out_path,
    ]
    run(cmd)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work-dir", required=True)
    ap.add_argument("--num-beats", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--style", default=STYLE_PATH)
    args = ap.parse_args()

    with open(args.style) as f:
        style = json.load(f)
    width = style["video"]["width"]
    height = style["video"]["height"]

    muxed = []
    for i in range(1, args.num_beats + 1):
        webm = os.path.join(args.work_dir, f"beat{i}.webm")
        wav = os.path.join(args.work_dir, f"beat{i}.wav")
        ass = os.path.join(args.work_dir, f"beat{i}.ass")
        out = os.path.join(args.work_dir, f"beat{i}_final.mp4")
        for p in (webm, wav, ass):
            if not os.path.exists(p):
                print(f"ERROR: missing {p}", file=sys.stderr)
                sys.exit(1)
        mux_beat(webm, wav, ass, out, width, height)
        muxed.append(out)

    concat_beats(muxed, args.out)
    print(json.dumps({"out": args.out}))


if __name__ == "__main__":
    main()
