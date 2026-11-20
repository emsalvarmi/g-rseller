"""Emsal Var mı? — "Kafede Hukuk" KISA BİÇİM motoru (21.11.2026 talimatı).
Durumla açılır (ilk kareden itibaren büyük "GERÇEK DAVA" kartı), Ayşe ve Mert iki ayrı sesle konuşur,
balonlar ekranda kalır (sesi kapalı izleyenler için), karar erken gelir, sonda karne + künye + uyarılar.

Bölüm verisi: 2026/<tarih>-kafede/kisa.py içindeki KISA sözlüğü (+ aynı klasördeki bolumler.py).
Ses: ses klasöründe <anahtar>_<A|M>_<nn>.wav dosyaları (Mac'teki seslendir_gemini.sh üretir).
     Ses yoksa satır süresi kelime sayısından tahmin edilir (sessiz yedek).

Kullanım:
  python3 kafede_kisa.py b7 --dosya ../../2026/2026-11-21-kafede/kisa.py --ses /yol/ses_gemini --kare 0 3 9 15
  python3 kafede_kisa.py b7 --dosya ... --ses ... --cikti out/reel.mp4 --kapak out/kapak.jpg
"""
import argparse, importlib.util, math, os, subprocess, sys, tempfile, wave
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import karakter as K
import sohbet as S
import kafede as KF
from sohbet import F, W, H, FPS, ease, CREAM, INK, NAVY, GOLD, INTER_M, INTER_SB, INTER_R, CORM, CORM_I, MONO
from kafede import RED, GREEN, SOFT, RENK

SR = 48000
GAP = 0.22          # satırlar arası boşluk (sn)
LEAD = 0.25         # ilk sesin başlangıcı
END = 3.8           # kapanış kartı
STAMP = 1.7         # karar mührünün ekranda kalma süresi
BOTTOM, TOPCLIP = 1010, 480
MAXDUR = 40.0       # bunu aşarsa ses biraz daha hızlandırılır
TEMPO = 1.12        # Gemini sesleri Reels için yavaş; perdeyi bozmadan hızlandırılır


# ---------------------------------------------------------------- ses
def load_wav(path):
    """wav'ı 48 kHz mono float32 olarak okur, baştaki/sondaki sessizliği kırpar."""
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, dtype=np.float32).copy()
    if not len(a):
        return a
    win = int(SR * 0.02)
    env = np.sqrt(np.convolve(a * a, np.ones(win) / win, mode='same'))
    thr = max(0.01, env.max() * 0.04)
    idx = np.where(env > thr)[0]
    if len(idx):
        a = a[max(0, idx[0] - int(0.04 * SR)): min(len(a), idx[-1] + int(0.08 * SR))]
    pk = np.abs(a).max() or 1
    return (a / pk * 0.85).astype(np.float32)


def tempo(a, f):
    if abs(f - 1) < 0.005:
        return a
    with tempfile.TemporaryDirectory() as td:
        i, o = os.path.join(td, 'i.f32'), os.path.join(td, 'o.f32')
        a.tofile(i)
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', i,
                        '-af', f'atempo={f:.3f}', '-f', 'f32le', o], check=True)
        return np.fromfile(o, dtype=np.float32)


def envelope(a):
    """Kare başına ağız açık/kapalı (ses şiddetine göre)."""
    n = int(math.ceil(len(a) / SR * FPS))
    out = []
    step = SR / FPS
    pk = 1e-6
    vals = []
    for k in range(n):
        seg = a[int(k * step): int((k + 1) * step)]
        v = float(np.sqrt(np.mean(seg * seg))) if len(seg) else 0.0
        vals.append(v); pk = max(pk, v)
    for k, v in enumerate(vals):
        out.append(v > pk * 0.22 and (k % 3 != 2 or v > pk * 0.6))
    return out


