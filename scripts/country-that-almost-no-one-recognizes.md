# Script: "The Country That Exists but Almost No One Recognizes"

**Format reference:** GeoGlobeTales-style short (map-animation + VO, 60s, YouTube Shorts/TikTok) — Day 18 of 30-day lineup
**Topic:** Transnistria, a self-governing breakaway strip of land between Moldova and Ukraine, recognized by no UN member state
**Target length:** 60 seconds (6 beats x 10s)
**Tone:** Calm, confident, deadpan-surprised narrator. Short declarative sentences.

**VO word-count discipline:** Lines pre-tuned to ~19-23 words each, targeting a natural ~8-9s read. Narrator engine is Google TTS — normal digit formatting reads correctly.

---

## TITLE OPTIONS
1. "The Country That Exists but Almost No One Recognizes 🏳️" (primary)
2. "This Country Never Actually Left the USSR"
3. "Cross This Border and Your Currency Changes — to a Country That Doesn't Officially Exist"

---

## SCRIPT (6 x 10s beats)

**Beat 1 — HOOK (0:00–0:10)**
VO: "This country has its own government, its own currency, its own army, and its own border checkpoints — and almost no nation recognizes it exists."
*VISUAL: Camera pushes into a narrow strip of land inside Moldova, a gold dashed outline tracing the strip along a river.*
*ON-SCREEN TEXT: "A country almost nobody recognizes."*

**Beat 2 — SETUP (0:10–0:20)**
VO: "It's called Transnistria — a narrow strip that broke away from Moldova in 1990 and has governed itself ever since."
*VISUAL: Map zoom labeling Transnistria in gold along the Dniester River, green Moldova and Ukraine bordering it on both sides.*
*ON-SCREEN TEXT: "Broke away from Moldova in 1990."*

**Beat 3 — ESCALATION 1 (0:20–0:30)**
VO: "It's recognized by no United Nations member state — not one country on Earth officially accepts it as sovereign."
*VISUAL: Marker at Tiraspol with a small question-mark flag icon, gold outline pulsing along the strip's border.*
*ON-SCREEN TEXT: "Recognized by zero UN members."*

**Beat 4 — ESCALATION 2 (0:30–0:40)**
VO: "Cross into it and your currency changes, your passport gets an unofficial stamp, and even your phone signal switches networks."
*VISUAL: Border-crossing icon animating across the boundary line, small currency and signal icons flickering on either side.*
*ON-SCREEN TEXT: "Cross the line. Everything changes."*

**Beat 5 — TWIST / CLIMAX (0:40–0:50)**
VO: "Its flag still carries the hammer and sickle, and statues of Lenin still stand in its capital — this is a country that never left the USSR."
*VISUAL: Marker at Tiraspol with a hammer-and-sickle style icon, a faded red tint briefly washing over the marker area.*
*ON-SCREEN TEXT: "Never actually left the USSR."*

**Beat 6 — BUTTON / CTA (0:50–1:00)**
VO: "A government, a currency, an army, and a border — for a country that, on paper, isn't supposed to be there at all. Follow for more places on Earth that shouldn't exist, but do."
*VISUAL: Pull back to full map — gold Transnistria strip along the river, Moldova and Ukraine on either side, freeze on title card.*
*ON-SCREEN TEXT: "Follow for more 🌍"*

---

## VISUAL STYLE DIRECTION (continue established look)
- Same blue-water / green-land classic map palette locked across the series.
- Transnistria is a breakaway region of Moldova, not its own polygon in `country-codes.json`/world-atlas, so `highlight: ["MD"]` gives Moldova for context and a hand-drawn `lines` loop (a narrow strip along the Dniester River, roughly Camenca in the north to Tiraspol/Slobozia in the south) plus a marker at Tiraspol stand in for the territory, per the README's "scenes that aren't a country" pattern — same convention used for Nagorno-Karabakh.

## PRODUCTION NOTES (cost-conscious)
- Reuse the locked style-key and narrator voice — do not rebuild.
- VO lines pre-tuned to ~19-23 words to minimize regeneration retries.
- Skip thumbnail generation to save credits.
- **Caption/hashtags:**
  `The country that exists but almost no one recognizes 🏳️ #geography #maps #transnistria #moldova #geotok #history #education #shorts #fyp #viralmap #funfacts`

## WHY THIS TOPIC FITS THE CHANNEL
Same "map anomaly" structure: one concrete visual (a self-governing strip of land with its own everything, tucked inside Moldova), escalating real facts (zero UN recognition, the currency/signal switch at the border), and a genuinely strange twist (Soviet symbols still in daily use) before the CTA. Day 18 of the lineup in `content-calendar.md`.
