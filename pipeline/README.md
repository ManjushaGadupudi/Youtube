# Local zero-cost video pipeline

Turns a written GeoGlobeTales-style script into a finished ~60s vertical
(1080x1920) MP4, fully locally: no paid AI APIs, no external network calls
at render time beyond the one-time package installs already done in this
environment.

## Why this exists

The Higgsfield AI-video workflow (seedance/minimax) costs credits per clip.
This pipeline replaces it with deterministic D3 map rendering + local TTS,
reusing the same visual identity (blue water, green land, gold-highlighted
target country, single consistent narrator voice, burned captions) at
**zero marginal cost per video**.

## Locked identity (do not drift between videos)

All of this lives in `config/style.json` — change it there once, not per-scene.

| | Value |
|---|---|
| Water | `#3A6EA5` |
| Land | `#74A35D` |
| Highlight (target country outline) | `#D4A72C` / `#F2CF6B` |
| Narrator | espeak-ng, voice `en-us`, 170 wpm, pitch 38 |
| Captions | word-timed ASS, even time-slicing (see Blockers) |
| Video | 1080x1920, 30fps, h264/aac mp4 |

## Pipeline stages

```
scripts/<name>.md  →  scripts/<name>.scenes.json  →  build_video.js  →  output/<name>.mp4
```

1. **`maps/build_scene_html.js`** — Node/D3 module. Given one beat's scene
   spec (highlight country codes, a pan/zoom camera path as two lon/lat
   bounding boxes, markers, animated lines, on-screen text), produces a
   self-contained HTML page. D3 (`geoMercator`/`geoPath`/`fitExtent`) runs
   server-side in Node to convert `world-atlas`'s 110m TopoJSON to GeoJSON
   and to compute exact projection parameters per camera keyframe; the real
   `d3.js` UMD bundle is inlined into the page (no CDN) so the SAME d3
   projection math re-renders every animation frame in-browser as the
   camera tweens between keyframes.
   - `maps/country-codes.json` maps ISO alpha-2 codes to the numeric ids
     `world-atlas` uses. It covers every real country in `content-calendar.md`.
     Non-country topics (Sealand, Bir Tawil, Null Island, Transnistria,
     Nagorno-Karabakh, the JSA building, the old Saudi-Iraq Neutral Zone)
     aren't in the countries layer — use `markers`/`lines` instead of
     `highlight` for those, see "Scenes that aren't a country" below.
2. **`render_scene.js`** — given a scene spec + duration, launches
   Playwright/Chromium (`/opt/pw-browsers/chromium`), loads the generated
   HTML, and uses Playwright's built-in `recordVideo` to capture exactly
   `duration` seconds as a silent `.webm`.
3. **`narrate.py`** — one VO line → one WAV via the locked espeak-ng voice
   (loudness-normalized, silence-trimmed).
4. **`caption.py`** — one VO line + its WAV's measured duration → one `.ass`
   word-chunk caption track, timed by even slicing across the duration.
5. **`assemble.py`** — per beat: mux the silent `.webm` with its `.wav`,
   burn that beat's `.ass` captions, transcode to h264/aac (system
   `ffmpeg`, **not** the Playwright-bundled one — see Blockers). Then
   concatenates all beats into one final MP4 with `+faststart`.
6. **`build_video.js`** — orchestrator. Runs 1-5 for every beat in a
   scene-spec JSON, then calls `assemble.py`.

## Running it on a new script

1. Write the script as usual under `scripts/<name>.md` (6 beats of VO +
   ON-SCREEN TEXT, per the existing template).
2. Hand-author `scripts/<name>.scenes.json` next to it — same convention as
   `scripts/russia-with-no-border-to-russia.scenes.json`. For each beat:
   - `voText`: the beat's VO line (numerals spelled out, e.g. "two hundred"
     not "200" — espeak-ng reads digits inconsistently).
   - `onScreenText`: the script's ON-SCREEN TEXT cue.
   - `highlight`: `["XX"]` alpha-2 code(s) to gold-outline (must exist in
     `maps/country-codes.json`, add it there if missing).
   - `camera.from` / `camera.to`: `[[west,south],[east,north]]` lon/lat
     boxes for the start/end of that beat's pan/zoom. Use a real map or globe
     to eyeball these — there's no auto-framing. **Do not hand-write the
     ring winding yourself elsewhere in the codebase** — `fitBBoxProjection`
     already handles d3-geo's (counter-intuitive) winding convention; just
     pass `[[west,south],[east,north]]` and it works.
   - `markers` (optional): `{lonlat:[lon,lat], label, emoji?, showAt}` —
     `showAt` is a 0-1 fraction of the beat's duration.
   - `lines` (optional): `{points:[[lon,lat],...], dashed, showAt, drawDuration}`
     — animates a "draw-on" reveal; `dashed:true` for a dashed stroke.
   - Don't set `duration` — it's filled in automatically from the measured
     narration length.
3. `cd pipeline && node build_video.js ../scripts/<name>.scenes.json output/<name>.mp4`
4. Preview quickly without a full render: there's no bundled preview script
   (it was a scratch file, not committed), but the same idea — load the
   generated scene HTML in Playwright and `page.screenshot()` at t=0 and
   t=duration — is the fastest way to sanity-check a bounding box before
   committing to a full ~2min pipeline run. `build_scene_html.js` is also
   runnable standalone: `node maps/build_scene_html.js beat.json out.html`.