# ---------------------------------------------------------------- zaman çizelgesi
def timeline(ep, sesdir):
    lines = []
    for i, (spk, goster, ses, rol, durak) in enumerate(ep['satirlar']):
        a = None
        if sesdir:
            p = os.path.join(sesdir, f"{ep['anahtar']}_{spk}_{i:02d}.wav")
            if os.path.exists(p):
                a = load_wav(p)
        lines.append(dict(i=i, who='A' if spk == 'A' else 'B', text=goster, rol=rol, stamp=durak, audio=a))
    voiced = all(l['audio'] is not None for l in lines)
    if sesdir and not voiced:
        eksik = [l['i'] for l in lines if l['audio'] is None]
        print('UYARI: ses dosyası eksik satırlar:', eksik, '— bu satırlar sessiz zamanlanır', file=sys.stderr)

    def dur(l):
        if l['audio'] is not None:
            return len(l['audio']) / SR
        return max(1.6, 0.42 * len((l['text']).split()) + 0.5)

    fac = TEMPO if voiced else 1.0
    for _ in range(4):
        t = LEAD
        for l in lines:
            l['t0'] = t
            l['d'] = dur(l) / fac
            t += l['d'] + (GAP if l['rol'] != 'kanca' else 0.35)
        total = t + 0.45 + END
        if total <= MAXDUR or not voiced:
            break
        fac = min(1.25, fac * total / MAXDUR + 0.01)
    if voiced and fac > 1.0:
        for l in lines:
            l['audio'] = tempo(l['audio'], fac)
            l['d'] = len(l['audio']) / SR
        t = LEAD
        for l in lines:
            l['t0'] = t
            t += l['d'] + (GAP if l['rol'] != 'kanca' else 0.35)
        total = t + 0.45 + END
    for l in lines:
        l['mouth'] = envelope(l['audio']) if l['audio'] is not None else None
    kanca = next(l for l in lines if l['rol'] == 'kanca')
    tm = dict(kanca_end=kanca['t0'] + kanca['d'] + 0.2, end=t + 0.45, total=total, tempo=fac, voiced=voiced)
    return lines, tm


# ---------------------------------------------------------------- katmanlar
def kanca_layout(ep):
    """Kart içeriğinin satırları ve yükseklikleri; kart içeriğe göre boyutlanır."""
    items = []
    for l in ep['kanca']:
        size = 86
        while F(CORM_I, size).getlength(l) > 900 and size > 52:
            size -= 2
        items.append((l, CORM_I, size, CREAM, size + 20))
    size = 108
    while F(CORM, size).getlength(ep['kanca_soru']) > 900 and size > 60:
        size -= 2
    items.append((ep['kanca_soru'], CORM, size, GOLD, size + 30))
    h = 100 + sum(it[4] for it in items) + 70
    return items, h


def kanca_card(t, ep, tm, alpha=None):
    a = 1.0 if alpha is None else alpha
    if alpha is None and t > tm['kanca_end'] - 0.3:
        a = max(0.0, 1 - (t - (tm['kanca_end'] - 0.3)) / 0.4)
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    if a <= 0:
        return ov
    d = ImageDraw.Draw(ov)
    A = lambda v: int(v * a)
    items, ch = kanca_layout(ep)
    top = max(300, 650 - ch / 2)
    d.rectangle([0, 0, W, H], fill=(8, 12, 20, A(110)))
    d.rounded_rectangle([50, top, 1030, top + ch], 38, fill=(10, 14, 22, A(236)), outline=GOLD + (A(210),), width=3)
    m = F(MONO, 34)
    tag = 'GERÇEK DAVA'
    tw = m.getlength(tag)
    d.rounded_rectangle([540 - tw / 2 - 26, top + 34, 540 + tw / 2 + 26, top + 92], 14, fill=RED + (A(255),))
    d.text((540 - tw / 2, top + 41), tag, font=m, fill=(255, 255, 255, A(255)))
    yy = top + 120
    for txt, font, size, col, adv in items:
        f = F(font, size)
        d.text(((W - f.getlength(txt)) / 2, yy), txt, font=f, fill=col + (A(255),))
        yy += adv
    m2 = F(MONO, 24)
    s = 'MERT TAHMİN EDİYOR · SİZ DE EDİN'
    d.text(((W - m2.getlength(s)) / 2, top + ch - 58), s, font=m2, fill=SOFT + (A(255),))
    return ov


def karar_muhru(t, t0, ep, durak):
    if durak is None or t < t0 or t > t0 + STAMP + 0.35:
        return None
    l1, l2, tarih, gun, renk = ep['duraklar'][durak]
    col = RENK[renk]
    p = ease((t - t0) / 0.22)
    a = 1.0 if t < t0 + STAMP else max(0.0, 1 - (t - t0 - STAMP) / 0.35)
    S2 = 2
    fw = F(CORM, 120 * S2)
    fs = F(MONO, 30 * S2)
    w = int(max(fw.getlength(l1), fs.getlength(l2)) + 120 * S2)
    h = 250 * S2
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([8 * S2, 8 * S2, w - 8 * S2, h - 8 * S2], 26 * S2, fill=(250, 246, 238, 235), outline=col + (255,), width=10 * S2)
    d.text(((w - fs.getlength(l2)) / 2, 34 * S2), l2, font=fs, fill=col + (255,))
    d.text(((w - fw.getlength(l1)) / 2, 74 * S2), l1, font=fw, fill=col + (255,))
    sc = (1.55 - 0.55 * p) / S2
    im = im.resize((max(1, int(w * sc)), max(1, int(h * sc))), Image.LANCZOS).rotate(-7, resample=Image.BICUBIC, expand=True)
    if a < 0.999:
        im.putalpha(im.getchannel('A').point(lambda v: int(v * a)))
    return im


