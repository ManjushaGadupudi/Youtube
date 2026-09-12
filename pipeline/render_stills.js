#!/usr/bin/env node
/**
 * render_stills.js — export one clean static PNG background per beat of a
 * scene-spec JSON, for feeding into Canva (or any other manual editor)
 * instead of rendering a full video locally.
 *
 * Reuses the exact same map renderer as the video pipeline (maps/build_scene_html.js)
 * -- same locked colors, gradients, terrain texture, extrude effect on the
 * highlighted country, grain, vignette -- so these stills match the same
 * visual identity as everything already rendered. Deliberately OMITS the
 * animated on-screen headline text (leaves that as blank), since the point
 * is to hand Canva a clean backdrop and let its own text tools/animations
 * own that layer -- baking in text here would just mean redoing it in Canva
 * anyway. Markers, lines, and the highlighted country ARE baked in (those
 * are the hard-to-recreate-by-hand parts), captured in their fully-settled
 * end state (all pop-in animations complete, camera at its `to` position).
 *
 * Usage:
 *   node render_stills.js <scene-spec.json> <out-dir>
 *
 * Writes <out-dir>/beat1.png .. beatN.png, one per beat in the spec.
 */
"use strict";
const fs = require("fs");
const os = require("os");
const path = require("path");
const { chromium } = require("playwright");
const { buildSceneHTML } = require("./maps/build_scene_html.js");

const PKG_ROOT = __dirname;
const STYLE = JSON.parse(fs.readFileSync(path.join(PKG_ROOT, "config", "style.json"), "utf8"));

const SETTLE_SEC = 3; // fake "duration" long enough for every marker/line pop-in to finish

async function renderStill(beat, outPng, browser) {
  const { width, height } = STYLE.video;
  const scene = {
    duration: SETTLE_SEC,
    highlight: beat.highlight || [],
    camera: beat.camera,
    markers: beat.markers || [],
    lines: beat.lines || [],
    onScreenText: "", // deliberately blank -- add text in Canva instead
    onScreenTextShowAt: 0,
  };
  const html = buildSceneHTML(scene);
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "still-"));
  const htmlPath = path.join(tmpDir, "scene.html");
  fs.writeFileSync(htmlPath, html);

  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
  try {
    await page.goto("file://" + htmlPath);
    await page.waitForFunction("window.__sceneReady === true", { timeout: 5000 });
    // Wait past SETTLE_SEC so the camera is at rest at `camera.to` and every
    // marker/line's pop-in/draw-on animation has fully completed.
    await page.waitForTimeout(SETTLE_SEC * 1000 + 300);
    fs.mkdirSync(path.dirname(outPng), { recursive: true });
    await page.screenshot({ path: outPng });
  } finally {
    await page.close();
    fs.rmSync(tmpDir, { recursive: true, force: true });
  }
}

async function main() {
  const [specPath, outDir] = process.argv.slice(2);
  if (!specPath || !outDir) {
    console.error("Usage: node render_stills.js <scene-spec.json> <out-dir>");
    process.exit(1);
  }
  const spec = JSON.parse(fs.readFileSync(specPath, "utf8"));
  const beats = spec.beats;
  if (!Array.isArray(beats) || beats.length === 0) {
    throw new Error("scene-spec JSON must have a non-empty `beats` array");
  }

  const browser = await chromium.launch({
    executablePath: process.env.PW_CHROMIUM || "/opt/pw-browsers/chromium",
  });
  const outputs = [];
  try {
    for (let i = 0; i < beats.length; i++) {
      const n = i + 1;
      const outPng = path.join(outDir, `beat${n}.png`);
      console.error(`Rendering beat ${n}/${beats.length} (${beats[i].id || ""}) -> ${outPng}`);
      await renderStill(beats[i], outPng, browser);
      outputs.push(outPng);
    }
  } finally {
    await browser.close();
  }
  console.log(JSON.stringify({ outputs }));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
