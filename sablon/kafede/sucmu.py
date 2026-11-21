"""Emsal Var mı? — "Suç mu, değil mi?" motoru (12–20 sn, döngüye uygun, gönderilmek için).
Akış: soru (ilk kareden itibaren ekranda) → 3 sn geri sayım, iki seçenek → sonuç bandı + bilgi kartları → "…gönder".
Kullanım:
  python3 sucmu.py s1 --dosya ../../2026/<tarih>-sucmu/bolumler.py --ses <wav klasörü> --kare 0.3 5 9 15
  python3 sucmu.py s1 --dosya ... --ses ... --cikti out/reel.mp4 --kapak out/kapak.jpg
"""
import argparse, importlib.util, math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sohbet import F, W, H, FPS, ease, CREAM, INK, NAVY, GOLD, INTER_M, INTER_SB, INTER_R, CORM, CORM_I, MONO
from kafede import RED, GREEN, SOFT
from kafede_kisa import load_wav, tempo, SR

TEMPO = 1.10
SAYIM = 2.7          # geri sayım süresi
GAP = 0.16
SON = 0.9            # son sesten sonra bekleme (döngü)
BG1, BG2 = (9, 13, 24), (20, 28, 48)


def wrap(text, font, maxw):
    out, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if font.getlength(t) <= maxw or not cur:
            cur = t
        else:
            out.append(cur); cur = w
    if cur:
        out.append(cur)
    return out


def bg():
    g = np.linspace(0, 1, H)[:, None, None]
    a = (np.array(BG1)[None, None, :] * (1 - g) + np.array(BG2)[None, None, :] * g)
    im = Image.fromarray(np.repeat(a, W, axis=1).astype(np.uint8)).convert('RGBA')
    d = ImageDraw.Draw(im)
    f = F(CORM, 40)
    s = 'E M S A L   V A R   M I ?'
    d.text(((W - f.getlength(s)) / 2, 150), s, font=f, fill=GOLD + (255,))
    return im


def timeline(ep, key, sesdir):
    n = len(ep['satirlar']) + 2
    aud = []
    for i in range(n):
        p = os.path.join(sesdir, f'{key}_A_{i:02d}.wav') if sesdir else None
        aud.append(load_wav(p) if p and os.path.exists(p) else None)
    voiced = all(a is not None for a in aud)
    texts = [ep['soru_ses']] + [s for _, s, _ in ep['satirlar']] + [ep['gonder_ses']]
    if voiced:
        aud = [tempo(a, TEMPO) for a in aud]
        durs = [len(a) / SR for a in aud]
    else:
        durs = [max(1.2, 0.36 * len(t.split()) + 0.3) for t in texts]
    t = 0.15
    seg = []
    seg.append(dict(t0=t, d=durs[0])); t += durs[0] + 0.1
    t_say = t; t += SAYIM
    t_rev = t; t += 0.25
    for i in range(1, n):
        seg.append(dict(t0=t, d=durs[i])); t += durs[i] + GAP
    return dict(seg=seg, aud=aud if voiced else None, t_say=t_say, t_rev=t_rev, total=t - GAP + SON, voiced=voiced)


def pill(d, cx, cy, text, font, fill, fg, padx=30, pady=14, outline=None, a=255):
    tw = font.getlength(text); th = font.size
    box = [cx - tw / 2 - padx, cy - th / 2 - pady, cx + tw / 2 + padx, cy + th / 2 + pady + 6]
    d.rounded_rectangle(box, (box[3] - box[1]) / 2 if pady < 20 else 26, fill=fill + (a,) if fill else None,
                        outline=outline + (a,) if outline else None, width=5)
    d.text((cx - tw / 2, cy - th / 2 - 2), text, font=font, fill=fg + (a,))
    return box