def kapanis(t, t0, ep):
    a = ease((t - t0) / 0.45)
    ov = Image.new('RGBA', (W, H), NAVY + (int(250 * a),))
    d = ImageDraw.Draw(ov)
    A = lambda v: int(v * a)
    f = F(CORM, 76)
    s = 'Emsal var mı?'
    d.text(((W - f.getlength(s)) / 2, 330), s, font=f, fill=CREAM + (A(255),))
    m = F(MONO, 26)
    s = 'MERT’İN KARNESİ'
    d.text(((W - m.getlength(s)) / 2, 470), s, font=m, fill=GOLD + (A(255),))
    d.rounded_rectangle([110, 520, 970, 880], 24, fill=(22, 28, 40, A(255)), outline=(70, 80, 100, A(255)), width=2)
    fl, fv = F(MONO, 22), F(INTER_SB, 32)
    rows = [(f'BÖLÜM {ep["no"]}', ep['karne_baslik']), ('TAHMİN', ep['karne_tahmin']), ('YARGITAY', ep['karne_sonuc'])]
    for k, (l, v) in enumerate(rows):
        y = 552 + k * 72
        d.text((146, y + 8), l, font=fl, fill=SOFT + (A(255),))
        size = 32
        fvv = fv
        while fvv.getlength(v) > 440 and size > 20:
            size -= 1; fvv = F(INTER_SB, size)
        d.text((330, y), v, font=fvv, fill=CREAM + (A(255),))
    p = ease((t - t0 - 0.35) / 0.35)
    cx, cy = 890, 624
    if ep['dogru']:
        d.ellipse([cx - 38, cy - 38, cx + 38, cy + 38], fill=GREEN + (A(255 * p),))
        d.line([(cx - 19, cy), (cx - 6, cy + 15), (cx + 21, cy - 15)], fill=(255, 255, 255, A(255 * p)), width=9)
    else:
        d.line([(cx - 32, cy - 32), (cx + 32, cy + 32)], fill=RED + (A(255 * p),), width=12)
        d.line([(cx + 32, cy - 32), (cx - 32, cy + 32)], fill=RED + (A(255 * p),), width=12)
    d.line([(146, 774), (934, 774)], fill=(70, 80, 100, A(255)), width=2)
    ft = F(CORM, 50)
    s2 = f'Toplam: {ep["toplam_dogru"]} doğru · {ep["toplam_yanlis"]} yanlış'
    d.text(((W - ft.getlength(s2)) / 2, 792), s2, font=ft, fill=CREAM + (A(255),))
    r = F(INTER_M, 34)
    s3 = 'Siz ne tahmin etmiştiniz? Yorumlara yazın.'
    while r.getlength(s3) > 960:
        r = F(INTER_M, r.size - 1)
    d.text(((W - r.getlength(s3)) / 2, 930), s3, font=r, fill=GOLD + (A(255),))
    mm = F(MONO, 21)
    yy = 1040
    for s4 in ep['kunyeler']:
        d.text(((W - mm.getlength(s4)) / 2, yy), s4, font=mm, fill=(178, 186, 198, A(255)))
        yy += 34
    rn = F(INTER_R, 24)
    for s5 in [ep['kalp_not'], 'Genel bilgilendirme amaçlıdır; hukuki görüş değildir.',
               'Karakterler temsilîdir; dosyanın tarafları değildir.']:
        while rn.getlength(s5) > 980:
            rn = F(INTER_R, rn.size - 1)
        d.text(((W - rn.getlength(s5)) / 2, yy + 22), s5, font=rn, fill=SOFT + (A(255),))
        yy += 38
    return ov


