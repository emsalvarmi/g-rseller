"""Format 3 — "Bunu Yanlış Biliyoruz" motoru.
Akış: 0-2 sn "Herkes sanıyor ki..." + tırnaklı iddia → 2-3 sn büyük kırmızı X "YANLIŞ" damga
→ Gerçek kartı + Ceza/Bedel kartı → "Bunu sanan arkadaşına gönder" çağrısı.
Ses: tek erkek anlatıcı. Kimlikler <anahtar>_00 iddia, _01 YANLIŞ, _02 gerçek, _03 bedel, _04 CTA.
"""
import argparse, importlib.util, math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sohbet import F, W, H, FPS, ease, CREAM, INK, NAVY, GOLD, INTER_M, INTER_SB, INTER_R, CORM, CORM_I, MONO
from kafede import RED, GREEN, SOFT
from kafede_kisa import load_wav, tempo, SR
from sucmu import bg, wrap, TEMPO

GAP = 0.18
SON = 0.9


def timeline(ep, key, sesdir):
    n = 5
    aud = []
    for i in range(n):
        p = os.path.join(sesdir, f'{key}_A_{i:02d}.wav') if sesdir else None
        aud.append(load_wav(p) if p and os.path.exists(p) else None)
    voiced = all(a is not None for a in aud)
    texts = [ep['iddia_ses'], ep['yanlis_ses'], ep['gercek_ses'], ep['bedel_ses'], ep['cta_ses']]
    if voiced:
        aud = [tempo(a, TEMPO) for a in aud]
        durs = [len(a) / SR for a in aud]
    else:
        durs = [max(1.3, 0.36 * len(t.split()) + 0.3) for t in texts]
    t = 0.15
    seg = []
    for i in range(n):
        g = GAP if i != 1 else 0.15
        seg.append(dict(t0=t, d=durs[i])); t += durs[i] + g
    return dict(seg=seg, aud=aud if voiced else None, total=t - GAP + SON, voiced=voiced)


