// Usage: node render.js <srcDir> <outDir> <file1.dc.html> [file2.dc.html ...]
// Renders each Design Component artboard's static markup to a PNG at its native size.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const [srcDir, outDir, ...files] = process.argv.slice(2);
const fontBase = 'file://' + path.join(__dirname, 'node_modules', '@fontsource');
const fontLinks = [
  'inter/400.css', 'inter/500.css', 'inter/600.css',
  'source-serif-4/400.css', 'source-serif-4/600.css',
  'source-serif-4/400-italic.css', 'source-serif-4/600-italic.css',
].map((p) => `<link rel="stylesheet" href="${fontBase}/${p}">`).join('\n');

function toStatic(src) {
  const start = src.indexOf('<x-dc>');
  const end = src.indexOf('</x-dc>');
  if (start < 0 || end < 0) throw new Error('no <x-dc> block');
  let body = src.slice(start + 6, end);
  body = body.replace(/<helmet>[\s\S]*?<\/helmet>/, '').trim();
  return `<!doctype html><html lang="tr"><head><meta charset="utf-8">${fontLinks}<style>body{margin:0}</style></head><body>${body}</body></html>`;
}

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: 1 });
  for (const [i, f] of files.entries()) {
    const html = toStatic(fs.readFileSync(path.join(srcDir, f), 'utf8'));
    const tmp = path.join(__dirname, `_tmp_${i}.html`);
    fs.writeFileSync(tmp, html);
    await page.setViewportSize({ width: 1600, height: 1600 });
    await page.goto('file://' + tmp);
    await page.evaluate(() => document.fonts.ready);
    const root = page.locator('body > div').first();
    const out = path.join(outDir, `${String(i + 1).padStart(2, '0')}.png`);
    await root.screenshot({ path: out });
    const box = await root.boundingBox();
    const fontsOk = await page.evaluate(() => [
      document.fonts.check('600 40px "Source Serif 4"'),
      document.fonts.check('400 40px Inter'),
    ]);
    console.log(out, Math.round(box.width) + 'x' + Math.round(box.height), 'fonts', fontsOk.join(','));
    fs.unlinkSync(tmp);
  }
  await browser.close();
})();
