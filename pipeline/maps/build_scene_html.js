/**
 * maps/build_scene_html.js
 *
 * The Node/D3 module for the pipeline. Given ONE scene spec (a single ~10s
 * beat: highlighted country/ies, a pan/zoom camera path, optional markers
 * and animated lines, and on-screen caption text), produces a single
 * self-contained HTML file. Playwright loads that file and records it as
 * video (see ../render_scene.js).
 *
 * Design choice: D3 (d3-geo's geoMercator/geoPath/fitExtent) is used HERE,
 * server-side in Node, to convert the world-atlas 110m TopoJSON into plain
 * GeoJSON and to compute exact projection parameters (scale/translate) for
 * each camera keyframe from a lon/lat bounding box. The real d3.js UMD
 * bundle is then inlined verbatim into the page (no CDN, no network) so the
 * SAME real d3 projection math re-renders every animation frame in-browser
 * as the camera interpolates between keyframes -- no hand-rolled
 * reimplementation of Mercator math, no bundler.
 */
"use strict";
const fs = require("fs");
const path = require("path");
const d3 = require("d3");
const topojson = require("topojson-client");

const PKG_ROOT = path.resolve(__dirname, "..");
const STYLE = JSON.parse(fs.readFileSync(path.join(PKG_ROOT, "config", "style.json"), "utf8"));
const COUNTRY_CODES = JSON.parse(fs.readFileSync(path.join(__dirname, "country-codes.json"), "utf8"));
const D3_BUNDLE = fs.readFileSync(path.join(PKG_ROOT, "node_modules", "d3", "dist", "d3.js"), "utf8");

const WORLD_TOPO = require(path.join(PKG_ROOT, "node_modules", "world-atlas", "countries-110m.json"));

// Precompute once: land as GeoJSON, countries as GeoJSON (with numeric ids),
// and an interior-border mesh (a-b country seams only, not coastlines).
const LAND_GEOJSON = topojson.feature(WORLD_TOPO, WORLD_TOPO.objects.land);
const COUNTRIES_GEOJSON = topojson.feature(WORLD_TOPO, WORLD_TOPO.objects.countries);
const BORDER_MESH = topojson.mesh(WORLD_TOPO, WORLD_TOPO.objects.countries, (a, b) => a !== b);

function alpha2ToNumericId(code) {
  const id = COUNTRY_CODES[code.toUpperCase()];
  if (id === undefined) {
    throw new Error(`Unknown country code "${code}" -- add it to maps/country-codes.json`);
  }
  // world-atlas topology ids are zero-padded 3-digit ISO 3166-1 numeric
  // strings (e.g. Azerbaijan is "031", not "31") -- pad so 1-2 digit
  // numeric codes (Andorra, Armenia, Azerbaijan, Austria, Belgium,
  // Australia, Brazil, Argentina, ...) still match.
  return String(id).padStart(3, "0");
}

/** Compute {scale, translate} for a lon/lat bbox via a real d3 fitExtent, so
 * the browser can just plug scale+translate into geoMercator() directly. */
function fitBBoxProjection(bbox, width, height, padPx) {
  const [[west, south], [east, north]] = bbox;
  // NOTE: d3-geo's spherical winding convention is the opposite of the
  // GeoJSON/RFC7946 "CCW exterior ring" rule -- a ring that looks
  // counter-clockwise in plain lon/lat x-y actually reads as "the rest of
  // the sphere minus this rectangle" to d3-geo. This order (clockwise in
  // lon/lat x-y) is the one that keeps the ring's enclosed area small.
  const ring = [
    [west, south], [west, north], [east, north], [east, south], [west, south],
  ];
  const feature = { type: "Feature", geometry: { type: "Polygon", coordinates: [ring] } };
  const proj = d3.geoMercator().fitExtent(
    [[padPx, padPx], [width - padPx, height - padPx]],
    feature
  );
  return { scale: proj.scale(), translate: proj.translate() };
}

/**
 * scene = {
 *   duration,                     // seconds, REQUIRED (matches measured VO audio)
 *   highlight: ["RU"],            // alpha-2 codes to gold-outline
 *   camera: {
 *     from: [[west,south],[east,north]],   // lon/lat bbox at t=0
 *     to:   [[west,south],[east,north]],   // lon/lat bbox at t=duration
 *     pad: 90                               // px padding, optional
 *   },
 *   markers: [ { lonlat:[lon,lat], label:"Moscow", emoji:"📍", showAt:0.15 } ],
 *   lines:   [ { points:[[lon,lat],...], dashed:true, showAt:0.2, drawDuration:0.6 } ],
 *   onScreenText: "200 miles from the rest of Russia.",
 *   onScreenTextShowAt: 0.12       // fraction of duration
 * }
 */
