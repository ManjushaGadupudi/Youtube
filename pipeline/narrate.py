#!/usr/bin/env python3
"""
narrate.py — generate narration WAV for one line of VO text using the
LOCKED narrator voice defined in config/style.json.

Primary engine (locked): espeak-ng, fully offline, voice data ships in the
apt package. See config/style.json -> tts._note_piper for why piper-tts
(the originally preferred engine) is not used: its voice models live on
huggingface.co, which this sandbox's egress proxy blocks (confirmed 403).

Usage:
    python3 narrate.py "Some line of VO text." out.wav
    python3 narrate.py --text-file line.txt out.wav

Always writes a 44.1kHz mono WAV suitable for ffmpeg muxing.
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STYLE_PATH = os.path.join(HERE, "config", "style.json")


def load_style():
    with open(STYLE_PATH) as f:
        return json.load(f)


def synth_espeak(text, out_wav, tts_cfg):
    """Offline synth via espeak-ng. Locked voice/rate/pitch from style.json."""
    raw_wav = out_wav + ".raw.wav"
    cmd = [
        "espeak-ng",
        "-v", tts_cfg["voice"],
        "-s", str(tts_cfg["speed_wpm"]),
        "-p", str(tts_cfg["pitch"]),
        "-a", str(tts_cfg["amplitude"]),
        "-g", str(tts_cfg.get("gap_ms", 6)),
        "-w", raw_wav,
        text,
    ]
    subprocess.run(cmd, check=True)
    # Normalize to 44.1kHz mono PCM16 via ffmpeg for consistent muxing downstream,
    # and apply a gentle loudness normalization so all beats sit at a similar level.
    norm_cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", raw_wav,
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05",
        "-ar", "44100", "-ac", "1",
        out_wav,
    ]
    subprocess.run(norm_cmd, check=True)
    os.remove(raw_wav)


def synth_piper(text, out_wav, voice_model_path):
    """
    UNUSED fallback path, left in place for when/if a future environment can
    reach huggingface.co to fetch a piper voice (e.g.
    en_US-lessac-medium.onnx / .onnx.json into pipeline/voices/).
    Kept here so switching engines later is a one-line change in style.json.
    """
    cmd = [
        "piper",
        "--model", voice_model_path,
        "--output_file", out_wav,
    ]
    subprocess.run(cmd, input=text.encode("utf-8"), check=True)


def get_duration(wav_path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", wav_path],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text", nargs="?", help="VO text to synthesize")
    ap.add_argument("--text-file", help="Read VO text from file instead of argv")
    ap.add_argument("out_wav")
    args = ap.parse_args()

    text = args.text
    if args.text_file:
        with open(args.text_file) as f:
            text = f.read().strip()
    if not text:
        print("ERROR: no text given", file=sys.stderr)
        sys.exit(1)

    style = load_style()
    tts_cfg = style["tts"]

    if tts_cfg["engine"] == "espeak-ng":
        synth_espeak(text, args.out_wav, tts_cfg)
    elif tts_cfg["engine"] == "piper":
        synth_piper(text, args.out_wav, tts_cfg["voice_model_path"])
    else:
        raise ValueError(f"Unknown tts engine: {tts_cfg['engine']}")

    dur = get_duration(args.out_wav)
    print(json.dumps({"wav": args.out_wav, "duration_sec": dur}))


if __name__ == "__main__":
    main()
