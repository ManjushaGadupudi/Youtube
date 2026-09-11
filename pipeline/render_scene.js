/**
 * render_scene.js
 *
 * Given a scene spec (JSON: highlighted region(s), camera pan/zoom path,
 * markers, lines, on-screen text, duration in seconds), builds the scene
 * HTML (via maps/build_scene_html.js), launches Playwright/Chromium, and
 * uses Playwright's built-in video recording to capture exactly the
 * scene's duration. Outputs a raw .webm scene video (no audio track --
 * narration is muxed in separately by assemble.js).
 *
 * Usage:
 *   node render_scene.js <scene.json> <out.webm> [outDir]
 *
 * scene.json shape: see maps/build_scene_html.js's buildSceneHTML() docblock.
 */
"use strict";
const fs = require("fs");
const os = require("os");
const path = require("path");
const { chromium } = require("playwright");
const { buildSceneHTML } = require("./maps/build_scene_html.js");

const PKG_ROOT = __dirname;
const STYLE = JSON.parse(fs.readFileSync(path.join(PKG_ROOT, "config", "style.json"), "utf8"));

async function renderScene(scenePath, outWebm) {
  const scene = JSON.parse(fs.readFileSync(scenePath, "utf8"));
  if (!scene.duration || scene.duration <= 0) {
    throw new Error("scene.duration must be a positive number of seconds");
  }

  const html = buildSceneHTML(scene);
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "scene-"));
  const htmlPath = path.join(tmpDir, "scene.html");
  fs.writeFileSync(htmlPath, html);

  const videoDir = fs.mkdtempSync(path.join(os.tmpdir(), "scenevid-"));
  const { width, height } = STYLE.video;

  const browser = await chromium.launch({
    executablePath: process.env.PW_CHROMIUM || "/opt/pw-browsers/chromium",
  });
  try {
    const context = await browser.newContext({
      viewport: { width, height },
      recordVideo: { dir: videoDir, size: { width, height } },
      deviceScaleFactor: 1,
    });
    const page = await context.newPage();
    await page.goto("file://" + htmlPath);
    await page.waitForFunction("window.__sceneReady === true", { timeout: 5000 });

    // Let the in-page rAF loop run for exactly `duration` seconds of wall
    // clock, which is what Playwright's video recorder captures.
    await page.waitForTimeout(Math.round(scene.duration * 1000) + 250);

    await page.close();
    const videoObj = page.video();
    await context.close();

    // Playwright finalizes the video file only after context.close(); find it.
    const producedPath = videoObj ? await videoObj.path() : null;
    if (!producedPath || !fs.existsSync(producedPath)) {
      throw new Error("Playwright did not produce a video file");
    }
    fs.mkdirSync(path.dirname(outWebm), { recursive: true });
    fs.copyFileSync(producedPath, outWebm);
  } finally {
    await browser.close();
    fs.rmSync(tmpDir, { recursive: true, force: true });
    fs.rmSync(videoDir, { recursive: true, force: true });
  }

  return outWebm;
}

module.exports = { renderScene };

if (require.main === module) {
  const [scenePath, outWebm] = process.argv.slice(2);
  if (!scenePath || !outWebm) {
    console.error("Usage: node render_scene.js <scene.json> <out.webm>");
    process.exit(1);
  }
  renderScene(scenePath, outWebm)
    .then(() => console.log(JSON.stringify({ out: outWebm })))
    .catch((err) => {
      console.error(err);
      process.exit(1);
    });
}
