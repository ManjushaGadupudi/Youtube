# Script: "The Highest Border Crossing on Earth Shuts Down for Winter"

**Format reference:** GeoGlobeTales-style short (map-animation + VO, 60s, YouTube Shorts/TikTok) — Day 29 of 30-day lineup
**Topic:** The Khunjerab Pass, Pakistan-China border, Karakoram Highway
**Target length:** ~60 seconds (6 beats x 10s)
**Tone:** Calm, confident, deadpan-surprised narrator. Short declarative sentences.

**VO word-count discipline:** Lines pre-tuned to ~20-25 words each (beat 6 runs longer for the CTA), targeting a natural ~8-10s read per beat. Narrator is Google TTS — normal digit formatting is fine, no need to spell out numbers.

---

## TITLE OPTIONS
1. "The Highest Border Crossing on Earth Shuts Down for Winter 🏔️" (primary)
2. "This Border Sits at 15,397 Feet — and Freezes Shut"
3. "The World's Highest Paved Border Closes Every Winter"

---

## SCRIPT (6 x 10s beats)

**Beat 1 — HOOK (0:00–0:10)**
VO: "At over 15,000 feet, this is the highest paved international border crossing anywhere on Earth — and for months each year, it's completely buried in snow."

*VISUAL: Push-in over jagged mountain terrain toward a small road winding up to a high pass between two countries.*
*ON-SCREEN TEXT: "15,397 feet. Buried in snow."*

**Beat 2 — SETUP (0:10–0:20)**
VO: "It's called the Khunjerab Pass, connecting Pakistan and China through the Karakoram Mountains, at nearly 4,700 meters above sea level."

*VISUAL: Map zoom on the Karakoram range, gold marker at the pass, Pakistan and China labeled on either side of the border.*
*ON-SCREEN TEXT: "Highest border crossing on Earth."*

**Beat 3 — ESCALATION 1 (0:20–0:30)**
VO: "The altitude is so extreme that altitude sickness is a real risk just from standing at the checkpoint, before you've even crossed the border."

*VISUAL: Extreme zoom on the pass marker, a small warning-icon pulsing beside it, thin-air haze effect over the terrain.*
*ON-SCREEN TEXT: "Altitude sickness at the checkpoint."*

**Beat 4 — ESCALATION 2 (0:30–0:40)**
VO: "Under a 1985 agreement, the pass only stays open from April through November, the rest of the year, snow makes it physically impassable."

*VISUAL: Animated route line along the Karakoram Highway through the pass, snow texture fading in over it and the line dimming.*
*ON-SCREEN TEXT: "Open April–November only."*

**Beat 5 — TWIST / CLIMAX (0:40–0:50)**
VO: "When it reopens each spring, it's briefly one of the most remote functioning borders anyone can actually drive across, before winter shuts it again."

*VISUAL: Snow texture melting away from the route line, the highway glowing gold end to end as it reopens.*
*ON-SCREEN TEXT: "Reopens every spring."*

**Beat 6 — BUTTON / CTA (0:50–1:00)**
VO: "A road so high the mountains themselves close it for half the year, and it still reopens, every single spring. Follow for more places on Earth that shouldn't exist, but do."

*VISUAL: Pull back to the full Pakistan-China border region, the highway glowing gold across the pass, freeze on title card.*
*ON-SCREEN TEXT: "Follow for more 🌍"*

---

## VISUAL STYLE DIRECTION (continue established look)
- Same blue-water / green-land base palette; Pakistan and China are both gold-highlighted throughout, with the Karakoram Highway itself carried by an animated `lines` route through the pass.
- Snow/altitude details (haze, snow texture) are described as visual direction only — the renderer keeps the same locked style key; these read as simple color/texture cues within that palette, not new assets.

## PRODUCTION NOTES
- Local zero-cost pipeline: D3 map render + Google TTS narration + burned captions, same locked style key as every other video in the lineup — no per-video visual changes.
- `highlight: ["PK", "CN"]` throughout — both codes confirmed present in `country-codes.json` and the `world-atlas` 110m dataset; Khunjerab Pass itself (~36.85°N, 75.42°E, verified via WebSearch) is carried by a marker + route line, not a polygon of its own.
- **Caption/hashtags:**
  `The highest border crossing on Earth shuts down for winter 🏔️ #geography #maps #khunjerabpass #pakistan #china #geotok #shorts #fyp`

## WHY THIS TOPIC FITS THE CHANNEL
Same "map anomaly" structure as the rest of the lineup: one concrete visual (a border crossing higher than most mountains), escalating real facts (altitude sickness risk, the seasonal closure), and a twist (a border that reopens every spring like clockwork) before the CTA. Day 29 of the 30-day lineup in `content-calendar.md`.
