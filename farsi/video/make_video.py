#!/usr/bin/env python3
"""ترکیه بدون تله — sohbet formatında Reels üretici.

Kullanım:  python3 farsi/video/make_video.py <spec.json> <çıktı-klasörü>
Çıktı:     <çıktı-klasörü>/reel.mp4 (1080x1920, 30 fps, sesli), kapak.jpg, timeline.json
Önce bir kez:  bash farsi/setup.sh
Spec biçimi ve kurallar: farsi/README.md
"""
import asyncio, glob, hashlib, json, os, pathlib, subprocess, sys

import numpy as np
import soundfile as sf

HERE = pathlib.Path(__file__).resolve().parent
CACHE = pathlib.Path(os.environ.get("FARSI_CACHE", "/tmp/farsi-cache"))
VOICE_DIR = CACHE / "vits-piper-fa_IR-amir-medium"
FONT_DIR = CACHE / "node_modules/vazirmatn/fonts/ttf"
BRAND_VOICE = "ترکیهٔ بدونِ تله."
SR = 44100
_tts = None


def tts(text):
    """Metni seslendirir; (örnekler@44100, süre) döndürür. Sonuçlar önbelleğe alınır."""
    global _tts
    key = hashlib.sha1(text.encode()).hexdigest()[:16]
    f = CACHE / "wav" / f"{key}.wav"
    if not f.exists():
        if _tts is None:
            import sherpa_onnx
            cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
                vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                    model=glob.glob(str(VOICE_DIR / "*.onnx"))[0],
                    tokens=str(VOICE_DIR / "tokens.txt"),
                    data_dir=str(VOICE_DIR / "espeak-ng-data")), num_threads=4))
            _tts = sherpa_onnx.OfflineTts(cfg)
        a = _tts.generate(text, sid=0, speed=1.0)
        if len(a.samples) == 0:
            raise SystemExit(f"Seslendirme boş döndü: {text}")
        f.parent.mkdir(parents=True, exist_ok=True)
        sf.write(str(f), np.asarray(a.samples, dtype="float32"), int(a.sample_rate))
    x, sr = sf.read(str(f))
    x = np.repeat(x, SR // sr) if sr != SR else x
    x = np.convolve(x, [0.25, 0.5, 0.25], "same")
    x = x / max(1e-6, np.max(np.abs(x))) * 0.8
    return x, len(x) / SR


def build_timeline(spec):
    """Seslendirme sürelerinden tüm zamanları hesaplar. (timeline, ses_olayları) döndürür."""
    snd = []  # (zaman, tür, veri)
    _, d0 = tts(spec["intro"]["voice"])
    snd.append((0.3, "voice", spec["intro"]["voice"]))
    C = max(4.5, 0.3 + d0 + 0.25)
    D = 1.7
    snd += [(C, "hit", 0.6), (C + 0.25, "voice", BRAND_VOICE)]
    t = C + D + 0.5
    rows, flags, skips, status_t, last_in, n = [], [], [], None, None, 0
    for ev in spec["events"]:
        k = ev["type"]
        if k == "in":
            n += 1
            rid = f"m{n}"
            rows.append({"kind": "typing", "a": t, "b": t + 0.9})
            t += 0.9
            rows.append({"kind": "in", "id": rid, "t": t, "x": ev["text"], "m": ev.get("time", ""), "ty": 1})
            snd.append((t, "pop_in", 0.35))
            last_in = rid
            t += min(3.6, 1.3 + 0.038 * len(ev["text"]))
        elif k == "out":
            n += 1
            rows.append({"kind": "out", "id": f"m{n}", "t": t, "x": ev["text"], "m": ev.get("time", ""),
                         "one": 1 if ev.get("unread") else 0, "ty": 0})
            snd.append((t, "pop_out", 0.3))
            t += min(3.0, 0.9 + 0.034 * len(ev["text"]))
        elif k == "flag":
            if last_in is None:
                raise SystemExit("flag olayından önce en az bir 'in' mesajı olmalı")
            _, d = tts(ev["voice"])
            a, b = t, t + 0.4 + d + 0.8
            flags.append({"a": a, "b": b, "id": last_in, "k": ev["k"], "h": ev["h"], "p": ev["p"]})
            snd += [(a, "hit", 0.55), (a + 0.4, "voice", ev["voice"])]
            t = b + 0.4
        elif k == "skip":
            n += 1
            skips.append({"a": t, "b": t + 1.6, "big": ev["big"], "small": ev.get("small", "")})
            snd.append((t - 0.1, "whoosh", 0.5))
            rows.append({"kind": "mid", "id": f"m{n}", "t": t + 0.8, "x": ev["big"], "ty": 0})
            t += 1.8
        elif k == "status":
            status_t = t
            t += 1.3
        else:
            raise SystemExit(f"Bilinmeyen olay türü: {k}")
    L = spec["lesson"]
    la = t + 0.2
    snd.append((la - 0.1, "whoosh", 0.4))
    cur = la + 0.3
    if L.get("title_voice"):
        _, d = tts(L["title_voice"])
        snd.append((cur, "voice", L["title_voice"]))
        cur += d + 0.25
    else:
        cur += 0.8
    items = []
    for it in L["items"]:
        items.append({"t": cur, "html": it["html"], "warn": 1 if it.get("warn") else 0})
        snd.append((cur, "tick", 0.3))
        if it.get("voice"):
            _, d = tts(it["voice"])
            snd.append((cur + 0.1, "voice", it["voice"]))
            cur += d + 0.35
        else:
            cur += 1.2
    lb = cur + 0.9
    E = lb + 0.2
    snd.append((E - 0.1, "whoosh", 0.35))
    _, de = tts(spec["end"]["voice"])
    snd.append((E + 0.4, "voice", spec["end"]["voice"]))
    total = round(max(E + 5.5, E + 0.4 + de + 1.8), 2)
    tl = {"C": C, "D": D, "rows": rows, "flags": flags, "skips": skips, "status_t": status_t,
          "contact": spec["contact"],
          "intro": {"tag": spec["intro"]["tag"], "h1": spec["intro"]["h1"], "note": spec["intro"].get("note", "")},
          "lesson": {"a": la, "b": lb, "title": L["title"], "items": items, "src": L.get("src", ""), "src_t": cur - 0.6},
          "end": {"t": E, "h1": spec["end"]["h1"], "cta": spec["end"]["cta"]}, "total": total}
    return tl, snd


def mix_audio(snd, total, out):
    mix = np.zeros(int(SR * total))

    def put(x, t, g=1.0):
        i = int(t * SR)
        x = x[:max(0, len(mix) - i)]
        mix[i:i + len(x)] += x * g

    def ar(d):
        return np.arange(int(d * SR)) / SR

    def pop_in():
        t = ar(0.16); return np.sin(2 * np.pi * (880 + 500 * t / 0.16) * t) * np.exp(-t * 22)

    def pop_out():
        t = ar(0.14); return np.sin(2 * np.pi * (620 - 200 * t / 0.14) * t) * np.exp(-t * 26)

    def hit():
        t = ar(0.9); x = np.sin(2 * np.pi * (90 * np.exp(-t * 3) + 38) * t) * np.exp(-t * 4.5)
        return x + np.random.default_rng(1).standard_normal(len(t)) * np.exp(-t * 40) * 0.5

    def whoosh():
        n = np.random.default_rng(2).standard_normal(int(0.6 * SR)); n = np.convolve(n, np.ones(200) / 200, "same") * 12
        return n * np.sin(np.pi * np.linspace(0, 1, len(n))) ** 2

    def tick():
        t = ar(0.12); return np.sin(2 * np.pi * 1320 * t) * np.exp(-t * 40)

    fx = {"pop_in": pop_in, "pop_out": pop_out, "hit": hit, "whoosh": whoosh, "tick": tick}
    t = np.arange(len(mix)) / SR
    dr = (np.sin(2 * np.pi * 55 * t) + 0.6 * np.sin(2 * np.pi * 82.4 * t) + 0.3 * np.sin(2 * np.pi * 110.3 * t)) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.13 * t))
    mix += dr * np.clip(t / 1.5, 0, 1) * np.clip((total - t) / 1.5, 0, 1) * 0.035
    voices = []
    for when, kind, data in snd:
        if kind == "voice":
            x, d = tts(data); put(x, when); voices.append((round(when, 2), round(when + d, 2)))
        else:
            put(fx[kind](), when, data)
    voices.sort()
    for (a1, b1), (a2, b2) in zip(voices, voices[1:]):
        if a2 < b1:
            raise SystemExit(f"Seslendirmeler çakışıyor: {b1} > {a2}")
    sf.write(str(out), np.tanh(mix * 1.1).astype("float32"), SR)


