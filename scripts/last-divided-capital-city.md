# Script: "The Last Divided Capital City in the World"

**Format reference:** GeoGlobeTales-style short (map-animation + VO, 60s, YouTube Shorts/TikTok) — Day 19 of 30-day lineup
**Topic:** Nicosia, Cyprus, split by a UN-patrolled buffer zone since 1974
**Target length:** 60 seconds (6 beats x 10s)
**Tone:** Calm, confident, deadpan-surprised narrator. Short declarative sentences.

**VO word-count discipline:** Lines pre-tuned to ~19-23 words each, targeting a natural ~8-9s read. Narrator engine is Google TTS — normal digit formatting reads correctly.

---

## TITLE OPTIONS
1. "The Last Divided Capital City in the World 🏙️" (primary)
2. "This Capital Has Been Cut in Half Since 1974"
3. "There's an Abandoned Airport Frozen in Time Inside This City"

---

## SCRIPT (6 x 10s beats)

**Beat 1 — HOOK (0:00–0:10)**
VO: "This capital city has been cut in half since 1974, and the line running through it hasn't moved since."
*VISUAL: Camera pushes into a city marker split by a gold dashed line running straight through it.*
*ON-SCREEN TEXT: "Cut in half since 1974."*

**Beat 2 — SETUP (0:10–0:20)**
VO: "It's Nicosia, Cyprus — split by a UN-patrolled buffer zone, the Republic of Cyprus to the south, Turkish-controlled territory to the north."
*VISUAL: Map zoom on Cyprus, gold line dividing the island roughly east-west, Nicosia marked at the split point.*
*ON-SCREEN TEXT: "Split, north and south, by the UN."*

**Beat 3 — ESCALATION 1 (0:20–0:30)**
VO: "It's the only capital city on Earth still divided by a hard international border — every other divided capital eventually reunified."
*VISUAL: Marker on Nicosia glowing gold, a small crown or capital-icon fading in beside the buffer-zone line.*
*ON-SCREEN TEXT: "The last divided capital on Earth."*

**Beat 4 — ESCALATION 2 (0:30–0:40)**
VO: "The buffer zone runs directly through the old city, so a checkpoint sits in the middle of what used to be an ordinary shopping street."
*VISUAL: Zoomed street-level marker with a checkpoint-barrier icon straddling the dashed line.*
*ON-SCREEN TEXT: "A checkpoint. In the middle of the street."*

**Beat 5 — TWIST / CLIMAX (0:40–0:50)**
VO: "Inside that buffer zone sits an entire abandoned airport, untouched since 1974 — an old airliner is still parked on its runway."
*VISUAL: Marker at an airport icon inside the buffer zone, a small plane icon frozen in place beside it.*
*ON-SCREEN TEXT: "An airport frozen since 1974."*

**Beat 6 — BUTTON / CTA (0:50–1:00)**
VO: "One capital, one line, over 50 years unmoved — and a whole airport still waiting for flights that never came back. Follow for more places on Earth that shouldn't exist, but do."
*VISUAL: Pull back to full map of Cyprus, gold dividing line across the island, freeze on title card.*
*ON-SCREEN TEXT: "Follow for more 🌍"*

---

## VISUAL STYLE DIRECTION (continue established look)
- Same blue-water / green-land classic map palette locked across the series.
- Cyprus is a real country polygon (`highlight: ["CY"]`), so the island itself renders normally; the north/south split and the buffer zone are drawn as a `lines` entry (a rough east-west line across the island through Nicosia) since the pipeline's map data has no separate polygon for the Turkish-controlled north or the UN buffer zone.

## PRODUCTION NOTES (cost-conscious)
- Reuse the locked style-key and narrator voice — do not rebuild.
- VO lines pre-tuned to ~19-23 words to minimize regeneration retries.
- Skip thumbnail generation to save credits.
- **Caption/hashtags:**
  `The last divided capital city in the world 🏙️ #geography #maps #nicosia #cyprus #geotok #history #education #shorts #fyp #viralmap #funfacts`

## WHY THIS TOPIC FITS THE CHANNEL
Same "map anomaly" structure: one concrete visual (a capital city split by a hard border), escalating real facts (the last divided capital on Earth, a checkpoint mid-street), and a genuinely eerie twist (a whole airport frozen in time since 1974) before the CTA. Day 19 of the lineup in `content-calendar.md`.