def compose(t, st):
    ep, tm = st['ep'], st['tm']
    fr = st['bg'].copy()
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    rev = t >= tm['t_rev']
    pr = ease((t - tm['t_rev']) / 0.35) if rev else 0.0
    ok = ep['dogru']
    col_ok = GREEN if ok == 1 else RED
    # ---- soru bloğu: sonuçtan sonra küçülüp yukarı çıkar
    if pr < 1:
        a = int(255 * (1 - pr))
        m = F(MONO, 34)
        pill(d, 540, 300, 'GERÇEK DAVA', m, RED, (255, 255, 255), a=a)
        y = 400
        pulse = 1 + 0.02 * math.sin(t * 6)
        for l in ep['soru']:
            size = 92
            while F(CORM_I, size).getlength(l) > 960 and size > 56:
                size -= 2
            f = F(CORM_I, size)
            d.text(((W - f.getlength(l)) / 2, y), l, font=f, fill=CREAM + (a,))
            y += size + 22
        f = F(CORM, int(170 * pulse))
        d.text(((W - f.getlength(ep['vurgu'])) / 2, y + 20), ep['vurgu'], font=f, fill=GOLD + (a,))
        # seçenekler
        fb = F(INTER_SB, 66)
        cnt = (t - tm['t_say']) / SAYIM
        for i, (lab, col) in enumerate(zip(ep['secenekler'], (RED, GREEN))):
            cx = 290 + i * 500
            act = 0 <= cnt < 1 and int((t - tm['t_say']) * 3) % 2 == i
            box = [cx - 220, 1090, cx + 220, 1250]
            d.rounded_rectangle(box, 40, fill=col + (int(a * (0.34 if act else 0.14)),), outline=col + (a,), width=7)
            tw = fb.getlength(lab)
            ff = fb if tw < 400 else F(INTER_SB, 54)
            tw = ff.getlength(lab)
            d.text((cx - tw / 2, 1170 - ff.size / 2 - 6), lab, font=ff, fill=(255, 255, 255, a))
        if 0 <= cnt < 1:
            d.rounded_rectangle([110, 1310, 970, 1334], 12, fill=(255, 255, 255, 40))
            d.rounded_rectangle([110, 1310, 110 + 860 * (1 - cnt), 1334], 12, fill=GOLD + (255,))
            num = str(3 - int(cnt * 3))
            fn = F(CORM, 150)
            d.text(((W - fn.getlength(num)) / 2, 1350), num, font=fn, fill=GOLD + (255,))
            m2 = F(MONO, 28)
            s = 'SEN NE DERSİN?'
            d.text(((W - m2.getlength(s)) / 2, 1020), s, font=m2, fill=SOFT + (255,))
        elif cnt < 0:
            m2 = F(MONO, 28)
            s = 'TAHMİNİNİ YAP'
            d.text(((W - m2.getlength(s)) / 2, 1020), s, font=m2, fill=SOFT + (a,))
    if rev:
        a = int(255 * pr)
        # küçük soru (bağlam)
        fq = F(CORM_I, 44)
        q = ' '.join(ep['soru']) + ' ' + ep['vurgu']
        yy = 250
        for l in wrap(q, fq, 900):
            d.text(((W - fq.getlength(l)) / 2, yy), l, font=fq, fill=CREAM + (int(a * 0.85),))
            yy += 54
        # sonuç bandı
        fs = F(INTER_SB, 74)
        while fs.getlength(ep['sonuc']) > 900:
            fs = F(INTER_SB, fs.size - 2)
        sc = 1.25 - 0.25 * pr
        by = yy + 40
        bh = 150
        d.rounded_rectangle([60, by, 1020, by + bh], 34, fill=col_ok + (a,))
        d.text(((W - fs.getlength(ep['sonuc'])) / 2, by + bh / 2 - fs.size / 2 - 6), ep['sonuc'], font=fs, fill=(255, 255, 255, a))
        # bilgi kartları
        y = by + bh + 44
        fc = F(INTER_SB, 46)
        for i, (ekran, _, tur) in enumerate(ep['satirlar']):
            sg = tm['seg'][i + 1]
            if t < sg['t0']:
                break
            p = ease((t - sg['t0']) / 0.25)
            lines = wrap(ekran, fc, 860)
            h = 44 + len(lines) * 60
            aa = int(255 * p)
            off = int((1 - p) * 40)
            cur = sg['t0'] <= t < sg['t0'] + sg['d'] + GAP
            if tur == 'kanun':
                d.rounded_rectangle([60, y + off, 1020, y + h + off], 26, fill=(34, 30, 14, aa), outline=GOLD + (aa,), width=4)
                fg = GOLD
            else:
                d.rounded_rectangle([60, y + off, 1020, y + h + off], 26, fill=CREAM + (aa if cur else int(aa * 0.86),))
                fg = INK
            ty = y + 20 + off
            for l in lines:
                d.text((100, ty), l, font=fc, fill=fg + (aa,))
                ty += 60
            y += h + 22
        # gönder çağrısı
        sg = tm['seg'][-1]
        if t >= sg['t0']:
            p = ease((t - sg['t0']) / 0.3)
            fg_ = F(INTER_SB, 46)
            lines = wrap(ep['gonder'], fg_, 760)
            h = 50 + len(lines) * 60
            yb = max(y + 14, 1250) - int(8 * math.sin((t - sg['t0']) * 7))
            aa = int(255 * p)
            d.rounded_rectangle([60, yb, 1020, yb + h], h / 2 if len(lines) == 1 else 40, fill=(255, 255, 255, aa))
            # kâğıt uçak
            px, py = 130, yb + h / 2
            d.polygon([(px - 34, py - 6), (px + 36, py - 30), (px + 6, py + 34), (px - 2, py + 6)], fill=(40, 120, 255, aa))
            ty = yb + 24
            for l in lines:
                d.text((190, ty), l, font=fg_, fill=INK + (aa,))
                ty += 60
        # künye + uyarı
        mm = F(MONO, 22)
        d.text(((W - mm.getlength(ep['kunye'])) / 2, 1500), ep['kunye'], font=mm, fill=(178, 186, 198, a))
        rn = F(INTER_R, 23)
        s = 'Genel bilgilendirme amaçlıdır; hukuki görüş değildir.'
        d.text(((W - rn.getlength(s)) / 2, 1536), s, font=rn, fill=SOFT + (a,))
    fr.alpha_composite(ov)
    return fr.convert('RGB')