async def render(page_path, total, out, stills):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        exe = next((e for e in ["/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser"] if os.path.exists(e)), None)
        b = await p.chromium.launch(executable_path=exe, args=["--no-sandbox", "--allow-file-access-from-files"])
        pg = await b.new_page(viewport={"width": 1080, "height": 1920})
        await pg.goto("file://" + str(page_path))
        await pg.evaluate("document.fonts.ready")
        await pg.evaluate("init()")
        for name, t in stills:
            await pg.evaluate(f"render({t})")
            await pg.screenshot(path=str(out.parent / name), type="jpeg", quality=88)
        ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", "30", "-c:v", "mjpeg", "-i", "-",
                               "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE)
        for i in range(int(total * 30)):
            await pg.evaluate(f"render({i / 30})")
            ff.stdin.write(await pg.screenshot(type="jpeg", quality=92))
        ff.stdin.close()
        if ff.wait() != 0:
            raise SystemExit("ffmpeg görüntü kodlaması başarısız")
        await b.close()


def main():
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = pathlib.Path(sys.argv[2]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    if not VOICE_DIR.exists() or not FONT_DIR.exists():
        raise SystemExit("Önce: bash farsi/setup.sh")
    tl, snd = build_timeline(spec)
    (out / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    page = out / "page.html"
    page.write_text((HERE / "template.html").read_text(encoding="utf-8").replace("__FONT__", str(FONT_DIR)).replace("__TL__", json.dumps(tl, ensure_ascii=False)), encoding="utf-8")
    mix_audio(snd, tl["total"], out / "mix.wav")
    # kontrol kareleri: kanca, ilk uyarı kartı, özet ekranı, kapanış
    stills = [("kapak.jpg", 3.0)]
    if tl["flags"]:
        stills.append(("kare_uyari.jpg", tl["flags"][0]["a"] + 2.0))
    stills += [("kare_ozet.jpg", tl["lesson"]["b"] - 0.5), ("kare_kapanis.jpg", tl["total"] - 0.5)]
    asyncio.run(render(page, tl["total"], out / "video_tmp.mp4", stills))
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", str(out / "video_tmp.mp4"), "-i", str(out / "mix.wav"), "-map", "0:v", "-map", "1:a",
                           "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", str(out / "reel_tmp.mp4")])
    os.replace(out / "reel_tmp.mp4", out / "reel.mp4")
    for f in ["video_tmp.mp4", "mix.wav", "page.html"]:
        (out / f).unlink()
    print(f"Tamam: {out / 'reel.mp4'}  süre={tl['total']} sn")


if __name__ == "__main__":
    main()