This is close to a mechanical loop for future scripts once the beat bboxes
are chosen — the actual TTS/caption/render/assemble steps need zero manual
intervention. Camera framing per beat is still a judgment call (there's no
auto-fit-to-story-beat logic), so budget ~15-30 min per script picking
reasonable bounding boxes, plus one full pipeline run (~2 min) to check
the result. Iterate with the screenshot trick above rather than full
renders when tuning framing.

### Scenes that aren't a country

For lineup topics without a matching country polygon (Sealand, Bir Tawil,
Null Island, Transnistria, Nagorno-Karabakh, JSA/Panmunjom, the old
Saudi-Iraq Neutral Zone), set `highlight: []` and instead use a `marker`
(a gold dot + label, optionally an emoji) at the relevant lon/lat, and/or a
`lines` entry to draw a border/boundary shape. The visual language (gold =
the thing the video is about) still reads correctly.

## Blockers hit, and what was done about them

**Piper TTS voice models are unreachable.** `piper-tts` installed fine, and
IS the better engine (it's a real neural TTS, not formant synthesis), but
its voice files (`.onnx`/`.onnx.json`) are hosted on `huggingface.co`,
which this sandbox's egress proxy blocks outright (`403` on `CONNECT`,
confirmed via the proxy status endpoint — this is an organization policy
denial, not a flaky network). **Fallback used: `espeak-ng`**, fully offline
(voice data ships in the apt package). It's the lower-quality, more
robotic-sounding option the task anticipated as the fallback. If a future
environment can reach huggingface.co, `narrate.py` already has an unused
`synth_piper()` code path — flip `tts.engine` to `"piper"` in
`config/style.json`, drop a voice model in `pipeline/voices/`, and it's a
one-line swap.

**faster-whisper model weights are also unreachable.** Same story: its CPU
models are pulled from huggingface.co at first use (also blocked), and the
openai-whisper Azure mirror (`openaipublic.azureedge.net`) is blocked by
the same proxy policy too (also verified with a direct `curl`, also `403`).
**Fallback used: even time-slicing.** Since the script text is already
known (it's not being transcribed from scratch), `caption.py` splits it
into small word-chunks and distributes them evenly across the beat's
*measured* narration duration. Not true forced alignment — timing can
drift a little around punctuation-driven pauses in the narrator — but
fully deterministic, offline, and close enough given the narrator's
even, pre-tuned ~20-word lines.

**The Playwright-bundled `ffmpeg-linux` at `/opt/pw-browsers/ffmpeg-1011`
cannot mux the final video.** It's a deliberately stripped build (confirmed
via `ffmpeg -encoders`/`-decoders`/`-muxers`): only `mjpeg` decode,
`libvpx`/`png` encode, and an `image2`/`webm` muxer — it exists purely so
Playwright can turn its own screen-capture PNG frames into a `.webm`, not
as a general-purpose tool. It has no WAV decoder, no AAC/H.264 encoder, and
no MP4 muxer at all. **Fix: `apt-get install -y ffmpeg`** (root access was
already available) got a full build (`libx264`, `aac`, `mp4` muxer, all
present) at the normal `ffmpeg` PATH entry, which `assemble.py` uses for
everything. `render_scene.js`/Playwright's own video recording doesn't
touch either ffmpeg binary — Playwright records video internally.

**d3-geo's polygon winding convention bit us once.** `fitBBoxProjection()`
builds a small lon/lat rectangle as a GeoJSON `Polygon` to feed
`d3.geoMercator().fitExtent()`. A ring that looks counter-clockwise in
plain lon/lat x-y (the GeoJSON/RFC7946 convention) reads to d3-geo as "the
rest of the sphere minus this rectangle" — i.e. it silently computed a
whole-world-sized bounding box instead of the small one requested,
producing a fixed, non-zooming camera. Fixed by ordering the ring
clockwise in lon/lat x-y (see the comment at the top of
`fitBBoxProjection`). Worth knowing if anyone hand-edits that function.

## What's needed for the remaining 26 scripts

For each remaining day in `content-calendar.md`:

1. Write the script (as before).
2. Author `<script>.scenes.json` by hand — 6 beats, mostly copy-pasting the
   Kaliningrad one's shape and changing `voText`, `onScreenText`,
   `highlight`, and the camera bboxes/markers/lines to fit the new topic.
   This is the only manual/judgment-call step left.
3. `node build_video.js <script>.scenes.json output/<name>.mp4` — fully
   automatic from there (~2 min end to end for a 6-beat/~60s video on this
   machine).
4. Spot-check the MP4 (frame grabs via `ffmpeg -vf fps=1/5` are fast) before
   publishing — camera framing is not auto-validated, so a bad bbox (too
   tight, wrong hemisphere, etc.) won't error, it'll just look wrong.

No further tool installs, network access, or per-video code changes are
needed — this is a real "script → JSON → mp4" loop now, gated only by the
time it takes a human (or Claude) to pick reasonable bounding boxes for
each beat.
