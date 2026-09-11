#!/usr/bin/env node
/**
 * build_video.js — the orchestrator.
 *
 * Takes one scene-spec JSON (6 beats, see maps/build_scene_html.js's
 * buildSceneHTML() docblock for the per-beat camera/markers/lines shape)
 * and runs the full local pipeline in order to produce one finished MP4:
 *
 *   for each beat:
 *     1. narrate.py   -> beatN.wav   (locked espeak-ng voice)
 *     2. caption.py   -> beatN.ass   (word-timed captions, even-slicing)
 *     3. render_scene.js -> beatN.webm  (Playwright-recorded map animation,
 *        duration = the ACTUAL measured length of beatN.wav)
 *   assemble.py -> mux each beat's video+audio+captions, concat, final.mp4
 *
 * Usage:
 *   node build_video.js <scene-spec.json> <out.mp4> [--keep-work]
 *
 * All intermediate files (wav/ass/webm/mp4-per-beat) live in a work dir
 * under pipeline/output/<scene-spec-basename>-work/ so a failed run can be
 * inspected; pass --keep-work to skip cleanup (default: kept, since these
 * are gitignored and cheap -- nothing here is committed to git).
 */
"use strict";
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const PKG_ROOT = __dirname;
const PYTHON = "python3";

function sh(cmd, args, opts = {}) {
  console.error("+ " + cmd + " " + args.map((a) => JSON.stringify(a)).join(" "));
  return execFileSync(cmd, args, { stdio: ["ignore", "pipe", "inherit"], ...opts })
    .toString();
}

async function main() {
  const argv = process.argv.slice(2);
  const scenePath = argv[0];
  const outMp4 = argv[1];
  if (!scenePath || !outMp4) {
    console.error("Usage: node build_video.js <scene-spec.json> <out.mp4>");
    process.exit(1);
  }

  const spec = JSON.parse(fs.readFileSync(scenePath, "utf8"));
  const beats = spec.beats;
  if (!Array.isArray(beats) || beats.length === 0) {
    throw new Error("scene-spec JSON must have a non-empty `beats` array");
  }

  const baseName = path.basename(scenePath).replace(/\.scenes\.json$/, "").replace(/\.json$/, "");
  const workDir = path.join(PKG_ROOT, "output", `${baseName}-work`);
  fs.mkdirSync(workDir, { recursive: true });

  const { renderScene } = require("./render_scene.js");

  let totalDuration = 0;
  for (let i = 0; i < beats.length; i++) {
    const n = i + 1;
    const beat = beats[i];
    console.error(`\n=== Beat ${n}/${beats.length}: ${beat.id || ""} ===`);

    const wavPath = path.join(workDir, `beat${n}.wav`);
    const assPath = path.join(workDir, `beat${n}.ass`);
    const sceneJsonPath = path.join(workDir, `beat${n}.scene.json`);
    const webmPath = path.join(workDir, `beat${n}.webm`);

    // 1. Narration
    const narrateOut = sh(PYTHON, [
      path.join(PKG_ROOT, "narrate.py"),
      beat.voText,
      wavPath,
    ]);
    const { duration_sec: duration } = JSON.parse(narrateOut.trim().split("\n").pop());
    console.error(`  narration duration: ${duration.toFixed(2)}s`);
    totalDuration += duration;

    // 2. Captions (word-timed, even time-slicing fallback -- see caption.py docstring)
    sh(PYTHON, [
      path.join(PKG_ROOT, "caption.py"),
      beat.voText,
      String(duration),
      assPath,
    ]);

    // 3. Scene video (Playwright-recorded map animation, exact beat duration)
    const sceneForRender = {
      duration,
      highlight: beat.highlight || [],
      camera: beat.camera,
      markers: beat.markers || [],
      lines: beat.lines || [],
      onScreenText: beat.onScreenText || "",
      onScreenTextShowAt: beat.onScreenTextShowAt != null ? beat.onScreenTextShowAt : 0.12,
    };
    fs.writeFileSync(sceneJsonPath, JSON.stringify(sceneForRender, null, 2));
    await renderScene(sceneJsonPath, webmPath);
    console.error(`  scene video: ${webmPath}`);
  }

  console.error(`\n=== Assembling final video (${beats.length} beats, ~${totalDuration.toFixed(1)}s VO) ===`);
  fs.mkdirSync(path.dirname(outMp4), { recursive: true });
  sh(PYTHON, [
    path.join(PKG_ROOT, "assemble.py"),
    "--work-dir", workDir,
    "--num-beats", String(beats.length),
    "--out", outMp4,
  ]);

  console.error(`\nDone: ${outMp4}`);
  console.log(JSON.stringify({ out: outMp4, totalVoDurationSec: totalDuration, workDir }));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
