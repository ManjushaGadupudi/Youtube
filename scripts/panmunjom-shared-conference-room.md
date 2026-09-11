# Script: "Two Countries Share One Room — Literally"

**Format reference:** GeoGlobeTales-style short (map-animation + VO, 60s, YouTube Shorts/TikTok) — Day 23 of 30-day lineup
**Topic:** Panmunjom / the Joint Security Area (JSA), Korean DMZ
**Target length:** ~60 seconds (6 beats x 10s)
**Tone:** Calm, confident, deadpan-surprised narrator. Short declarative sentences.

**VO word-count discipline:** Lines pre-tuned to ~19-25 words each (beat 6 runs longer for the CTA), targeting a natural ~8-10s read per beat. Narrator is Google TTS — normal digit formatting is fine, no need to spell out numbers.

---

## TITLE OPTIONS
1. "Two Countries Share One Room — Literally 🇰🇵🇰🇷" (primary)
2. "This Table Is Split Between North and South Korea"
3. "You Can Stand in Two Countries at Once, Right Here"

---

## SCRIPT (6 x 10s beats)

**Beat 1 — HOOK (0:00–0:10)**
VO: "Walk into this building, and you can stand in North Korea and South Korea in the very same room."

*VISUAL: Push-in over the Korean peninsula toward a small cluster of blue buildings sitting exactly on the DMZ line.*
*ON-SCREEN TEXT: "Stand in two countries at once."*

**Beat 2 — SETUP (0:10–0:20)**
VO: "This is Panmunjom, the Joint Security Area inside the Korean DMZ — the one spot where both militaries stand face to face."

*VISUAL: Map zoom labeling North Korea and South Korea on either side of a thin dashed DMZ line, JSA marker glowing gold at the center.*
*ON-SCREEN TEXT: "The Joint Security Area."*

**Beat 3 — ESCALATION 1 (0:20–0:30)**
VO: "Inside the blue conference huts, the Military Demarcation Line runs directly across the meeting table, splitting it exactly in half."

*VISUAL: Extreme zoom on a single building marker, a thin gold line animating straight through it left to right.*
*ON-SCREEN TEXT: "The line splits the table."*

**Beat 4 — ESCALATION 2 (0:30–0:40)**
VO: "Step to the wrong side of that table, and you've technically crossed an international border without ever leaving the room."

*VISUAL: Same tight building marker, small footprint icon stepping across the gold line inside the outline of the hut.*
*ON-SCREEN TEXT: "One step, one border."*

**Beat 5 — TWIST / CLIMAX (0:40–0:50)**
VO: "North and South Korea never signed a peace treaty. The 1953 armistice only paused the war — this room sits on a frozen frontline."

*VISUAL: Pull back slightly to the DMZ strip, soldier-icon markers on both sides facing each other across the line.*
*ON-SCREEN TEXT: "Still technically at war."*

**Beat 6 — BUTTON / CTA (0:50–1:00)**
VO: "One room, one table, two countries technically still at war — and tourists can stand on either side of the line. Follow for more places on Earth that shouldn't exist, but do."

*VISUAL: Pull back to the full Korean peninsula, DMZ line glowing gold end to end, freeze on title card.*
*ON-SCREEN TEXT: "Follow for more 🌍"*

---

## VISUAL STYLE DIRECTION (continue established look)
- Same blue-water / green-land base palette locked across the series; the JSA has no country polygon of its own, so the "gold = subject" language comes entirely from markers and the animated demarcation line, not a highlighted landmass.
- North Korea and South Korea are labeled via plain markers on either side of the DMZ, never gold-highlighted themselves — the line between them is the story.

## PRODUCTION NOTES
- Local zero-cost pipeline: D3 map render + Google TTS narration + burned captions, same locked style key as every other video in the lineup — no per-video visual changes.
- JSA/Panmunjom is a specific building, not a country in the map dataset — `highlight: []` throughout, with markers/lines carrying the visual weight per the pipeline's "scenes that aren't a country" pattern.
- **Caption/hashtags:**
  `Two countries share one room — literally 🇰🇵🇰🇷 #geography #maps #panmunjom #dmz #korea #geotok #history #shorts #fyp`

## WHY THIS TOPIC FITS THE CHANNEL
Same "map anomaly" structure as the rest of the lineup: one concrete visual (a conference table split exactly in half by an international border), escalating real facts (the armistice, the frozen war), and a human-scale twist (a single step across a table counts as crossing a border) before the CTA. Day 23 of the 30-day lineup in `content-calendar.md`.