function buildSceneHTML(scene) {
  const { width, height } = STYLE.video;
  const pad = (scene.camera && scene.camera.pad) || 110;

  const camFrom = fitBBoxProjection(scene.camera.from, width, height, pad);
  const camTo = fitBBoxProjection(scene.camera.to, width, height, pad);

  const highlightIds = (scene.highlight || []).map(alpha2ToNumericId);
  const highlightFeatures = COUNTRIES_GEOJSON.features.filter((f) =>
    highlightIds.includes(String(f.id))
  );

  const payload = {
    style: STYLE,
    land: LAND_GEOJSON,
    borders: BORDER_MESH,
    highlight: { type: "FeatureCollection", features: highlightFeatures },
    camFrom,
    camTo,
    duration: scene.duration,
    markers: scene.markers || [],
    lines: scene.lines || [],
    onScreenText: scene.onScreenText || "",
    onScreenTextShowAt: scene.onScreenTextShowAt != null ? scene.onScreenTextShowAt : 0.12,
    dateStamp: scene.dateStamp || null,
  };

  return renderTemplate(payload);
}

function renderTemplate(payload) {
  const { width, height } = payload.style.video;
  const c = payload.style.colors;
  const fonts = payload.style.fonts;
  const diag = Math.hypot(width, height);

  return `<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
  html,body { margin:0; padding:0; background:${c.background}; overflow:hidden; }
  #stage { width:${width}px; height:${height}px; position:relative; }
  svg { position:absolute; top:0; left:0; }
  .on-screen-text {
    position:absolute;
    top: 9%;
    left: 6%;
    right: 6%;
    font-family: ${fonts.onScreenTextFamily};
    font-weight: 800;
    font-size: 58px;
    line-height: 1.22;
    letter-spacing: 0.3px;
    color: ${c.onScreenTextColor};
    text-shadow: 0 3px 0 ${c.onScreenTextShadow}, 0 0 26px ${c.onScreenTextShadow}, 0 6px 18px ${c.onScreenTextShadow};
    opacity: 0;
    transition: opacity 0.55s ease, transform 0.55s cubic-bezier(.2,1.4,.4,1);
    transform: translateY(14px) scale(0.97);
  }
  .on-screen-text.show { opacity: 1; transform: translateY(0) scale(1); }
  .marker-label {
    font-family: ${fonts.onScreenTextFamily};
    font-weight: 700;
    font-size: 25px;
    fill: ${c.markerText};
  }
  #vignette, #grain, #grade { pointer-events:none; }
</style>
</head>
<body>
<div id="stage">
  <svg id="map" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
    <defs>
      <radialGradient id="oceanGrad" cx="42%" cy="38%" r="75%">
        <stop offset="0%" stop-color="${c.waterLight}"></stop>
        <stop offset="55%" stop-color="${c.water}"></stop>
        <stop offset="100%" stop-color="${c.waterDark}"></stop>
      </radialGradient>
      <linearGradient id="landGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="${c.landLight}"></stop>
        <stop offset="55%" stop-color="${c.land}"></stop>
        <stop offset="100%" stop-color="${c.landDark}"></stop>
      </linearGradient>
      <linearGradient id="highlightGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="${c.highlightStroke}"></stop>
        <stop offset="100%" stop-color="${c.highlight}"></stop>
      </linearGradient>
      <filter id="landShadow" x="-20%" y="-20%" width="140%" height="140%">
        <feDropShadow dx="0" dy="6" stdDeviation="10" flood-color="#000000" flood-opacity="0.35"></feDropShadow>
      </filter>
      <filter id="softGlow" x="-60%" y="-60%" width="220%" height="220%">
        <feGaussianBlur stdDeviation="7" result="blur"></feGaussianBlur>
        <feMerge>
          <feMergeNode in="blur"></feMergeNode>
          <feMergeNode in="SourceGraphic"></feMergeNode>
        </feMerge>
      </filter>
      <filter id="badgeShadow" x="-40%" y="-40%" width="180%" height="180%">
        <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#000000" flood-opacity="0.45"></feDropShadow>
      </filter>
      <filter id="grainFilter" x="0" y="0" width="100%" height="100%">
        <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7" stitchTiles="stitch" result="noise"></feTurbulence>
        <feColorMatrix in="noise" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.5 0"></feColorMatrix>
      </filter>
      <radialGradient id="vignetteGrad" cx="50%" cy="46%" r="72%">
        <stop offset="55%" stop-color="#000000" stop-opacity="0"></stop>
        <stop offset="100%" stop-color="#000000" stop-opacity="1"></stop>
      </radialGradient>
      <linearGradient id="gradeGrad" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="${c.highlightStroke}" stop-opacity="0.10"></stop>
        <stop offset="45%" stop-color="#000000" stop-opacity="0"></stop>
        <stop offset="100%" stop-color="${c.waterDark}" stop-opacity="0.16"></stop>
      </linearGradient>
    </defs>
    <rect id="ocean" x="0" y="0" width="${width}" height="${height}" fill="url(#oceanGrad)"></rect>
    <path id="land" fill="url(#landGrad)" filter="url(#landShadow)"></path>
    <path id="borders" fill="none" stroke="${c.countryBorder}" stroke-width="1.4" stroke-linejoin="round"></path>
    <g id="highlight" fill="url(#landGrad)" stroke="url(#highlightGrad)" stroke-width="6" filter="url(#softGlow)"></g>
    <g id="lines"></g>
    <g id="markers"></g>
    <rect id="grade" x="0" y="0" width="${width}" height="${height}" fill="url(#gradeGrad)" style="mix-blend-mode:soft-light"></rect>
    <rect id="grain" x="0" y="0" width="${width}" height="${height}" filter="url(#grainFilter)" opacity="${c.grainOpacity}" style="mix-blend-mode:overlay"></rect>
    <rect id="vignette" x="0" y="0" width="${width}" height="${height}" fill="url(#vignetteGrad)" opacity="0.55"></rect>
  </svg>
  <div class="on-screen-text" id="onScreenText"></div>
</div>

<script>window.__D3_BUNDLE_INLINE__ = true;</script>
<script>
${D3_BUNDLE}
</script>
<script id="payload" type="application/json">${JSON.stringify(payload)}</script>
<script>
(function () {
  const payload = JSON.parse(document.getElementById("payload").textContent);
  const W = ${width}, H = ${height};
  const svg = d3.select("#map");
  const landPath = document.getElementById("land");
  const bordersPath = document.getElementById("borders");
  const highlightG = d3.select("#highlight");
  const linesG = d3.select("#lines");
  const markersG = d3.select("#markers");
  const onScreenTextEl = document.getElementById("onScreenText");
  onScreenTextEl.textContent = payload.onScreenText;

  function lerp(a, b, t) { return a + (b - a) * t; }
  function lerpLog(a, b, t) { return Math.exp(lerp(Math.log(a), Math.log(b), t)); }
  function easeInOutCubic(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
  // Gentler than cubic: a sine-based ease has much less "slam to a stop" at
  // t=0/t=1, which matters a lot here because every beat's camera motion
  // starts and ends AT a beat boundary -- cubic easing made the camera visibly
  // decelerate to a near-halt right before every cut, then re-accelerate hard
  // right after, reading as a stutter even when position was continuous.
  function easeInOutSine(t) { return -(Math.cos(Math.PI * t) - 1) / 2; }
  function easeOutBack(t) {
    const c1 = 1.70158, c3 = c1 + 1;
    return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
  }

  // Truncate an already-projected [x,y] polyline to the given fraction of
  // its total pixel length, interpolating the cut point -- used for the
  // line "draw-on" reveal. (Deliberately NOT using SVG pathLength-relative
  // dashoffset: that unit system fights with a real, small-px dash pattern
  // for the "dashed" visual style, so the two effects are kept separate.)
  function truncateByFraction(pts, frac) {
    if (pts.length < 2 || frac <= 0) return pts.length ? [pts[0]] : [];
    if (frac >= 1) return pts;
    const segLens = [];
    let total = 0;
    for (let i = 1; i < pts.length; i++) {
      const l = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
      segLens.push(l);
      total += l;
    }
    const target = total * frac;
    const out = [pts[0]];
    let acc = 0;
    for (let i = 1; i < pts.length; i++) {
      const segLen = segLens[i - 1];
      if (acc + segLen < target) {
        out.push(pts[i]);
        acc += segLen;
        continue;
      }
      const t = segLen > 0 ? (target - acc) / segLen : 0;
      out.push([
        pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * t,
        pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * t,
      ]);
      break;
    }
    return out;
  }

  const highlightSel = highlightG.selectAll("path")
    .data(payload.highlight.features)
    .join("path");

  const lineSel = linesG.selectAll("path")
    .data(payload.lines)
    .join("path")
    .attr("fill", "none")
    .attr("stroke", payload.style.colors.lineColor)
    .attr("stroke-width", 5)
    .attr("stroke-linecap", "round")
    .attr("stroke-dasharray", (d) => (d.dashed ? "14 10" : null))
    .attr("opacity", 0);

  const markerSel = markersG.selectAll("g.marker")
    .data(payload.markers)
    .join("g")
    .attr("class", "marker");
  markerSel.append("circle")
    .attr("class", "marker-dot")
    .attr("r", 9)
    .attr("fill", payload.style.colors.markerFill)
    .attr("stroke", "#ffffff")
    .attr("stroke-width", 2.5)
    .attr("filter", "url(#badgeShadow)");
  const badgeSel = markerSel.append("g").attr("class", "badge").attr("transform", "translate(0,-38)");
  badgeSel.append("rect")
    .attr("class", "badge-rect")
    .attr("rx", 12).attr("ry", 12)
    .attr("fill", payload.style.colors.markerFill)
    .attr("filter", "url(#badgeShadow)");
  badgeSel.append("text")
    .attr("class", "marker-label")
    .attr("text-anchor", "middle")
    .attr("dominant-baseline", "middle")
    .text((d) => (d.emoji ? d.emoji + "  " : "") + (d.label || "").toUpperCase());

  // Size each badge's pill to its actual rendered text (real DOM layout, so
  // this is exact regardless of label length -- no manual width guessing).
  badgeSel.each(function () {
    const g = d3.select(this);
    const textNode = g.select("text").node();
    const bbox = textNode.getBBox();
    const padX = 20, padY = 12;
    g.select("rect")
      .attr("x", bbox.x - padX)
      .attr("y", bbox.y - padY)
      .attr("width", bbox.width + padX * 2)
      .attr("height", bbox.height + padY * 2);
  });

  function currentProjection(t) {
    const scale = lerpLog(payload.camFrom.scale, payload.camTo.scale, t);
    const tx = lerp(payload.camFrom.translate[0], payload.camTo.translate[0], t);
    const ty = lerp(payload.camFrom.translate[1], payload.camTo.translate[1], t);
    return d3.geoMercator().scale(scale).translate([tx, ty]);
  }

  function draw(elapsedSec) {
    const dur = payload.duration;
    const rawT = Math.min(1, Math.max(0, elapsedSec / dur));
    const t = easeInOutSine(rawT);
    const projection = currentProjection(t);
    const path = d3.geoPath(projection);

    landPath.setAttribute("d", path(payload.land));
    bordersPath.setAttribute("d", path(payload.borders));
    highlightSel.attr("d", (d) => path(d));

    lineSel
      .attr("d", function (d) {
        const projPts = d.points.map((p) => projection(p)).filter(Boolean);
        const showAt = d.showAt || 0;
        const drawDur = d.drawDuration || 0.5;
        const localT = Math.min(1, Math.max(0, (rawT - showAt) / drawDur));
        const truncated = truncateByFraction(projPts, localT);
        return truncated.length > 1 ? d3.line()(truncated) : null;
      })
      .attr("opacity", (d) => (rawT >= (d.showAt || 0) ? 1 : 0));

    markerSel
      .attr("transform", (d) => {
        const p = projection(d.lonlat);
        if (!p) return "translate(-9999,-9999)";
        const showAt = d.showAt || 0;
        const popDur = 0.4;
        const localT = Math.min(1, Math.max(0, (rawT - showAt) / popDur));
        const scale = rawT >= showAt ? easeOutBack(localT) : 0;
        return "translate(" + p[0] + "," + p[1] + ") scale(" + Math.max(0, scale) + ")";
      })
      .attr("opacity", (d) => (rawT >= (d.showAt || 0) ? 1 : 0));

    if (payload.onScreenText && rawT >= payload.onScreenTextShowAt) {
      onScreenTextEl.classList.add("show");
    }
  }

  draw(0);

  let startTs = null;
  function frame(ts) {
    if (startTs === null) startTs = ts;
    const elapsedSec = (ts - startTs) / 1000;
    draw(elapsedSec);
    if (elapsedSec < payload.duration + 0.5) {
      requestAnimationFrame(frame);
    }
  }
  requestAnimationFrame(frame);

  window.__sceneReady = true;
})();
</script>
</body>
</html>
`;
}

module.exports = { buildSceneHTML, fitBBoxProjection, alpha2ToNumericId };

// CLI usage: node build_scene_html.js <scene.json> <out.html>
if (require.main === module) {
  const [sceneJsonPath, outHtmlPath] = process.argv.slice(2);
  if (!sceneJsonPath || !outHtmlPath) {
    console.error("Usage: node build_scene_html.js <scene.json> <out.html>");
    process.exit(1);
  }
  const scene = JSON.parse(fs.readFileSync(sceneJsonPath, "utf8"));
  const html = buildSceneHTML(scene);
  fs.writeFileSync(outHtmlPath, html);
  console.log(JSON.stringify({ out: outHtmlPath }));
}
