"""Format 2 — "Başına Gelirse: 3 Adım" motoru.
Akış: 0-2 sn senaryo kartı → 3 numaralı kart tek tek belirir → "Kaydet" çağrısı.
Ses: tek erkek anlatıcı. Kimlikler <anahtar>_00 (senaryo) + _01.._03 (3 adım) + _04 (CTA).
"""
import argparse, importlib.util, math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sohbet import F, W, H, FPS, ease, CREAM, INK, NAVY, GOLD, INTER_M, INTER_SB, INTER_R, CORM, CORM_I, MONO
from kafede import RED, GREEN, SOFT
from kafede_kisa import load_wav, tempo, SR
from sucmu import bg, wrap, TEMPO

GAP = 0.18
SON = 0.9


def timeline(ep, key, sesdir):
    n = 5  # senaryo + 3 adım + CTA
    aud = []
    for i in range(n):
        p = os.path.join(sesdir, f'{key}_A_{i:02d}.wav') if sesdir else None
        aud.append(load_wav(p) if p and os.path.exists(p) else None)
    voiced = all(a is not None for a in aud)
    texts = [ep['senaryo_ses']] + [s for _, s in ep['adimlar']] + [ep['cta_ses']]
    if voiced:
        aud = [tempo(a, TEMPO) for a in aud]
        durs = [len(a) / SR for a in aud]
    else:
        durs = [max(1.5, 0.36 * len(t.split()) + 0.3) for t in texts]
    t = 0.15
    seg = []
    for i in range(n):
        seg.append(dict(t0=t, d=durs[i])); t += durs[i] + GAP
    return dict(seg=seg, aud=aud if voiced else None, total=t - GAP + SON, voiced=voiced)


def adim_boyut(baslik, dayanak, font_b, font_d):
    lines = wrap(baslik, font_b, 760)
    body_h = len(lines) * (font_b.size + 4)
    base = 24 + body_h + 24
    if dayanak:
        base += font_d.size + 10
    return max(base, 96), lines


def adim_karti(d, y, no, baslik, dayanak, a, cur, font_b, font_d, fn):
    bh, lines = adim_boyut(baslik, dayanak, font_b, font_d)
    aa = int(255 * a)
    d.rounded_rectangle([60, y, 1020, y + bh], 28, fill=CREAM + (aa if cur else int(aa * 0.86),))
    d.ellipse([90, y + 18, 90 + 70, y + 18 + 70], fill=GOLD + (aa,))
    nw = fn.getlength(str(no))
    d.text((90 + 35 - nw / 2, y + 18 + 35 - fn.size / 2 - 3), str(no), font=fn, fill=INK + (aa,))
    ty = y + 24
    for l in lines:
        d.text((200, ty), l, font=font_b, fill=INK + (aa,))
        ty += font_b.size + 4
    if dayanak:
        d.text((200, ty + 6), dayanak, font=font_d, fill=(100, 108, 120, aa))
    return bh


def compose(t, st):
    ep, tm = st['ep'], st['tm']
    fr = st['bg'].copy()
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    # senaryo etiketi + metin (hep üstte)
    m = F(MONO, 30)
    etiket = 'BAŞINA GELİRSE'
    tw = m.getlength(etiket)
    d.rounded_rectangle([540 - tw / 2 - 22, 240, 540 + tw / 2 + 22, 290], 14, fill=(40, 80, 160, 255))
    d.text((540 - tw / 2, 246), etiket, font=m, fill=(255, 255, 255, 255))
    sg0 = tm['seg'][0]
    say = F(CORM_I, 54)
    senaryo_lines = wrap(ep['senaryo'], say, 940)
    yy = 330
    for l in senaryo_lines:
        d.text(((W - say.getlength(l)) / 2, yy), l, font=say, fill=CREAM + (255,))
        yy += say.size + 10
    yy += 30
    # 3 adım
    f_b = F(INTER_SB, 44)
    f_d = F(INTER_R, 24)
    fn = F(CORM, 62)
    for i in range(1, 4):
        sg = tm['seg'][i]
        if t < sg['t0']:
            break
        p = ease((t - sg['t0']) / 0.3)
        a = p
        cur = sg['t0'] <= t < sg['t0'] + sg['d'] + GAP
        baslik, _ = ep['adimlar'][i - 1]
        dayanak = ep['dayanaklar'][i - 1] if i - 1 < len(ep['dayanaklar']) else ''
        off = int((1 - p) * 30)
        bh = adim_karti(d, yy + off, i, baslik, dayanak, a, cur, f_b, f_d, fn)
        yy += bh + 18
    # CTA
    sg = tm['seg'][4]
    if t >= sg['t0']:
        p = ease((t - sg['t0']) / 0.35)
        f_cta = F(INTER_SB, 46)
        lines = wrap(ep['cta'], f_cta, 760)
        h = 50 + len(lines) * 60
        yb = max(yy + 10, 1340) - int(6 * math.sin((t - sg['t0']) * 7))
        aa = int(255 * p)
        d.rounded_rectangle([60, yb, 1020, yb + h], h / 2 if len(lines) == 1 else 40, fill=(255, 255, 255, aa))
        # kaydet ikonu (bookmark)
        px, py = 130, yb + h / 2
        d.polygon([(px - 18, py - 24), (px + 18, py - 24), (px + 18, py + 28), (px, py + 12), (px - 18, py + 28)], fill=(40, 80, 160, aa))
        ty = yb + 24
        for l in lines:
            d.text((190, ty), l, font=f_cta, fill=INK + (aa,))
            ty += 60
    # künye + uyarı
    mm = F(MONO, 22)
    d.text(((W - mm.getlength(ep['kunye'])) / 2, 1540), ep['kunye'], font=mm, fill=(178, 186, 198, 255))
    rn = F(INTER_R, 23)
    s = 'Genel bilgilendirme amaçlıdır; hukuki görüş değildir.'
    d.text(((W - rn.getlength(s)) / 2, 1580), s, font=rn, fill=SOFT + (255,))
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
            if au is not None:
                add(sg['t0'], au * 0.9)
    tone(0.02, 520, 780, 0.22, 0.08, 20)
    for i, sg in enumerate(tm['seg'][1:4], 1):
        tone(sg['t0'] - 0.04, 700 + i * 100, 500 + i * 60, 0.12, 0.08, 25)
    pcm = (np.clip(a[:n], -1, 1) * 32767).astype(np.int16)
    with wave.open(path, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


def build(dosya, key, sesdir):
    spec = importlib.util.spec_from_file_location('adim3_bolum', dosya)
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
    print('süre: %.1f sn | sesli: %s' % (tm['total'], tm['voiced']), [round(s['t0'], 1) for s in tm['seg']])
    for t in a.kare or []:
        compose(t, st).save(f'{a.bolum}_{t:05.1f}.png')
    if a.kapak:
        # kapak: senaryo + 3 adım birden görünür
        total = tm['seg'][4]['t0'] - 0.1
        compose(total, st).save(a.kapak, quality=92)
    if a.cikti:
        render(st, a.cikti); print('done', a.cikti)


if __name__ == '__main__':
    main()
