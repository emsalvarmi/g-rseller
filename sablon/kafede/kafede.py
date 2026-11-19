"""Emsal Var mı? — "Kafede Hukuk" dizisi motoru (seslendirmesiz, konuşma balonlu).
Bir bölüm, bolumler.py içindeki sözlükle tanımlanır.
Kullanım: python3 kafede.py <bolum_anahtari> --kare 10 20   |   python3 kafede.py <anahtar> --cikti x.mp4
"""
import argparse, math, os, random, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import karakter as K
import sohbet as S
from sohbet import F, W, H, FPS, ease, CREAM, INK, NAVY, GOLD, INTER_M, INTER_SB, INTER_R, CORM, CORM_I, MONO

RED = (196, 70, 60)
BLUE = (110, 160, 200)
GREEN = (96, 170, 120)
SOFT = (150, 160, 175)
RENK = dict(gri=SOFT, kirmizi=RED, altin=GOLD, mavi=BLUE, yesil=GREEN)

INTRO, TYPE = 3.0, 0.55
KALP, KARNE, OUTRO = 4.6, 3.2, 3.0
BOTTOM, TOPCLIP = 1010, 480
HEDEF = 60.4

# ---------------------------------------------------------------- günün saatine göre sahne
SAAT = {
    'sabah': dict(top=(60, 64, 84), bot=(92, 90, 100), win=(176, 204, 228), win2=(250, 222, 196),
                  lights=[(255, 246, 225), (255, 226, 190), (255, 210, 170)], la=(50, 110), glow=(255, 226, 180, 80)),
    'ogle': dict(top=(58, 70, 86), bot=(90, 96, 104), win=(120, 170, 220), win2=(190, 214, 236),
                 lights=[(255, 255, 255), (235, 245, 255), (255, 244, 220)], la=(50, 110), glow=(255, 244, 220, 60)),
    'aksamustu': dict(top=(40, 34, 46), bot=(66, 50, 50), win=(230, 140, 90), win2=(120, 70, 100),
                      lights=[(255, 190, 120), (255, 150, 90), (250, 210, 160)], la=(50, 120), glow=(255, 170, 100, 80)),
    'gece': dict(top=(16, 22, 34), bot=(30, 34, 44), win=(24, 34, 52), win2=(24, 34, 52),
                 lights=[(232, 186, 110), (240, 210, 150), (120, 170, 200), (220, 140, 90)], la=(40, 110), glow=(255, 190, 110, 60)),
}