def mix(st, path):
    tm = st['tm']
    n = int(SR * tm['total'])
    a = np.zeros(n + SR, dtype=np.float32)

    def add(t0, s):
        i0 = int(t0 * SR); m = max(0, min(len(s), len(a) - i0)); a[i0:i0 + m] += s[:m]

    def tone(t0, f0, f1, dur, vol, decay=30):
        m = int(dur * SR); tt = np.arange(m) / SR; f = np.linspace(f0, f1, m)
        add(t0, (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * decay) * (1 - np.exp(-tt * 900)) * vol).astype(np.float32))
    if tm['aud']:
        for sg, au in zip(tm['seg'], tm['aud']):
            add(sg['t0'], au * 0.9)
    for k in range(3):
        tone(tm['t_say'] + k * SAYIM / 3, 880, 880, 0.09, 0.16, 45)
    m = int(0.25 * SR); tt = np.arange(m) / SR
    add(tm['t_rev'], ((np.sin(2 * np.pi * 85 * tt) * 0.9 + np.random.default_rng(1).normal(0, 0.2, m) * np.exp(-tt * 50)) * np.exp(-tt * 16) * 0.35).astype(np.float32))
    tone(tm['t_rev'] + 0.05, 520, 1040, 0.3, 0.10, 10)
    for sg in tm['seg'][1:]:
        tone(sg['t0'] - 0.03, 760, 600, 0.07, 0.05)
    pcm = (np.clip(a[:n], -1, 1) * 32767).astype(np.int16)
    with wave.open(path, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


def build(dosya, key, sesdir):
    spec = importlib.util.spec_from_file_location('sucmu_bolum', dosya)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    ep = mod.BOLUMLER[key]
    return dict(ep=ep, tm=timeline(ep, key, sesdir), bg=bg())


def render(st, out):
    tm = st['tm']
    tmp = out[:-4] + '.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                          '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    for i in range(int(round(tm['total'] * FPS))):
        p.stdin.write(compose(i / FPS, st).tobytes())
    p.stdin.close()
    if p.wait() != 0:
        sys.exit('ffmpeg hata')
    wav = out[:-4] + '.wav'; mix(st, wav)
    tmp2 = out[:-4] + '.tmp2.mp4'
    r = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                        '-af', 'loudnorm=I=-15:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '160k', '-shortest',
                        '-movflags', '+faststart', tmp2])
    if r.returncode != 0:
        sys.exit('ses ekleme hata')
    os.replace(tmp2, out); os.remove(tmp); os.remove(wav)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('bolum'); ap.add_argument('--dosya', required=True); ap.add_argument('--ses')
    ap.add_argument('--kare', nargs='*', type=float); ap.add_argument('--cikti'); ap.add_argument('--kapak')
    a = ap.parse_args()
    st = build(a.dosya, a.bolum, a.ses)
    tm = st['tm']
    print('süre: %.1f sn | sesli: %s | geri sayım %.1f | sonuç %.1f' % (tm['total'], tm['voiced'], tm['t_say'], tm['t_rev']),
          [round(s['t0'], 1) for s in tm['seg']])
    for t in a.kare or []:
        compose(t, st).save(f'{a.bolum}_{t:05.1f}.png')
    if a.kapak:
        compose(0.3, st).save(a.kapak, quality=92)
    if a.cikti:
        render(st, a.cikti); print('done', a.cikti)


if __name__ == '__main__':
    main()