def yanlis_damga(t, t0, a):
    im = Image.new('RGBA', (900, 600), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    p = ease(min(1.0, (t - t0) / 0.28))
    fg = F(CORM, int(240 + 20 * (1 - p)))
    sc = 1.9 - 0.9 * p
    s = 'YANLIŞ'
    tw = fg.getlength(s)
    cx, cy = 450, 300
    # kırmızı damga daire + metin
    rot = -8 * (1 - p)
    tmp = Image.new('RGBA', (int(tw) + 160, fg.size + 100), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    td.rounded_rectangle([20, 20, tmp.width - 20, tmp.height - 20], 36, outline=RED + (int(255 * a),), width=12)
    td.text(((tmp.width - tw) / 2, (tmp.height - fg.size) / 2 - 8), s, font=fg, fill=RED + (int(255 * a),))
    tmp = tmp.rotate(rot, resample=Image.BICUBIC, expand=True)
    sw = int(tmp.width * sc / 2); sh = int(tmp.height * sc / 2)
    if sw < 2 or sh < 2:
        return im
    tmp = tmp.resize((sw * 2, sh * 2), Image.LANCZOS)
    # X çizgileri (ikinci yarıda)
    if p > 0.45:
        q = ease((p - 0.45) / 0.55)
        bx0, by0, bx1, by1 = cx - 240, cy - 160, cx + 240, cy + 160
        d.line([(bx0, by0), (bx0 + (bx1 - bx0) * q, by0 + (by1 - by0) * q)], fill=RED + (int(240 * a),), width=20)
        if q > 0.5:
            r = (q - 0.5) * 2
            d.line([(bx1, by0), (bx1 - (bx1 - bx0) * r, by0 + (by1 - by0) * r)], fill=RED + (int(240 * a),), width=20)
    im.alpha_composite(tmp, (int(cx - tmp.width / 2), int(cy - tmp.height / 2)))
    return im


def compose(t, st):
    ep, tm = st['ep'], st['tm']
    fr = st['bg'].copy()
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    # etiket "HERKES SANIYOR Kİ"
    sg0, sg1 = tm['seg'][0], tm['seg'][1]
    reveal = t >= sg1['t0']
    pr = ease((t - sg1['t0']) / 0.4) if reveal else 0.0
    if pr < 1:
        a0 = 1 - pr
        m = F(MONO, 30)
        et = 'HERKES SANIYOR Kİ'
        tw = m.getlength(et)
        d.rounded_rectangle([540 - tw / 2 - 22, 300, 540 + tw / 2 + 22, 350], 14, fill=(200, 160, 40, int(255 * a0)))
        d.text((540 - tw / 2, 306), et, font=m, fill=INK + (int(255 * a0),))
        # iddia (tırnak içinde, büyük italik)
        fq = F(CORM_I, 72)
        lines = wrap(ep['iddia'], fq, 940)
        while len(lines) > 3 and fq.size > 52:
            fq = F(CORM_I, fq.size - 4); lines = wrap(ep['iddia'], fq, 940)
        yy = 430
        d.text((60, yy - 60), '"', font=F(CORM, 180), fill=GOLD + (int(220 * a0),))
        for l in lines:
            d.text(((W - fq.getlength(l)) / 2, yy), l, font=fq, fill=CREAM + (int(255 * a0),))
            yy += fq.size + 12
        d.text((W - 130, yy - 20), '"', font=F(CORM, 180), fill=GOLD + (int(220 * a0),))
        # geri sayım yok; damga doğrudan
    if reveal:
        # küçük iddia üstte
        a1 = pr
        fq2 = F(CORM_I, 36)
        lines = wrap('"' + ep['iddia'] + '"', fq2, 920)
        yy2 = 240
        for l in lines:
            d.text(((W - fq2.getlength(l)) / 2, yy2), l, font=fq2, fill=CREAM + (int(a1 * 180),))
            yy2 += fq2.size + 4
        # YANLIŞ damgası
        dmg = yanlis_damga(t, sg1['t0'], a1)
        fr.alpha_composite(dmg, (W // 2 - dmg.width // 2, 360))
        # GERÇEK ve BEDEL kartları
        yy = 900
        for idx, (title, body, key_t, key_b, col_bg, col_fg) in enumerate([
            ('GERÇEK', ep['gercek'], 'gercek_ses', 'gercek', (18, 48, 30), GREEN),
            ('BEDELİ', ep['bedel'], 'bedel_ses', 'bedel', (54, 18, 24), RED),
        ]):
            sg = tm['seg'][2 + idx]
            if t < sg['t0']:
                break
            p = ease((t - sg['t0']) / 0.3)
            aa = int(255 * p)
            off = int((1 - p) * 30)
            bt = F(MONO, 28)
            fb = F(INTER_SB, 40)
            body_lines = wrap(body, fb, 900)
            while len(body_lines) > 3 and fb.size > 30:
                fb = F(INTER_SB, fb.size - 2); body_lines = wrap(body, fb, 900)
            h = 44 + 36 + len(body_lines) * (fb.size + 8) + 20
            d.rounded_rectangle([60, yy + off, 1020, yy + h + off], 26, fill=col_bg + (aa,), outline=col_fg + (aa,), width=4)
            d.text((90, yy + 22 + off), title, font=bt, fill=col_fg + (aa,))
            ty = yy + 68 + off
            for l in body_lines:
                d.text((90, ty), l, font=fb, fill=CREAM + (aa,))
                ty += fb.size + 8
            yy += h + 22
        # CTA
        sg = tm['seg'][4]
        if t >= sg['t0']:
            p = ease((t - sg['t0']) / 0.35)
            f_cta = F(INTER_SB, 44)
            lines = wrap(ep['cta'], f_cta, 760)
            h = 50 + len(lines) * 58
            yb = max(yy + 10, 1340) - int(6 * math.sin((t - sg['t0']) * 7))
            aa = int(255 * p)
            d.rounded_rectangle([60, yb, 1020, yb + h], h / 2 if len(lines) == 1 else 40, fill=(255, 255, 255, aa))
            px, py = 130, yb + h / 2
            d.polygon([(px - 34, py - 6), (px + 36, py - 30), (px + 6, py + 34), (px - 2, py + 6)], fill=(40, 120, 255, aa))
            ty = yb + 24
            for l in lines:
                d.text((190, ty), l, font=f_cta, fill=INK + (aa,))
                ty += 58
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

    def thud(t0, vol=0.35):
        m = int(0.25 * SR); tt = np.arange(m) / SR
        add(t0, ((np.sin(2 * np.pi * 70 * tt) * 0.9 + np.random.default_rng(1).normal(0, 0.2, m) * np.exp(-tt * 50)) * np.exp(-tt * 14) * vol).astype(np.float32))
    if tm['aud']:
        for sg, au in zip(tm['seg'], tm['aud']):
            if au is not None:
                add(sg['t0'], au * 0.9)
    thud(tm['seg'][1]['t0'] + 0.0, 0.42)
    tone(tm['seg'][1]['t0'] + 0.02, 440, 220, 0.35, 0.12, 8)
    tone(tm['seg'][2]['t0'] - 0.04, 500, 700, 0.1, 0.06)
    tone(tm['seg'][3]['t0'] - 0.04, 500, 700, 0.1, 0.06)
    pcm = (np.clip(a[:n], -1, 1) * 32767).astype(np.int16)
    with wave.open(path, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


def build(dosya, key, sesdir):
    spec = importlib.util.spec_from_file_location('yanlis_bolum', dosya)
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
        compose(0.4, st).save(a.kapak, quality=92)
    if a.cikti:
        render(st, a.cikti); print('done', a.cikti)


if __name__ == '__main__':
    main()
