#!/usr/bin/env python3
"""
narrate.py — generate narration WAV for one line of VO text using the
LOCKED narrator voice defined in config/style.json.

Primary engine (locked): "google" — the unofficial Google Translate TTS
endpoint (translate.googleapis.com/translate_tts), reachable from this
sandbox (confirmed) unlike huggingface.co/speech.platform.bing.com/
cdn.jsdelivr.net (all confirmed 403). Free, no API key, neural-quality
voice, en/co.uk accent locked in style.json. The endpoint caps request
text around ~200 characters, so long lines are split on sentence
boundaries and the resulting clips concatenated.

Fallback engine: espeak-ng, fully offline (used automatically if the
network call fails, e.g. a transient block). See config/style.json ->
tts._note_piper for why piper-tts (originally preferred) isn't used.

Usage:
    python3 narrate.py "Some line of VO text." out.wav
    python3 narrate.py --text-file line.txt out.wav

Always writes a 44.1kHz mono WAV suitable for ffmpeg muxing.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
STYLE_PATH = os.path.join(HERE, "config", "style.json")
GOOGLE_TTS_URL = "https://translate.googleapis.com/translate_tts"
GOOGLE_TTS_MAX_CHARS = 180  # safety margin under the endpoint's ~200-char cap
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"


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


def _split_for_google(text, max_chars=GOOGLE_TTS_MAX_CHARS):
    """Split text into <=max_chars chunks on sentence, then clause, boundaries."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks = []
    for s in sentences:
        if len(s) <= max_chars:
            chunks.append(s)
            continue
        # sentence itself too long: split on commas/dashes as a fallback
        parts = re.split(r"(?<=[,;—-])\s+", s)
        buf = ""
        for p in parts:
            candidate = (buf + " " + p).strip() if buf else p
            if len(candidate) <= max_chars:
                buf = candidate
            else:
                if buf:
                    chunks.append(buf)
                buf = p
        if buf:
            chunks.append(buf)
    return [c for c in chunks if c.strip()]


def _fetch_google_clip(text, tld):
    url = (
        f"{GOOGLE_TTS_URL}?ie=UTF-8&client=tw-ob&tl=en"
        f"&q={urllib.parse.quote(text)}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as resp:
        if resp.status != 200:
            raise RuntimeError(f"google tts HTTP {resp.status}")
        return resp.read()


def synth_google(text, out_wav, tts_cfg):
    """Primary synth: unofficial Google Translate TTS, chunked + concatenated."""
    chunks = _split_for_google(text)
    tld = tts_cfg.get("google_tld", "com")
    with tempfile.TemporaryDirectory() as td:
        mp3_paths = []
        for i, chunk in enumerate(chunks):
            data = _fetch_google_clip(chunk, tld)
            mp3_path = os.path.join(td, f"part{i:02d}.mp3")
            with open(mp3_path, "wb") as f:
                f.write(data)
            mp3_paths.append(mp3_path)

        if len(mp3_paths) == 1:
            concat_input = mp3_paths[0]
        else:
            list_path = os.path.join(td, "concat.txt")
            with open(list_path, "w") as f:
                for p in mp3_paths:
                    f.write(f"file '{p}'\n")
            concat_input = os.path.join(td, "joined.mp3")
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat",
                 "-safe", "0", "-i", list_path, "-c", "copy", concat_input],
                check=True,
            )

        norm_cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", concat_input,
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,"
                   "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05",
            "-ar", "44100", "-ac", "1",
            out_wav,
        ]
        subprocess.run(norm_cmd, check=True)


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

    engine = tts_cfg["engine"]
    if engine == "google":
        try:
            synth_google(text, args.out_wav, tts_cfg)
        except Exception as e:
            print(f"WARNING: google TTS failed ({e}); falling back to espeak-ng", file=sys.stderr)
            synth_espeak(text, args.out_wav, tts_cfg["fallback_espeak"])
    elif engine == "espeak-ng":
        synth_espeak(text, args.out_wav, tts_cfg)
    elif engine == "piper":
        synth_piper(text, args.out_wav, tts_cfg["voice_model_path"])
    else:
        raise ValueError(f"Unknown tts engine: {engine}")

    dur = get_duration(args.out_wav)
    print(json.dumps({"wav": args.out_wav, "duration_sec": dur}))


if __name__ == "__main__":
    main()
