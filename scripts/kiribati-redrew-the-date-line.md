# Script: "This Country Redrew the Map So It Could Share One Calendar Day"

**Format reference:** GeoGlobeTales-style short (map-animation + VO, 60s, YouTube Shorts/TikTok) — Day 26 of 30-day lineup
**Topic:** Kiribati and the 1995 realignment of the International Date Line
**Target length:** ~60 seconds (6 beats x 10s)
**Tone:** Calm, confident, deadpan-surprised narrator. Short declarative sentences.

**VO word-count discipline:** Lines pre-tuned to ~20-25 words each (beat 6 runs longer for the CTA), targeting a natural ~8-10s read per beat. Narrator is Google TTS — normal digit formatting is fine, no need to spell out numbers.

---

## TITLE OPTIONS
1. "This Country Redrew the Map So It Could Share One Calendar Day 🗓️" (primary)
2. "Kiribati Moved the International Date Line to Fix Itself"
3. "The Country That's First to See Every New Day"

---

## SCRIPT (6 x 10s beats)

**Beat 1 — HOOK (0:00–0:10)**
VO: "This country spans more than a thousand miles of Pacific Ocean — so far, its own calendar used to split down the middle."

*VISUAL: Wide push-in over open blue Pacific Ocean, scattered gold island markers appearing far apart across the frame.*
*ON-SCREEN TEXT: "Split by its own calendar."*

**Beat 2 — SETUP (0:10–0:20)**
VO: "It's called Kiribati — dozens of islands stretching from the Gilbert Islands to the Line Islands, almost a third of the way around the globe."

*VISUAL: Map zoom on the western Gilbert Islands, gold marker and label, blue ocean stretching far to the right toward the rest of the country.*
*ON-SCREEN TEXT: "Islands 1,000+ miles apart."*

**Beat 3 — ESCALATION 1 (0:20–0:30)**
VO: "The date line used to run straight through the country, putting its eastern islands a full calendar day behind the west."

*VISUAL: A straight dashed line animating down through open ocean between two island groups, labels flipping between two different weekday names on either side.*
*ON-SCREEN TEXT: "The date line cut it in half."*

**Beat 4 — ESCALATION 2 (0:30–0:40)**
VO: "In 1995, Kiribati simply redrew the map — bending the date line east, around its own islands, so the whole country shared one single day."

*VISUAL: The straight dashed line dissolves as a new bent gold line draws itself eastward in a wide loop around the eastern islands.*
*ON-SCREEN TEXT: "Kiribati redrew the map."*

**Beat 5 — TWIST / CLIMAX (0:40–0:50)**
VO: "Now its easternmost islands sit fourteen hours ahead of New York — making Kiribati the very first place on Earth to greet each new day."

*VISUAL: Zoom on the easternmost Line Islands, sunrise-colored glow animating in over the gold markers first.*
*ON-SCREEN TEXT: "First to see each new day."*

**Beat 6 — BUTTON / CTA (0:50–1:00)**
VO: "One country moved the actual date line just to share a calendar with itself — and now it's the first place on Earth to see tomorrow. Follow for more places on Earth that shouldn't exist, but do."

*VISUAL: Pull back to the full wide Pacific view, the bent date line glowing gold end to end, freeze on title card.*
*ON-SCREEN TEXT: "Follow for more 🌍"*

---

## VISUAL STYLE DIRECTION (continue established look)
- Same blue-water / green-land base palette; Kiribati's islands are too small for the 110m map dataset to render as country polygons, so the entire "gold = subject" language comes from markers and the animated date-line, per the pipeline's "scenes that aren't a country" pattern.
- No single camera bbox ever crosses the antimeridian (confirmed by testing that d3-geo's fitExtent normalizes longitude and breaks otherwise) — Gilbert Islands beats stay on the positive-longitude side, Line Islands beats stay on the negative side, cutting between them like any other beat transition; markers/lines use true real-world longitude throughout since point projection (unlike the camera's bounds fit) handles that correctly on its own.

## PRODUCTION NOTES
- Local zero-cost pipeline: D3 map render + Google TTS narration + burned captions, same locked style key as every other video in the lineup — no per-video visual changes.
- Kiribati (`KI`) is listed in `country-codes.json` but is NOT present in the `world-atlas` 110m countries dataset (confirmed by direct lookup) — `highlight: []` throughout for every beat, with markers/lines carrying the entire visual.
- **Caption/hashtags:**
  `This country redrew the map so it could share one calendar day 🗓️ #geography #maps #kiribati #pacific #internationaldateline #geotok #shorts #fyp`

## WHY THIS TOPIC FITS THE CHANNEL
Same "map anomaly" structure as the rest of the lineup: one concrete visual (a national calendar split by an invisible ocean line), escalating real facts (the west/east day gap, the 1995 redraw), and a twist (being the first place on Earth to see each new day) before the CTA. Day 26 of the 30-day lineup in `content-calendar.md`.