def background(saat):
    p = SAAT[saat]
    y = np.linspace(0, 1, H)[:, None]
    top, bot = np.array(p['top']), np.array(p['bot'])
    g = (top + (bot - top) * y).astype(np.float32)
    bg = Image.fromarray(np.repeat(g[:, None, :], W, axis=1).clip(0, 255).astype(np.uint8)).convert('RGBA')
    # pencere: gökyüzü degradesi
    wy = np.linspace(0, 1, 1220)[:, None]
    w1, w2 = np.array(p['win2']), np.array(p['win'])
    wg = (w1 + (w2 - w1) * wy).astype(np.float32)
    sky = Image.fromarray(np.repeat(wg[:, None, :], 960, axis=1).clip(0, 255).astype(np.uint8)).convert('RGBA')
    win = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    win.paste(sky, (60, 250))
    rnd = random.Random(7)
    lights = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lights)
    for _ in range(70):
        x, yy = rnd.uniform(80, 1000), rnd.uniform(700, 1460)
        r = rnd.uniform(14, 46)
        col = rnd.choice(p['lights'])
        ld.ellipse([x - r, yy - r, x + r, yy + r], fill=col + (rnd.randint(*p['la']),))
    if saat in ('sabah', 'ogle'):
        # uzak bina siluetleri
        sd = ImageDraw.Draw(win)
        for i in range(14):
            bx = 60 + i * 70 + rnd.uniform(-10, 10)
            bh = rnd.uniform(160, 420)
            sd.rectangle([bx, 1470 - bh, bx + rnd.uniform(50, 80), 1470], fill=(150, 170, 190, 110))
    win.alpha_composite(lights.filter(ImageFilter.GaussianBlur(14)))
    mask = Image.new('L', (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle([60, 250, 1020, 1470], 40, fill=255)
    win.putalpha(Image.fromarray(np.minimum(np.array(win.getchannel('A')), np.array(mask))))
    bg.alpha_composite(win)
    fr = ImageDraw.Draw(bg)
    frame = tuple(int(c * 0.8) for c in p['bot']) + (255,)
    fr.rounded_rectangle([60, 250, 1020, 1470], 40, outline=frame, width=6)
    fr.line([(540, 250), (540, 1470)], fill=frame, width=6)
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([140, 1180, 940, 1760], fill=p['glow'])
    bg.alpha_composite(glow.filter(ImageFilter.GaussianBlur(90)))
    return bg


# ---------------------------------------------------------------- zaman çizelgesi
def timeline(ep):
    for fac in (0.25, 0.24, 0.23, 0.22, 0.21):
        t = INTRO
        ev = []
        for i, d in enumerate(ep['diyalog']):
            who, tx = d[0], d[1]
            hold = max(1.8, min(4.6, 0.85 + fac * len(tx.split())))
            ev.append(dict(i=i, who=who, text=tx, t_type=t, t_show=t + TYPE, stamp=d[2], special=d[3]))
            t += TYPE + hold
        tm = dict(kalp=t + 0.3)
        tm['karne'] = tm['kalp'] + KALP
        tm['out'] = tm['karne'] + KARNE
        tm['total'] = tm['out'] + OUTRO
        if tm['total'] <= HEDEF:
            break
    return ev, tm


# ---------------------------------------------------------------- katmanlar
def header(ep):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = F(CORM, 40)
    t = 'E M S A L   V A R   M I ?'
    d.text(((W - f.getlength(t)) / 2, 64), t, font=f, fill=GOLD + (255,))
    m = F(MONO, 20)
    t2 = f'KAFEDE HUKUK · BÖLÜM {ep["no"]}'
    d.text(((W - m.getlength(t2)) / 2, 116), t2, font=m, fill=(200, 206, 216, 255))
    return im


def node_x(n):
    return [128 + k * (824 / (n - 1)) for k in range(n)]


NODE_Y = 280


def strip_base(ep):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([36, 160, 1044, 410], 26, fill=(12, 17, 26, 228), outline=(60, 70, 90, 255), width=2)
    d.text((68, 182), 'DOSYANIN YOLCULUĞU', font=F(MONO, 24), fill=GOLD + (255,))
    xs = node_x(len(ep['duraklar']))
    d.line([(xs[0], NODE_Y), (xs[-1], NODE_Y)], fill=(70, 80, 100, 255), width=3)
    for x in xs:
        d.ellipse([x - 13, NODE_Y - 13, x + 13, NODE_Y + 13], fill=(22, 28, 40, 255), outline=(80, 90, 110, 255), width=3)
    return im


def gun_yazi(g):
    y, r = divmod(g, 365)
    ay = int(r / 30.44)
    if y and ay:
        return f'{y} YIL {ay} AY'
    if y:
        return f'{y} YIL'
    return f'{ay} AY' if ay else ''


def strip_layer(t, ev, ep):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    dur = ep['duraklar']
    xs = node_x(len(dur))
    times = {e['stamp']: e['t_show'] for e in ev if e['stamp'] is not None}
    active = [k for k in range(len(dur)) if k in times and t >= times[k]]
    if active:
        last = max(active)
        p = ease((t - times[last]) / 0.6)
        x_prev = xs[last - 1] if last > 0 else xs[0]
        d.line([(xs[0], NODE_Y), (x_prev + (xs[last] - x_prev) * p, NODE_Y)], fill=GOLD + (255,), width=4)
    fl, fd = F(MONO, 22), F(MONO, 19)
    for k, (l1, l2, tarih, gun, renk) in enumerate(dur):
        x, col, on = xs[k], RENK[renk], k in active
        a = 255 if on else 90
        if on:
            p = ease((t - times[k]) / 0.45)
            r = 13 + (1 - p) * 16
            d.ellipse([x - r, NODE_Y - r, x + r, NODE_Y + r], fill=col + (int(255 * p),))
            if p < 1:
                rr = 13 + p * 30
                d.ellipse([x - rr, NODE_Y - rr, x + rr, NODE_Y + rr], outline=col + (int(200 * (1 - p)),), width=3)
        for j, s in enumerate([l1, l2]):
            if s:
                d.text((x - fl.getlength(s) / 2, 310 + j * 26), s, font=fl, fill=(col if on else SOFT) + (a,))
        d.text((x - fd.getlength(tarih) / 2, 368), tarih, font=fd, fill=SOFT + (a,))
    # süre sayacı (yalnızca tam tarihli duraklar)
    known = [k for k in active if dur[k][3] is not None]
    g = 0
    if known:
        last = max(known)
        prev = dur[max(known[:-1])][3] if len(known) > 1 else 0
        p = ease((t - times[last]) / 0.9)
        g = int(round(prev + (dur[last][3] - prev) * p))
    s = f'GEÇEN SÜRE  {g:,}'.replace(',', '.') + ' GÜN'
    fm = F(MONO, 24)
    d.text((1012 - fm.getlength(s), 180), s, font=fm, fill=CREAM + (255,))
    s2 = gun_yazi(g)
    if s2:
        fs = F(MONO, 19)
        d.text((1012 - fs.getlength('≈ ' + s2), 214), '≈ ' + s2, font=fs, fill=SOFT + (255,))
    return im


def name_chips():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = F(MONO, 22)
    for name, cx in (('AYŞE', 296), ('MERT', 784)):
        tw = f.getlength(name)
        d.rounded_rectangle([cx - tw / 2 - 16, 1420, cx + tw / 2 + 16, 1458], 19, fill=(12, 17, 26, 200))
        d.text((cx - tw / 2, 1427), name, font=f, fill=CREAM + (255,))
    return im


def tahmin_sticker(label, sonuc_p, dogru):
    S2 = 2
    w, h = 300, 116
    im = Image.new('RGBA', (w * S2, h * S2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w * S2 - 1, h * S2 - 1], 18 * S2, fill=(236, 217, 168, 255))
    f1 = F(MONO, 18 * S2)
    t1 = 'MERT’İN TAHMİNİ'
    d.text(((w * S2 - f1.getlength(t1)) / 2, 12 * S2), t1, font=f1, fill=(110, 90, 50))
    size = 50
    while size > 24 and F(CORM, size * S2).getlength(label) > (w - 30) * S2:
        size -= 2
    f2 = F(CORM, size * S2)
    d.text(((w * S2 - f2.getlength(label)) / 2, (34 + (50 - size) * 0.5) * S2), label, font=f2, fill=INK)
    if sonuc_p > 0:
        p = ease(sonuc_p)
        if dogru:
            # yeşil onay halkası
            d.rounded_rectangle([4 * S2, 4 * S2, (w - 4) * S2, (h - 4) * S2], 16 * S2, outline=GREEN + (int(255 * p),), width=7 * S2)
            cx, cy = (w - 34) * S2, 30 * S2
            d.ellipse([cx - 22 * S2, cy - 22 * S2, cx + 22 * S2, cy + 22 * S2], fill=GREEN + (int(255 * p),))
            d.line([(cx - 11 * S2, cy), (cx - 3 * S2, cy + 9 * S2), (cx + 12 * S2, cy - 9 * S2)], fill=(255, 255, 255, int(255 * p)), width=5 * S2)
        else:
            x0, y0, x1, y1 = 40 * S2, 22 * S2, (w - 40) * S2, (h - 18) * S2
            q1 = min(1, p * 2)
            d.line([(x0, y0), (x0 + (x1 - x0) * q1, y0 + (y1 - y0) * q1)], fill=RED + (235,), width=10 * S2)
            if p > 0.5:
                q = (p - 0.5) * 2
                d.line([(x1, y0), (x1 - (x1 - x0) * q, y0 + (y1 - y0) * q)], fill=RED + (235,), width=10 * S2)
    im = im.resize((w, h), Image.LANCZOS)
    return im.rotate(6, resample=Image.BICUBIC, expand=True)


def kalp_layout(ep):
    f = F('LibreCaslonText_400Regular.ttf', 36)
    words = ep['kalp_metin'].split()
    vurgu = ep['kalp_vurgu'].split()
    hi = set()
    norm = lambda w: w.strip('.,;:…')
    for i in range(len(words) - len(vurgu) + 1):
        if [norm(w) for w in words[i:i + len(vurgu)]] == [norm(v) for v in vurgu]:
            hi = set(range(i, i + len(vurgu)))
            break
    assert hi, 'vurgu metinde bulunamadı'
    x0, maxw, lh = 120, 840, 56
    pos, x, y = [], x0, 0
    sp = f.getlength(' ')
    for i, w in enumerate(words):
        ww = f.getlength(w)
        if x + ww > x0 + maxw:
            x, y = x0, y + lh
        pos.append((w, x, y, ww, i in hi))
        x += ww + sp
    return f, pos, y + lh


def kalp_card(t, t0, ep, lay):
    a = ease((t - t0) / 0.5)
    ov = Image.new('RGBA', (W, H), (10, 14, 22, int(242 * a)))
    d = ImageDraw.Draw(ov)
    m = F(MONO, 30)
    s = 'KARARIN KALBİ'
    d.text(((W - m.getlength(s)) / 2, 404), s, font=m, fill=GOLD + (int(255 * a),))
    m2 = F(MONO, 21)
    s2 = ep['kalp_kaynak']
    d.text(((W - m2.getlength(s2)) / 2, 452), s2, font=m2, fill=SOFT + (int(255 * a),))
    f, pos, th = lay
    top = 540
    d.rounded_rectangle([80, top - 40, 1000, top + th + 40], 20, fill=(246, 241, 231, int(255 * a)))
    hp = max(0.0, min(1.0, (t - t0 - 0.9) / 1.4))
    hl = [p for p in pos if p[4]]
    total_w = sum(p[3] for p in hl) or 1
    done = 0
    for w, x, y, ww, h in hl:
        frac = max(0.0, min(1.0, (hp * total_w - done) / ww))
        if frac > 0:
            d.rectangle([x - 4, top + y + 6, x + (ww + 8) * frac - 4, top + y + 48], fill=(244, 206, 98, int(230 * a)))
        done += ww
    for w, x, y, ww, h in pos:
        d.text((x, top + y), w, font=f, fill=(INK if h else (90, 92, 98)) + (int(255 * a),))
    r = F(INTER_R, 24)
    s3 = ep['kalp_not']
    d.text(((W - r.getlength(s3)) / 2, top + th + 80), s3, font=r, fill=SOFT + (int(255 * a),))
    return ov


def karne_card(t, t0, ep):
    a = ease((t - t0) / 0.4)
    ov = Image.new('RGBA', (W, H), (10, 14, 22, 242))
    d = ImageDraw.Draw(ov)
    m = F(MONO, 26)
    s = 'MERT’İN KARNESİ'
    d.text(((W - m.getlength(s)) / 2, 466), s, font=m, fill=GOLD + (int(255 * a),))
    d.rounded_rectangle([90, 530, 990, 1010], 24, fill=(22, 28, 40, int(255 * a)), outline=(70, 80, 100, int(255 * a)), width=2)
    fl, fv = F(MONO, 22), F(INTER_SB, 33)
    rows = [(f'BÖLÜM {ep["no"]}', ep['karne_baslik']), ('TAHMİN', ep['karne_tahmin']), ('YARGITAY', ep['karne_sonuc'])]
    for k, (l, v) in enumerate(rows):
        y = 572 + k * 92
        d.text((130, y + 8), l, font=fl, fill=SOFT + (int(255 * a),))
        fvv = fv
        size = 33
        while fvv.getlength(v) > 470 and size > 22:
            size -= 1
            fvv = F(INTER_SB, size)
        d.text((330, y), v, font=fvv, fill=CREAM + (int(255 * a),))
    p = ease((t - t0 - 0.5) / 0.4)
    cx, cy = 900, 664
    if ep['dogru']:
        d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=GREEN + (int(255 * p * a),))
        d.line([(cx - 20, cy), (cx - 6, cy + 16), (cx + 22, cy - 16)], fill=(255, 255, 255, int(255 * p * a)), width=9)
    else:
        d.line([(cx - 34, cy - 34), (cx + 34, cy + 34)], fill=RED + (int(255 * p * a),), width=12)
        d.line([(cx + 34, cy - 34), (cx - 34, cy + 34)], fill=RED + (int(255 * p * a),), width=12)
    d.line([(130, 860), (950, 860)], fill=(70, 80, 100, int(255 * a)), width=2)
    ft = F(CORM, 54)
    s2 = f'Toplam: {ep["toplam_dogru"]} doğru · {ep["toplam_yanlis"]} yanlış'
    d.text(((W - ft.getlength(s2)) / 2, 888), s2, font=ft, fill=CREAM + (int(255 * a),))
    r = F(INTER_M, 30)
    s3 = 'Siz ne tahmin etmiştiniz? Yorumlara yazın.'
    d.text(((W - r.getlength(s3)) / 2, 1060), s3, font=r, fill=GOLD + (int(255 * a * ease((t - t0 - 0.9) / 0.5)),))
    return ov


def outro(t, t0, ep):
    a = ease((t - t0) / 0.6)
    ov = Image.new('RGBA', (W, H), NAVY + (255,))
    d = ImageDraw.Draw(ov)
    f = F(CORM, 96)
    s = 'Emsal var mı?'
    d.text(((W - f.getlength(s)) / 2, 640), s, font=f, fill=CREAM + (int(255 * a),))
    f2 = F(CORM_I, 56)
    s2 = 'Kararı bil, hakkını bil.'
    d.text(((W - f2.getlength(s2)) / 2, 760), s2, font=f2, fill=GOLD + (int(255 * a),))
    m = F(MONO, 21)
    for k, s3 in enumerate(ep['kunyeler']):
        d.text(((W - m.getlength(s3)) / 2, 890 + k * 36), s3, font=m, fill=(170, 178, 190, int(255 * a)))
    r = F(INTER_R, 25)
    yy = 890 + len(ep['kunyeler']) * 36 + 70
    for k, s4 in enumerate(['Genel bilgilendirme amaçlıdır; hukuki görüş değildir.',
                            'Karakterler temsilîdir; dosyanın tarafları değildir.']):
        d.text(((W - r.getlength(s4)) / 2, yy + k * 38), s4, font=r, fill=SOFT + (int(255 * a),))
    return ov


def intro(t, ep):
    a = 1.0 if t < INTRO - 0.6 else max(0.0, 1 - (t - (INTRO - 0.6)) / 0.8)
    ov = Image.new('RGBA', (W, H), (10, 14, 22, int(225 * a)))
    d = ImageDraw.Draw(ov)
    yy = 600
    for k, l in enumerate(ep['soru']):
        size = 92
        while F(CORM_I, size).getlength(l) > 980 and size > 60:
            size -= 2
        f = F(CORM_I, size)
        al = a * ease((t - k * 0.45) / 0.5)
        d.text(((W - f.getlength(l)) / 2, yy), l, font=f, fill=(GOLD if k == len(ep['soru']) - 1 else CREAM) + (int(255 * al),))
        yy += 112
    m = F(MONO, 24)
    s = 'MERT TAHMİN EDECEK. SİZ DE EDİN.'
    d.text(((W - m.getlength(s)) / 2, yy + 40), s, font=m, fill=SOFT + (int(255 * a * ease((t - 1.4) / 0.5)),))
    return ov


# ---------------------------------------------------------------- kare
def compose(t, st):
    ev, tm, ep = st['ev'], st['tm'], st['ep']
    A, B = st['A'], st['B']
    fr = st['base'].copy()
    talking = None
    for e in ev:
        if e['t_type'] <= t < e['t_show'] + 0.7:
            talking = e['who']
    for who, k in (('A', A), ('B', B)):
        br = math.sin(t * 2 * math.pi / 4.2 + (0 if who == 'A' else 1.7)) * 2.5
        fr.alpha_composite(k.govde, (k.ox, int(k.oy + br)))
        mouth, tilt = 'kapali', 0.0
        if talking == who:
            mouth = 'acik' if int(t * 7.5) % 2 == 0 else 'kapali'
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
    et = next(e for e in ev if e['special'] == 'tahmin')
    es = next(e for e in ev if e['special'] == 'sonuc')
    if t >= et['t_show']:
        p = ease((t - et['t_show']) / 0.35)
        stk = tahmin_sticker(ep['tahmin'], max(0.0, (t - es['t_show'] - 0.3) / 0.6), ep['dogru'])
        if p < 1:
            stk = stk.resize((max(1, int(stk.width * (0.6 + 0.4 * p))), max(1, int(stk.height * (0.6 + 0.4 * p)))), Image.BICUBIC)
        fr.alpha_composite(stk, (int(540 - stk.width / 2), int(1325 - stk.height / 2)))
    slots = []
    for e in ev:
        if t < e['t_type']:
            break
        bi = st['bubbles'][e['i']]
        if t < e['t_show']:
            ti = S.typing_img(e['who'], t)
            g = ease((t - e['t_type']) / 0.25)
            slots.append((e, ti, ti.height * g, 1.0, g))
        else:
            p = (t - e['t_show']) / 0.32
            hh = 116 + (bi.height - 116) * ease(p)
            slots.append((e, bi, hh, min(1.0, 0.25 + 0.75 * ease(p)), 0.9 + 0.1 * ease(p)))
    y = BOTTOM
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for e, im, hh, al, sc in reversed(slots):
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
        x = S.LX if e['who'] == 'A' else S.RXB - img.width
        layer.alpha_composite(img, (int(x), int(top + (hh - img.height))))
    fr.alpha_composite(layer)
    fr.alpha_composite(st['strip'])
    fr.alpha_composite(strip_layer(t, ev, ep))
    fr.alpha_composite(st['hdr'])
    if t < INTRO + 0.3:
        fr.alpha_composite(intro(t, ep))
    if tm['kalp'] <= t < tm['karne'] + 0.4:
        fr.alpha_composite(kalp_card(t, tm['kalp'], ep, st['kalp']))
    if tm['karne'] <= t < tm['out'] + 0.6:
        fr.alpha_composite(karne_card(t, tm['karne'], ep))
    if t >= tm['out']:
        fr.alpha_composite(outro(t, tm['out'], ep))
    return fr.convert('RGB')


def build(ep):
    ev, tm = timeline(ep)
    st = dict(ep=ep, ev=ev, tm=tm, base=background(ep['saat']), tbl=S.table(), prp=S.props(), hdr=header(ep),
              strip=strip_base(ep), chips=name_chips(), kalp=kalp_layout(ep))
    st['A'] = S.Kisi(K.KADIN, 70, 950, None)
    st['B'] = S.Kisi(K.ERKEK, 530, 950, None)
    st['bubbles'] = {e['i']: S.bubble_img(e['who'], e['text']) for e in ev}
    return st


def sesler(st, path):
    ev, tm = st['ev'], st['tm']
    sr = 48000
    n = int(sr * tm['total'])
    a = np.zeros(n, dtype=np.float32)

    def tone(t0, f0, f1, dur, vol, decay=38):
        i0, m = int(t0 * sr), int(dur * sr)
        tt = np.arange(m) / sr
        f = np.linspace(f0, f1, m)
        s = np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-tt * decay) * (1 - np.exp(-tt * 900)) * vol
        a[i0:i0 + m] += s[:max(0, min(m, n - i0))]

    def thud(t0, vol=0.22):
        i0, m = int(t0 * sr), int(0.18 * sr)
        tt = np.arange(m) / sr
        rng = np.random.default_rng(int(t0 * 100))
        s = (np.sin(2 * np.pi * 95 * tt) * 0.8 + rng.normal(0, 0.25, m) * np.exp(-tt * 60)) * np.exp(-tt * 22) * vol
        a[i0:i0 + m] += s[:max(0, min(m, n - i0))]
    for e in ev:
        tone(e['t_show'], 900 if e['who'] == 'A' else 700, 640 if e['who'] == 'A' else 520, 0.09, 0.15)
        if e['stamp'] is not None:
            thud(e['t_show'] + 0.05)
    tone(0.15, 520, 780, 0.22, 0.10, 20)
    thud(tm['kalp'] + 0.1, 0.15)
    tone(tm['karne'] + 0.5, 520 if st['ep']['dogru'] else 300, 780 if st['ep']['dogru'] else 220, 0.25, 0.12, 14)
    tone(tm['out'], 660, 440, 0.35, 0.10, 12)
    pcm = (np.clip(a, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def render(ep, out):
    st = build(ep)
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
    sesler(st, wav)
    tmp2 = out[:-4] + '.tmp2.mp4'
    r = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-i', wav, '-map', '0:v', '-map', '1:a',
                        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', tmp2])
    if r.returncode != 0:
        sys.exit('ses ekleme hata')
    os.replace(tmp2, out)
    os.remove(tmp)
    os.remove(wav)
    return st


def kapak(ep, path):
    """Kapak: aydınlık kafe sahnesi + üst bölümde soru kartı + bölüm etiketi."""
    st = build(ep)
    fr = compose(INTRO + 0.32, st).convert('RGBA')
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rounded_rectangle([60, 470, 1020, 1010], 36, fill=(10, 14, 22, 228), outline=GOLD + (200,), width=3)
    m = F(MONO, 26)
    s = f'KAFEDE HUKUK · BÖLÜM {ep["no"]}'
    d.text(((W - m.getlength(s)) / 2, 510), s, font=m, fill=GOLD + (255,))
    yy = 590
    for k, l in enumerate(ep['soru']):
        size = 80
        while F(CORM_I, size).getlength(l) > 900 and size > 50:
            size -= 2
        f = F(CORM_I, size)
        d.text(((W - f.getlength(l)) / 2, yy), l, font=f, fill=(GOLD if k == len(ep['soru']) - 1 else CREAM) + (255,))
        yy += 104
    s2 = 'MERT TAHMİN EDECEK. SİZ DE EDİN.'
    m2 = F(MONO, 22)
    d.text(((W - m2.getlength(s2)) / 2, yy + 26), s2, font=m2, fill=SOFT + (255,))
    fr.alpha_composite(ov)
    fr.convert('RGB').save(path, quality=92)


def main():
    import importlib.util
    ap = argparse.ArgumentParser()
    ap.add_argument('bolum')
    ap.add_argument('--dosya', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bolumler.py'),
                    help='bölüm tanımlarını içeren bolumler.py yolu')
    ap.add_argument('--kare', nargs='*', type=float)
    ap.add_argument('--cikti')
    ap.add_argument('--kapak')
    a = ap.parse_args()
    spec = importlib.util.spec_from_file_location('bolumler', a.dosya)
    bolumler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bolumler)
    ep = bolumler.BOLUMLER[a.bolum]
    ev, tm = timeline(ep)
    print('süre: %.1f sn' % tm['total'], {k: round(v, 1) for k, v in tm.items()},
          [(e['i'], round(e['t_show'], 1)) for e in ev])
    if a.kare:
        st = build(ep)
        for t in a.kare:
            compose(t, st).save(f'{a.bolum}_{t:05.1f}.png')
    if a.kapak:
        kapak(ep, a.kapak)
    if a.cikti:
        render(ep, a.cikti)
        print('done', a.cikti)


if __name__ == '__main__':
    main()
