# Canva Production Guide

How to turn any of the `scripts/*.md` files into a finished video by hand in Canva. Worked example below uses `scripts/russia-with-no-border-to-russia.md` (Kaliningrad); the same structure applies to every other script in the repo — they all follow the identical 6-beat template.

---

## 1. Project setup (do this once, reuse for every video)

- **Canva design type:** "Video" → custom size **1080 x 1920px** (9:16 vertical)
- **Timeline:** one Canva "page" per beat = 6 pages, each set to that beat's voiceover duration (see per-beat timing below) — Canva lets you set exact page duration in seconds in the bottom timeline bar
- **Font:** search **"Archivo Black"** in Canva's font picker (it's in Canva's native library) — use it for all on-screen headline text, to keep it visually consistent with the bold/punchy style
- **Color palette** (save these as a Canva brand kit/palette so every video matches):

| Element | Hex |
|---|---|
| Water | `#3A6EA5` |
| Land | `#74A35D` |
| Highlighted country | `#D4A72C` (fill) / `#F2CF6B` (outline) |
| Background/dark accents | `#0B1E33` |
| On-screen text | `#FFFFFF` with a soft black drop shadow |
| Marker badge | `#D4A72C` fill, `#0B1E33` text |

- **Map source:** Canva's element search has map illustrations — search "world map," "Europe map," or use the **Maps app** (Canva has a built-in Maps app under Apps → search "Maps") which lets you drop a pin/highlight a specific country or region directly — much easier than hand-drawing borders. Recolor it to the palette above (select element → Edit colors).
- **Transitions:** use Canva's **"Fade"** transition between every page, set to **~0.3-0.4 seconds** — matches the crossfade timing used in the earlier pipeline version and avoids hard jump-cuts between scenes.

---

## 2. Voiceover — pick one path

**Option A: Record it yourself**
- Quiet room, phone voice memo app or a USB mic is fine
- Natural conversational pace, roughly 150-160 words/minute — don't rush
- Record each of the 6 lines as a separate clip (easier to re-take one line without redoing the whole thing)
- Leave a half-second of silence at the start/end of each clip for clean trimming
- Tone: calm, confident, slightly deadpan-surprised — like you're telling a friend a wild fact you just learned, not narrating a documentary

**Option B: Canva's built-in Text to Speech**
- In the Canva editor: **Apps → search "Text to Speech"** (sometimes listed as "Canva Voice")
- Paste each beat's VO line in, preview a few voices, and pick ONE voice and stick with it for all 6 scenes (consistency matters more than any single line sounding perfect)
- This tends to sound more natural than the free Google Translate TTS hack used in the automated pipeline — worth trying first before recording yourself, since it's zero extra effort

Either way: generate/record all 6 lines FIRST, drop each onto its matching page, and set that page's duration to match the actual clip length — everything else (map animation timing, on-screen text) should follow the voice, not the other way around.

---

## 3. Per-beat breakdown (worked example: Kaliningrad)

### Beat 1 — Hook (~9-10s)
**VO:** "This is Russian territory. It shares no land border with the rest of Russia — the closest Russian soil is over 200 miles away."
**Visual:** Map zoomed out to show the Baltic region; Kaliningrad highlighted in gold, rest of Russia far to the east (not visible in frame) — the geographic separation IS the hook, so keep it visually obvious.
**On-screen text (Canva text animation: "Rise"):** "200 miles from the rest of Russia."
**Canva tip:** apply a subtle "Pan" or slow zoom-in animation to the map element itself (Animate panel → Zoom, slow speed) for the push-in feel.

### Beat 2 — Setup (~9s)
**VO:** "It's called Kaliningrad — wedged between Poland and Lithuania, on the Baltic Sea, completely cut off from mainland Russia by land."
**Visual:** Zoom into the Kaliningrad/Poland/Lithuania area. Highlight Kaliningrad gold, keep Poland/Lithuania in the base green.
**On-screen text:** "Squeezed between two other countries."
**Add:** two small text labels directly on the map — "POLAND" and "LITHUANIA" (Canva: small text boxes, Archivo Black, white text with dark outline) fading in with "Fade" animation around the 3-4s mark.

### Beat 3 — Escalation 1 (~11s)
**VO:** "Before World War Two, this was German territory — the city of Königsberg. The Soviet Union kept it after the war, and never gave it back."
**Visual:** Same framing as Beat 2, optionally a quick label swap animation: "KÖNIGSBERG" fading out, "KALININGRAD" fading in, to show the renaming.
**On-screen text:** "Once German. Never returned."

### Beat 4 — Escalation 2 (~9s)
**VO:** "Today it's Russia's only Baltic Sea port that never freezes — which makes it one of the most strategically important pieces of land Russia owns."
**Visual:** Tighter zoom on the coastline/port area. Add a small anchor icon (Canva elements → search "anchor icon") at the port location.
**On-screen text:** "Russia's only ice-free Baltic port."

### Beat 5 — Twist/climax (~9-10s)
**VO:** "To reach it by land from Moscow, Russian citizens once needed special transit documents just to cross through Lithuania's territory."
**Visual:** Wider shot showing a line/route from Moscow through Lithuania into Kaliningrad — Canva: draw a dashed line element or use the "Line" shape with a dash pattern, animate it with "Wipe" so it draws across the map as the line plays.
**On-screen text:** "A passport. To cross to your own city."
**Add:** a small passport/document icon at the Lithuania crossing point.

### Beat 6 — Button/CTA (~13-14s)
**VO:** "One country, one exclave, 200 miles of foreign land in between — and it's still one of Russia's most valuable ports. Follow for more places on Earth that shouldn't exist, but do."
**Visual:** Pull back out to the full regional map, both flags/labels visible, freeze on a clean final frame.
**On-screen text:** "Follow for more 🌍"
**Canva tip:** this is your thumbnail-adjacent frame — make sure the final freeze looks good as a standalone still, since it's what viewers see if they scrub to the end.

---

## 4. Title & description (ready to paste)

**Title:** Russia Has a Piece of Land With No Border to Russia 🇷🇺

**Description:**
This is Russian territory. It shares no land border with the rest of Russia — the closest Russian soil is over 200 miles away.

Welcome to Kaliningrad — wedged between Poland and Lithuania on the Baltic Sea, once the German city of Königsberg, kept by the Soviet Union after World War Two and never given back. It's Russia's only Baltic Sea port that never freezes, making it one of the most strategically valuable pieces of land the country owns. For years, Russian citizens needed special transit documents just to cross through Lithuania to reach it — a passport required to get to their own country's city.

One country, one exclave, 200 miles of foreign land in between — and it's still one of Russia's most valuable ports.

#geography #maps #kaliningrad #russia #exclave #balticsea #geotok #history #education #shorts #fyp #viralmap #funfacts

---

## 5. Applying this to the other scripts

Every file in `scripts/*.md` has the same structure: 6 beats, each with a VO line, an ON-SCREEN TEXT cue, and a one-line VISUAL direction note already written out. To convert any of them the same way:

1. Copy the 6 VO lines into your Canva voiceover step (Section 2).
2. For each beat, read its "VISUAL" note and translate it into a Canva map + icon/marker setup the same way Beat 1-6 above did for Kaliningrad — the script already tells you what should be on screen, you're just building it in Canva's editor instead of code.
3. Reuse the same color palette, font, and transition settings every time — that's what keeps the channel looking consistent across videos, exactly like the automated pipeline's "locked style" did.
4. Titles/descriptions for every scripted day are already written out in full in `video-titles-descriptions.md` — just copy-paste.