# ---------------------------------------------------------------- kare
def compose(t, st):
    lines, tm, ep = st['lines'], st['tm'], st['ep']
    A, B = st['A'], st['B']
    fr = st['base'].copy()
    talking, mouth_open = None, False
    for l in lines:
        if l['t0'] <= t < l['t0'] + l['d']:
            talking = l['who']
            if l['mouth'] is not None:
                k = int((t - l['t0']) * FPS)
                mouth_open = l['mouth'][min(k, len(l['mouth']) - 1)]
            else:
                mouth_open = int(t * 7.5) % 2 == 0
    for who, k in (('A', A), ('B', B)):
        br = math.sin(t * 2 * math.pi / 4.2 + (0 if who == 'A' else 1.7)) * 2.5
        fr.alpha_composite(k.govde, (k.ox, int(k.oy + br)))
        mouth, tilt = 'kapali', 0.0
        if talking == who:
            mouth = 'acik' if mouth_open else 'kapali'
            tilt = 2.2 * k.p['d']
        elif talking:
            tilt = -0.8 * k.p['d']
        head = k.heads[('kapali' if k.blink(t) else 'acik', mouth)]
        if abs(tilt) > 0.01:
            head = head.rotate(-tilt, resample=Image.BICUBIC, center=(K.HX, 290))
        fr.alpha_composite(head, (k.ox, int(k.oy + br * 1.2)))
    fr.alpha_composite(st['tbl'])
    fr.alpha_composite(A.kol, (A.ox, A.oy))
    fr.alpha_composite(B.kol, (B.ox, B.oy))
    fr.alpha_composite(st['prp'])
    fr.alpha_composite(st['chips'])
    lt = next(l for l in lines if l['rol'] == 'tahmin')
    ls = next(l for l in lines if l['rol'] == 'sonuc')
    if t >= lt['t0']:
        p = ease((t - lt['t0']) / 0.35)
        stk = KF.tahmin_sticker(ep['tahmin'], max(0.0, (t - ls['t0'] - 0.5) / 0.6), ep['dogru'])
        if p < 1:
            stk = stk.resize((max(1, int(stk.width * (0.6 + 0.4 * p))), max(1, int(stk.height * (0.6 + 0.4 * p)))), Image.BICUBIC)
        fr.alpha_composite(stk, (int(540 - stk.width / 2), int(1325 - stk.height / 2)))
    # balonlar (kanca satırı balon olmaz; kart onu taşır)
    slots = []
    for l in lines:
        if l['rol'] == 'kanca' or t < l['t0']:
            continue
        bi = st['bubbles'][l['i']]
        p = (t - l['t0']) / 0.28
        hh = 116 + (bi.height - 116) * ease(p)
        slots.append((l, bi, hh, min(1.0, 0.25 + 0.75 * ease(p)), 0.9 + 0.1 * ease(p)))
    y = BOTTOM
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for l, im, hh, al, sc in reversed(slots):
        y -= hh
        top = y
        y -= 18
        if top + hh < TOPCLIP - 60:
            break
        a = al * max(0.0, min(1.0, (top - (TOPCLIP - 70)) / 70))
        if a <= 0.01:
            continue
        img = im
        if sc < 0.999:
            img = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BICUBIC)
        if a < 0.999:
            img = img.copy()
            img.putalpha(img.getchannel('A').point(lambda v: int(v * a)))
        x = S.LX if l['who'] == 'A' else S.RXB - img.width
        layer.alpha_composite(img, (int(x), int(top + (hh - img.height))))
    fr.alpha_composite(layer)
    # şerit (kanca bitince belirir)
    sa = ease((t - tm['kanca_end'] - 0.05) / 0.4)
    if sa > 0:
        ev = st['strip_ev']
        strip = Image.alpha_composite(st['strip'], KF.strip_layer(t, ev, ep))
        if sa < 0.999:
            strip.putalpha(strip.getchannel('A').point(lambda v: int(v * sa)))
        fr.alpha_composite(strip)
    fr.alpha_composite(st['hdr'])
    m = karar_muhru(t, ls['t0'] + 0.1, ep, ls['stamp'])
    if m is not None:
        fr.alpha_composite(m, (int(540 - m.width / 2), int(700 - m.height / 2)))
    if t < tm['kanca_end'] + 0.15:
        fr.alpha_composite(kanca_card(t, ep, tm))
    if t >= tm['end']:
        fr.alpha_composite(kapanis(t, tm['end'], ep))
    return fr.convert('RGB')


def build(ep, sesdir):
    lines, tm = timeline(ep, sesdir)
    st = dict(ep=ep, lines=lines, tm=tm, base=KF.background(ep['saat']), tbl=S.table(), prp=S.props(),
              hdr=KF.header(ep), strip=KF.strip_base(ep), chips=KF.name_chips())
    st['A'] = S.Kisi(K.KADIN, 70, 950, None)
    st['B'] = S.Kisi(K.ERKEK, 530, 950, None)
    st['bubbles'] = {l['i']: S.bubble_img(l['who'], l['text']) for l in lines if l['rol'] != 'kanca'}
    # şerit durakları: ilk durak şeritle yanar; bir satır birden çok durağı atlıyorsa aradakiler satır boyunca sırayla yanar
    ev, last = [], -1
    if not any(l['stamp'] == 0 for l in lines):
        ev.append(dict(stamp=0, t_show=tm['kanca_end'] + 0.1)); last = 0
    for l in lines:
        k = l['stamp']
        if k is None or k <= last:
            continue
        span = k - last
        for j in range(last + 1, k + 1):
            frac = (j - last - 1) / span
            ev.append(dict(stamp=j, t_show=l['t0'] + frac * l['d'] * 0.85))
        last = k
    st['strip_ev'] = ev
    return st


