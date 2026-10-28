// Usage: node render-scenes.js <html> <fontNodeModulesDir> <outDir>
// Renders each scene of a deterministic HTML timeline (window.seek, window.SCENES) to its own MP4,
// using identical encoder settings so the files can be joined with the concat demuxer (-c copy).
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { chromium } = require('playwright');

const [htmlPath, fontDir, outDir] = process.argv.slice(2);
const FPS = 30;

function encodeScene(page, s, e, outFile) {
  return new Promise(async (resolve, reject) => {
    const tmp = outFile.replace(/\.mp4$/, '.part.mp4');
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-r', String(FPS), '-g', '60', tmp]);
    ff.stderr.on('data', (d) => process.stderr.write(d));
    ff.on('close', (c) => { if (c === 0) { fs.renameSync(tmp, outFile); resolve(); } else reject(new Error('ffmpeg exit ' + c)); });
    const f0 = Math.round(s * FPS), f1 = Math.round(e * FPS);
    for (let f = f0; f < f1; f++) {
      await page.evaluate((t) => window.seek(t), f / FPS);
      const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
    }
    ff.stdin.end();
  });
}

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const src = fs.readFileSync(htmlPath, 'utf8').replaceAll('FONTBASE', 'file://' + path.join(fontDir, '@fontsource'));
  const tmpHtml = path.join(path.dirname(path.resolve(htmlPath)), '_render_tmp.html');
  fs.writeFileSync(tmpHtml, src);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto('file://' + tmpHtml);
  await page.evaluate(() => document.fonts.ready);
  const duration = await page.evaluate(() => window.DURATION);
  const scenes = await page.evaluate(() => window.SCENES.map((s) => ({ id: s.id, start: s.start, end: Math.min(s.end, window.DURATION) })));
  const list = [];
  for (const sc of scenes) {
    const out = path.join(outDir, `${sc.id}.mp4`);
    await encodeScene(page, sc.start, sc.end, out);
    list.push(`file '${out}'`);
    console.log('scene', sc.id, sc.start, '→', sc.end);
  }
  fs.writeFileSync(path.join(outDir, 'list.txt'), list.join('\n') + '\n');
  await page.evaluate((t) => window.seek(t), 3.0);
  await page.screenshot({ path: path.join(outDir, 'kapak.jpg'), type: 'jpeg', quality: 92 });
  await browser.close();
  fs.unlinkSync(tmpHtml);
  console.log('duration', duration);
})().catch((e) => { console.error(e); process.exit(1); });
