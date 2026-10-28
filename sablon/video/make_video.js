// Usage: node make_video.js <spec.json> <outDir> <fontNodeModulesDir> [--snap t1,t2,...]
// Builds an Instagram Reel (1080x1920, 30 fps, H.264 + AAC) from a JSON scene spec using engine.html.
// Output: <outDir>/reel.mp4 and <outDir>/kapak.jpg (cover). With --snap, only writes full-size frames for checking.
const fs = require('fs');
const path = require('path');
const { spawn, execFileSync } = require('child_process');
const { chromium } = require('playwright');

const [specPath, outDir, fontDir, flag, snapList] = process.argv.slice(2);
const FPS = 30;
const here = __dirname;

function encodeScene(page, s, e, outFile) {
  return new Promise(async (resolve, reject) => {
    const tmp = outFile.replace(/\.mp4$/, '.part.mp4');
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-r', String(FPS), '-g', '60', tmp]);
    ff.stderr.on('data', (d) => process.stderr.write(d));
    ff.on('close', (c) => { if (c === 0) { fs.renameSync(tmp, outFile); resolve(); } else reject(new Error('ffmpeg exit ' + c)); });
    for (let f = Math.round(s * FPS); f < Math.round(e * FPS); f++) {
      await page.evaluate((t) => window.seek(t), f / FPS);
      const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
    }
    ff.stdin.end();
  });
}

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
  const html = fs.readFileSync(path.join(here, 'engine.html'), 'utf8')
    .replaceAll('FONTBASE', 'file://' + path.join(path.resolve(fontDir), '@fontsource'))
    .replace('/*SPEC*/null', JSON.stringify(spec).replace(/</g, '\\u003c'));
  const tmpHtml = path.join(path.resolve(outDir), '_engine.html');
  fs.writeFileSync(tmpHtml, html);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  await page.goto('file://' + tmpHtml);
  await page.evaluate(() => document.fonts.ready);
  if (errors.length) { console.error('page errors:', errors); process.exit(1); }
  const tl = await page.evaluate(() => window.TIMELINE);
  const scenes = await page.evaluate(() => window.SCENES);
  fs.writeFileSync(path.join(outDir, 'timeline.json'), JSON.stringify(tl, null, 1));
  console.log('duration', tl.duration, 'scenes', scenes.map((s) => `${s.id}:${s.start.toFixed(1)}-${s.end.toFixed(1)}`).join(' '));

  if (flag === '--snap') {
    for (const t of String(snapList).split(',').map(Number)) {
      await page.evaluate((x) => window.seek(x), t);
      await page.screenshot({ path: path.join(outDir, `snap_${t}.jpg`), type: 'jpeg', quality: 85 });
    }
    await browser.close(); fs.unlinkSync(tmpHtml); return;
  }

  const sceneDir = path.join(outDir, 'scenes');
  fs.mkdirSync(sceneDir, { recursive: true });
  const list = [];
  for (const sc of scenes) {
    const f = path.join(sceneDir, `${sc.id}.mp4`);
    await encodeScene(page, sc.start, sc.end, f);
    list.push(`file '${path.basename(f)}'`);
  }
  fs.writeFileSync(path.join(sceneDir, 'list.txt'), list.join('\n') + '\n');
  await page.evaluate((t) => window.seek(t), tl.cover);
  await page.screenshot({ path: path.join(outDir, 'kapak.jpg'), type: 'jpeg', quality: 92 });
  await browser.close();
  fs.unlinkSync(tmpHtml);

  const video = path.join(outDir, 'video_only.mp4');
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', path.join(sceneDir, 'list.txt'), '-c', 'copy', video]);
  execFileSync('python3', [path.join(here, 'audio.py'), path.join(outDir, 'timeline.json'), path.join(outDir, 'music.wav')], { stdio: 'inherit' });
  const tmpOut = path.join(outDir, 'reel.part.mp4');
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', video, '-i', path.join(outDir, 'music.wav'), '-map', '0:v', '-map', '1:a',
    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', tmpOut]);
  fs.renameSync(tmpOut, path.join(outDir, 'reel.mp4'));
  console.log('done', path.join(outDir, 'reel.mp4'));
})().catch((e) => { console.error(e); process.exit(1); });