def mix(st, path):
    lines, tm, ep = st['lines'], st['tm'], st['ep']
    n = int(SR * tm['total']) + SR
    a = np.zeros(n, dtype=np.float32)

    def add(t0, s):
        i0 = int(t0 * SR)
        m = max(0, min(len(s), n - i0))
        a[i0:i0 + m] += s[:m]

    def tone(t0, f0, f1, dur, vol, decay=38):
        m = int(dur * SR)
        tt = np.arange(m) / SR
        f = np.linspace(f0, f1, m)
        add(t0, (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * decay) * (1 - np.exp(-tt * 900)) * vol).astype(np.float32))

    def thud(t0, vol=0.22):
        m = int(0.2 * SR)
        tt = np.arange(m) / SR
        rng = np.random.default_rng(int(t0 * 100))
        add(t0, ((np.sin(2 * np.pi * 90 * tt) * 0.8 + rng.normal(0, 0.25, m) * np.exp(-tt * 60)) * np.exp(-tt * 20) * vol).astype(np.float32))
    for l in lines:
        if l['audio'] is not None:
            add(l['t0'], l['audio'] * 0.9)
        if l['rol'] != 'kanca':
            tone(l['t0'], 900 if l['who'] == 'A' else 700, 640 if l['who'] == 'A' else 520, 0.08, 0.06)
        if l['rol'] == 'sonuc':
            thud(l['t0'] + 0.1, 0.30)
    tone(0.02, 520, 780, 0.22, 0.08, 20)
    tone(tm['end'] + 0.35, 520 if ep['dogru'] else 300, 780 if ep['dogru'] else 220, 0.25, 0.10, 14)
    a = a[:int(SR * tm['total'])]
    pcm = (np.clip(a, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def render(ep, sesdir, out):
    st = build(ep, sesdir)
    tm = st['tm']
    tmp = out[:-4] + '.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                          '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16',
                          '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    for i in range(int(round(tm['total'] * FPS))):
        p.stdin.write(compose(i / FPS, st).tobytes())
    p.stdin.close()
    if p.wait() != 0:
        sys.exit('ffmpeg hata')
    wav = out[:-4] + '.wav'
    mix(st, wav)
    tmp2 = out[:-4] + '.tmp2.mp4'
    r = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-i', wav, '-map', '0:v', '-map', '1:a',
                        '-c:v', 'copy', '-af', 'loudnorm=I=-15:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '160k',
                        '-shortest', '-movflags', '+faststart', tmp2])
    if r.returncode != 0:
        sys.exit('ses ekleme hata')
    os.replace(tmp2, out)
    os.remove(tmp)
    os.remove(wav)
    return st


def kapak(st, path):
    """Kapak = ilk saniyedeki kanca kartı (sahne görünür, kart tam opak)."""
    st['tm_k'] = st['tm']
    compose(min(0.6, st['tm']['kanca_end'] - 0.5), st).save(path, quality=92)


def yukle(dosya, anahtar):
    spec = importlib.util.spec_from_file_location('kisa_bolum', dosya)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.bolum(anahtar)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('bolum')
    ap.add_argument('--dosya', required=True, help='kisa.py yolu (KISA sözlüğü ve bolum() işlevi)')
    ap.add_argument('--ses', help='seslendirme wav klasörü (yoksa sessiz yedek)')
    ap.add_argument('--kare', nargs='*', type=float)
    ap.add_argument('--cikti')
    ap.add_argument('--kapak')
    a = ap.parse_args()
    ep = yukle(a.dosya, a.bolum)
    st = build(ep, a.ses)
    tm = st['tm']
    print('süre: %.1f sn | sesli: %s | tempo: %.2f' % (tm['total'], tm['voiced'], tm['tempo']),
          [(l['i'], l['who'], round(l['t0'], 1), round(l['d'], 1)) for l in st['lines']])
    if a.kare:
        for t in a.kare:
            compose(t, st).save(f'{a.bolum}_{t:05.1f}.png')
    if a.kapak:
        kapak(st, a.kapak)
    if a.cikti:
        render(ep, a.ses, a.cikti)
        print('done', a.cikti)


if __name__ == '__main__':
    main()
