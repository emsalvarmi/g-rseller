#!/usr/bin/env python3
"""ترکیه بدون تله — gönderi görseli üretici (1080x1350).
Kullanım: python3 farsi/post/make_post.py <spec.json> <çıktı-klasörü>
Spec: {"slides": ["<gövde html>", ...]}  → 01.png, 02.png, ...
Her gövde, post/post.css sınıflarını kullanır; logo ve alt satır otomatik eklenir. Örnekler: farsi/ornek/
"""
import asyncio, json, os, pathlib, sys
from playwright.async_api import async_playwright
HERE = pathlib.Path(__file__).resolve().parent
CACHE = pathlib.Path(os.environ.get("FARSI_CACHE", "/tmp/farsi-cache"))
FONT = CACHE / "node_modules/vazirmatn/fonts/ttf"

async def main():
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = pathlib.Path(sys.argv[2]).resolve(); out.mkdir(parents=True, exist_ok=True)
    css = (HERE / "post.css").read_text(encoding="utf-8").replace("__FONT__", str(FONT))
    n = len(spec["slides"])
    async with async_playwright() as p:
        exe = next((e for e in ["/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser"] if os.path.exists(e)), None)
        b = await p.chromium.launch(executable_path=exe, args=["--no-sandbox", "--allow-file-access-from-files"])
        pg = await b.new_page(viewport={"width": 1080, "height": 1350})
        for i, body in enumerate(spec["slides"], 1):
            foot = (f"<div class='pg'>{i} / {n}</div>" if n > 1 else "") + "<div class='hd'>@torkiye_bedoone_tale</div>"
            html = f"<html lang='fa'><head><meta charset='utf-8'><style>{css}</style></head><body><div class='lg'>ترکیه بدون تله</div>{body}{foot}</body></html>"
            f = out / f"{i:02d}.html"; f.write_text(html, encoding="utf-8")
            await pg.goto("file://" + str(f)); await pg.evaluate("document.fonts.ready")
            over = await pg.evaluate("document.body.scrollHeight > 1350")
            await pg.screenshot(path=str(out / f"{i:02d}.png")); f.unlink()
            print(f"{out / f'{i:02d}.png'}" + ("  UYARI: içerik taşıyor, metni kısaltın" if over else ""))
        await b.close()
asyncio.run(main())
