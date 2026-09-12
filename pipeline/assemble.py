#!/usr/bin/env python3
"""
assemble.py — mux each scene's silent video with its narration audio,
crossfade-dissolve all beats together (video xfade + audio acrossfade,
instead of a hard cut), then burn ONE merged word-timed caption track
over the whole thing and output the final vertical MP4.

Why crossfade instead of a hard concat: each beat is rendered as its own
independent Playwright clip, and even when consecutive beats' camera
bounding boxes are chained (beat N's `to` == beat N+1's `from`, so the map
POSITION is continuous), a straight `concat` still produces a visible cut --
different clips, spliced instantly, plus each beat's eased camera motion
decelerates toward zero velocity right at that exact splice point and then
re-accelerates, reading as a stutter. A short crossfade (default 0.35s)
smooths that seam into a dissolve instead of a hard pop.

Why captions are merged and burned ONCE at the end, not per-beat: burning
each beat's captions before crossfading would put two different beats'
caption lines on screen at once during every overlap window (beat N's
fading out while beat N+1's fades in), which looks like a glitch. Instead,
every beat's caption cues (from caption.py, which times them 0..duration
for that beat alone) get shifted onto the ONE shared final timeline -- at
the same offsets the video/audio crossfades use -- and merged into a single
.ass file burned in one pass at the very end.

Uses the system ffmpeg (apt-installed: full libx264/aac/mp4 build) -- NOT
the stripped-down ffmpeg-linux binary bundled with Playwright at
/opt/pw-browsers/ffmpeg-1011 (webm/vp8/png/mjpeg only, no WAV decode, no
AAC/H.264 encode, no MP4 muxer -- see git history for how that was found).

Usage:
    python3 assemble.py --work-dir <dir with beat1.webm/.wav/.ass ... beatN.*> \
        --num-beats 6 --out final.mp4 [--overlap 0.35]
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STYLE_PATH = os.path.join(HERE, "config", "style.json")


def run(cmd):
    print("+ " + " ".join(cmd), file=sys.stderr)
    subprocess.run(cmd, check=True)


def get_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def mux_beat(webm_path, wav_path, out_path, width, height):
    """Transcode webm(vp8, no audio) + wav -> one h264/aac mp4. No captions
    burned here anymore -- that happens once, at the very end, post-crossfade."""
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", webm_path,
        "-i", wav_path,
        "-vf", f"scale={width}:{height},setsar=1",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k",
        "-shortest",
        "-r", "30",
        out_path,
    ]
    run(cmd)


def crossfade_concat(mp4_paths, durations, overlap, out_path):
    """Chain xfade (video) + acrossfade (audio) across N clips and return the
    per-clip start offset on the FINAL merged timeline (for caption shifting)."""
    n = len(mp4_paths)
    if n == 1:
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4_paths[0], "-c", "copy", out_path])
        return [0.0]

    inputs = []
    for p in mp4_paths:
        inputs += ["-i", p]

    offsets = [0.0]
    v_chain = []
    a_chain = []
    running_total = durations[0]
    prev_v = "0:v"
    prev_a = "0:a"
    for i in range(1, n):
        offset = running_total - overlap
        offsets.append(offset)
        out_v = f"v{i}"
        out_a = f"a{i}"
        v_chain.append(
            f"[{prev_v}][{i}:v]xfade=transition=fade:duration={overlap}:offset={offset:.3f}[{out_v}]"
        )
        a_chain.append(
            f"[{prev_a}][{i}:a]acrossfade=d={overlap}[{out_a}]"
        )
        prev_v, prev_a = out_v, out_a
        running_total = offset + durations[i]

    filter_complex = ";".join(v_chain + a_chain)
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", f"[{prev_v}]", "-map", f"[{prev_a}]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k",
        out_path,
    ]
    run(cmd)
    return offsets


TIME_RE = re.compile(r"(\d+):(\d{2}):(\d{2}\.\d{2})")


def _parse_time(s):
    h, mi, sec = TIME_RE.match(s).groups()
    return int(h) * 3600 + int(mi) * 60 + float(sec)


def _format_time(t):
    t = max(0.0, t)
    h = int(t // 3600)
    mi = int((t % 3600) // 60)
    s = t % 60
    return f"{h:d}:{mi:02d}:{s:05.2f}"


def merge_ass(ass_paths, offsets, out_path):
    """Read each beat's 0-based .ass, shift its Dialogue lines onto the final
    merged timeline (same offsets the crossfade used), and -- critically --
    cap each beat's cues so they never extend past the point the NEXT beat's
    crossfade begins. Without this cap, beat N's last caption chunk is still
    "active" (per its original start/end) right as beat N+1's first chunk
    starts at the shared overlap window, and the ASS renderer stacks both
    lines on screen at once during every crossfade. Capping beat N's cues to
    end at offsets[N+1] (and dropping/shortening any cue that would become
    zero-length) makes the caption handoff clean: one line disappears exactly
    as the next appears, in sync with the video dissolve underneath it."""
    header_lines = None
    dialogue_lines = []
    n = len(ass_paths)
    for i, (ass_path, offset) in enumerate(zip(ass_paths, offsets)):
        cap = offsets[i + 1] if i + 1 < n else None
        with open(ass_path) as f:
            lines = f.readlines()
        if header_lines is None:
            header_lines = [l for l in lines if not l.startswith("Dialogue:")]
        for line in lines:
            if not line.startswith("Dialogue:"):
                continue
            parts = line.split(",", 9)
            start = _parse_time(parts[1]) + offset
            end = _parse_time(parts[2]) + offset
            if cap is not None:
                end = min(end, cap)
            if end <= start:
                continue  # this cue got fully squeezed out by the cap; drop it
            parts[1] = _format_time(start)
            parts[2] = _format_time(end)
            dialogue_lines.append(",".join(parts))
    with open(out_path, "w") as f:
        f.writelines(header_lines)
        f.writelines(dialogue_lines)


def burn_captions(in_path, ass_path, out_path):
    run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", in_path,
        "-vf", f"ass={ass_path}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k",
        "-movflags", "+faststart",
        out_path,
    ])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work-dir", required=True)
    ap.add_argument("--num-beats", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--style", default=STYLE_PATH)
    ap.add_argument("--overlap", type=float, default=0.35, help="crossfade duration in seconds")
    args = ap.parse_args()

    with open(args.style) as f:
        style = json.load(f)
    width = style["video"]["width"]
    height = style["video"]["height"]

    muxed = []
    ass_paths = []
    for i in range(1, args.num_beats + 1):
        webm = os.path.join(args.work_dir, f"beat{i}.webm")
        wav = os.path.join(args.work_dir, f"beat{i}.wav")
        ass = os.path.join(args.work_dir, f"beat{i}.ass")
        out = os.path.join(args.work_dir, f"beat{i}_muxed.mp4")
        for p in (webm, wav, ass):
            if not os.path.exists(p):
                print(f"ERROR: missing {p}", file=sys.stderr)
                sys.exit(1)
        mux_beat(webm, wav, out, width, height)
        muxed.append(out)
        ass_paths.append(ass)

    durations = [get_duration(p) for p in muxed]
    # Clamp overlap so it never exceeds the shortest beat's own length (an
    # overlap longer than a clip is nonsensical and breaks xfade's offsets).
    overlap = min(args.overlap, min(durations) * 0.4)

    crossfaded = os.path.join(args.work_dir, "crossfaded.mp4")
    offsets = crossfade_concat(muxed, durations, overlap, crossfaded)

    merged_ass = os.path.join(args.work_dir, "merged.ass")
    merge_ass(ass_paths, offsets, merged_ass)

    burn_captions(crossfaded, merged_ass, args.out)
    print(json.dumps({"out": args.out, "overlap": overlap, "offsets": offsets}))


if __name__ == "__main__":
    main()
