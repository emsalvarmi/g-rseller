"""Emsal Var mı? — sohbet biçimi örnek video (seslendirmesiz, konuşma balonları).
Kullanım: python3 sohbet.py --kare 5.0 12.3 ...   (kontrol kareleri)
          python3 sohbet.py --cikti ornek.mp4        (tam video)
"""
import argparse, math, os, random, subprocess, sys, wave, struct
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
import karakter as K

W, H, FPS = 1080, 1920, 30
FD = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts') + '/'
F = lambda n, s: ImageFont.truetype(FD + n, s)
INTER_M, INTER_SB, INTER_R = 'Inter-Medium.otf', 'Inter-SemiBold.otf', 'Inter-Regular.otf'
CORM, CORM_I = 'CormorantGaramond_600SemiBold.ttf', 'CormorantGaramond_600SemiBold_Italic.ttf'
MONO = 'IBMPlexMono_500Medium.ttf'
GOLD = (214, 178, 106)
INK = (24, 30, 40)
CREAM = (246, 241, 231)
NAVY = (14, 20, 30)

KUNYE = 'Yargıtay 4. Ceza Dairesi · E. 2024/12236 · K. 2026/8234 · 04.05.2026'
SORU = 'WhatsApp grubunda\nsöylenen söz\nhakaret mi?'

# A = kadın (solda, kararı okumuş), B = erkek (sağda, soruyor)
DIYALOG = [
    ('A', 'Bir WhatsApp grubuna atılan ses kaydı yüzünden hakaret davası açılmış.'),
    ('B', 'Ne denmiş ki?'),
    ('A', 'Bir okul müdürü için “uzun kollar tarafından yerleştirilmiş biri” denmiş.'),
    ('B', 'Bu düpedüz hakaret bence.'),
    ('A', 'Müdür de öyle düşünmüş. Ama ilk derece mahkemesi beraat vermiş.'),
    ('B', 'İstinaf ne demiş?'),
    ('A', 'Bölge adliye mahkemesi de istinaf başvurusunu reddetmiş.'),
    ('A', 'Müdürün vekili temyiz etmiş: Sözler, mesleği ve konumu nedeniyle onuruna zarar vermiş.'),
    ('B', 'Yargıtay ne dedi?'),
    ('A', 'Beraati onadı.'),
    ('B', 'Neden?'),
    ('A', 'Sözleri kaba, rahatsız edici ve nezaket dışı buldu; ama onur, şeref ve saygınlığı rencide edecek boyutta görmedi.'),
    ('A', 'Eleştiri saydı. Hakaret suçunun unsurları oluşmamış.'),
    ('B', 'Yani kaba olmak tek başına hakaret değil.'),
    ('A', 'Bu dosyada öyle. Her söz kendi bağlamında değerlendirilir.'),
    ('A', '#KARAR'),
]

INTRO = 3.0
TYPE = 0.6
OUTRO = 3.2
BOTTOM = 1010   # balon yığınının alt sınırı
TOPCLIP = 300   # balonların silikleştiği üst sınır
LX, RXB = 64, 1016
BMAX = 700


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def hold_for(text):
    if text == '#KARAR':
        return 3.0
    w = len(text.split())
    return max(1.8, min(4.8, 0.85 + 0.27 * w))


# ---------------------------------------------------------------- zaman çizelgesi
def timeline():
    t = INTRO
    ev = []
    for i, (who, tx) in enumerate(DIYALOG):
        ev.append(dict(i=i, who=who, text=tx, t_type=t, t_show=t + TYPE))
        t += TYPE + hold_for(tx)
    return ev, t + OUTRO


# ---------------------------------------------------------------- balonlar
def wrap(text, font, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        nxt = (cur + ' ' + w).strip()
        if font.getlength(nxt) <= maxw:
            cur = nxt
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def bubble_img(who, text):
    S = 2
    left = who == 'A'
    bg = CREAM if left else (236, 217, 168)
    if text == '#KARAR':
        return karar_card(S)
    f = F(INTER_M, 44 * S)
    lines = wrap(text, f, (BMAX - 64) * S)
    lh = 58 * S
    tw = max(f.getlength(l) for l in lines)
    bw, bh = int(tw + 64 * S), int(len(lines) * lh + 44 * S)
    im = Image.new('RGBA', (bw + 30 * S, bh + 30 * S), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ox = 0 if left else 30 * S
    ImageDraw.Draw(sh).rounded_rectangle([ox, 10 * S, ox + bw, 10 * S + bh], 34 * S, fill=(0, 0, 0, 90))
    sh = sh.filter(ImageFilter.GaussianBlur(10 * S))
    im = Image.alpha_composite(im, sh)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([ox, 0, ox + bw, bh], 34 * S, fill=bg + (255,))
    # kuyruk
    if left:
        d.polygon([(ox + 34 * S, bh - 2), (ox + 6 * S, bh + 26 * S), (ox + 74 * S, bh - 2)], fill=bg + (255,))
    else:
        d.polygon([(ox + bw - 34 * S, bh - 2), (ox + bw - 6 * S, bh + 26 * S), (ox + bw - 74 * S, bh - 2)], fill=bg + (255,))
    y = 22 * S
    for l in lines:
        d.text((ox + 32 * S, y), l, font=f, fill=INK)
        y += lh
    im = im.resize((im.width // S, im.height // S), Image.LANCZOS)
    return im


def karar_card(S):
    bw, bh = 700 * S, 330 * S
    im = Image.new('RGBA', (bw + 30 * S, bh + 30 * S), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([0, 10 * S, bw, 10 * S + bh], 28 * S, fill=(0, 0, 0, 100))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(10 * S)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, bw, bh], 28 * S, fill=CREAM + (255,))
    d.polygon([(34 * S, bh - 2), (6 * S, bh + 26 * S), (74 * S, bh - 2)], fill=CREAM + (255,))
    d.rounded_rectangle([22 * S, 22 * S, bw - 22 * S, bh - 22 * S], 18 * S, fill=(250, 247, 240, 255),
                        outline=(214, 205, 188, 255), width=2 * S)
    d.text((50 * S, 46 * S), 'YARGITAY', font=F(MONO, 22 * S), fill=(140, 120, 90))
    d.text((50 * S, 76 * S), '4. Ceza Dairesi', font=F(CORM, 54 * S), fill=INK)
    m = F(MONO, 24 * S)
    for k, (a, b) in enumerate([('ESAS', '2024/12236'), ('KARAR', '2026/8234'), ('TARİH', '04.05.2026')]):
        y = (152 + k * 40) * S
        d.text((50 * S, y), a, font=m, fill=(140, 120, 90))
        d.text((190 * S, y), b, font=m, fill=INK)
    # mühür
    st = Image.new('RGBA', (250 * S, 120 * S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    red = (178, 52, 46, 235)
    sd.rounded_rectangle([6 * S, 6 * S, 244 * S, 114 * S], 14 * S, outline=red, width=5 * S)
    fs = F(CORM, 56 * S)
    tw = fs.getlength('ONAMA')
    sd.text(((250 * S - tw) / 2, 12 * S), 'ONAMA', font=fs, fill=red)
    f2 = F(MONO, 18 * S)
    t2 = 'OY BİRLİĞİYLE'
    sd.text(((250 * S - f2.getlength(t2)) / 2, 80 * S), t2, font=f2, fill=red)
    st = st.rotate(-8, resample=Image.BICUBIC, expand=True)
    im.alpha_composite(st, (bw - st.width - 34 * S, 150 * S))
    return im.resize((im.width // S, im.height // S), Image.LANCZOS)


def typing_img(who, t):
    S = 2
    left = who == 'A'
    bg = CREAM if left else (236, 217, 168)
    bw, bh = 150 * S, 86 * S
    im = Image.new('RGBA', (bw + 30 * S, bh + 30 * S), (0, 0, 0, 0))
    ox = 0 if left else 30 * S
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([ox, 0, ox + bw, bh], 34 * S, fill=bg + (235,))
    if left:
        d.polygon([(ox + 34 * S, bh - 2), (ox + 6 * S, bh + 26 * S), (ox + 74 * S, bh - 2)], fill=bg + (235,))
    else:
        d.polygon([(ox + bw - 34 * S, bh - 2), (ox + bw - 6 * S, bh + 26 * S), (ox + bw - 74 * S, bh - 2)], fill=bg + (235,))
    for k in range(3):
        ph = (t * 3.2 - k * 0.22) % 1.0
        up = math.sin(ph * math.pi) if ph < 1 else 0
        a = int(110 + 120 * up)
        cy = bh / 2 - up * 8 * S
        cx = ox + bw / 2 + (k - 1) * 30 * S
        d.ellipse([cx - 9 * S, cy - 9 * S, cx + 9 * S, cy + 9 * S], fill=(60, 66, 78, a))
    return im.resize((im.width // S, im.height // S), Image.LANCZOS)


# ---------------------------------------------------------------- sahne (sabit katmanlar)
def background():
    y = np.linspace(0, 1, H)[:, None]
    top = np.array([16, 22, 34])
    bot = np.array([30, 34, 44])
    g = (top + (bot - top) * y).astype(np.float32)
    img = np.repeat(g[:, None, :], W, axis=1).reshape(H, W, 3)
    bg = Image.fromarray(img.clip(0, 255).astype(np.uint8)).convert('RGBA')
    # pencere ve bulanık şehir ışıkları
    win = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(win)
    wd.rounded_rectangle([60, 250, 1020, 1470], 40, fill=(24, 34, 52, 255))
    rnd = random.Random(7)
    lights = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lights)
    for _ in range(70):
        x, yy = rnd.uniform(80, 1000), rnd.uniform(700, 1460)
        r = rnd.uniform(14, 46)
        col = rnd.choice([(232, 186, 110), (240, 210, 150), (120, 170, 200), (220, 140, 90)])
        ld.ellipse([x - r, yy - r, x + r, yy + r], fill=col + (rnd.randint(40, 110),))
    lights = lights.filter(ImageFilter.GaussianBlur(14))
    mask = Image.new('L', (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle([60, 250, 1020, 1470], 40, fill=255)
    win.alpha_composite(lights)
    win.putalpha(mask)
    bg.alpha_composite(win)
    # pencere çerçevesi
    fr = ImageDraw.Draw(bg)
    fr.rounded_rectangle([60, 250, 1020, 1470], 40, outline=(44, 54, 72, 255), width=6)
    fr.line([(540, 250), (540, 1470)], fill=(44, 54, 72, 255), width=6)
    # sıcak lamba ışığı
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([140, 1180, 940, 1760], fill=(255, 190, 110, 60))
    bg.alpha_composite(glow.filter(ImageFilter.GaussianBlur(90)))
    return bg


def table():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    y = np.linspace(0, 1, H - 1490)[:, None]
    a = np.array([122, 82, 54]); b = np.array([70, 46, 32])
    g = (a + (b - a) * y)
    arr = np.repeat(g[:, None, :], W, axis=1)
    # ahşap damarları
    rnd = np.random.default_rng(3)
    for _ in range(26):
        yy = rnd.integers(0, H - 1490)
        arr[yy:yy + 2, :, :] *= 0.9
    t = Image.fromarray(arr.clip(0, 255).astype(np.uint8)).convert('RGBA')
    im.paste(t, (0, 1490))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 1486, W, 1496], fill=(160, 112, 74, 255))
    return im


def props():
    """Masadaki fincanlar ve telefon."""
    S = 3
    im = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    def cup(cx, cy, col):
        d.ellipse([(cx - 60) * S, (cy + 52) * S, (cx + 60) * S, (cy + 74) * S], fill=(0, 0, 0, 70))
        d.rounded_rectangle([(cx - 44) * S, (cy - 10) * S, (cx + 44) * S, (cy + 62) * S], 22 * S, fill=col)
        d.ellipse([(cx - 44) * S, (cy - 22) * S, (cx + 44) * S, (cy + 2) * S], fill=col)
        d.ellipse([(cx - 36) * S, (cy - 18) * S, (cx + 36) * S, (cy - 2) * S], fill=(92, 58, 36, 255))
        d.arc([(cx + 34) * S, (cy + 2) * S, (cx + 66) * S, (cy + 40) * S], 270, 90, fill=col, width=9 * S)
    cup(318, 1578, (238, 232, 220, 255))
    cup(762, 1578, (60, 92, 104, 255))
    # telefon (masada, ekranı yukarı)
    d.rounded_rectangle([(490) * S, (1640) * S, (590) * S, (1830) * S], 16 * S, fill=(22, 24, 30, 255))
    d.rounded_rectangle([(497) * S, (1647) * S, (583) * S, (1823) * S], 12 * S, fill=(38, 120, 92, 255))
    for k in range(4):
        y = 1670 + k * 34
        x0 = 506 if k % 2 == 0 else 530
        d.rounded_rectangle([x0 * S, y * S, (x0 + 46) * S, (y + 20) * S], 8 * S, fill=(220, 240, 230, 200))
    return im.resize((W, H), Image.LANCZOS)


def header():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = F(CORM, 44)
    t = 'E M S A L   V A R   M I ?'
    d.text(((W - f.getlength(t)) / 2, 96), t, font=f, fill=GOLD + (255,))
    m = F(MONO, 22)
    t2 = '@emsalvarmi'
    d.text(((W - m.getlength(t2)) / 2, 152), t2, font=m, fill=(150, 160, 175, 255))
    c = F(MONO, 22)
    t3 = 'YARGITAY 4. CEZA DAİRESİ · HAKARET'
    tw = c.getlength(t3)
    d.rounded_rectangle([(W - tw) / 2 - 20, 198, (W + tw) / 2 + 20, 238], 20, outline=GOLD + (200,), width=2)
    d.text(((W - tw) / 2, 205), t3, font=c, fill=GOLD + (255,))
    return im


# ---------------------------------------------------------------- karakterler
class Kisi:
    def __init__(self, p, ox, oy, arm_to):
        self.p, self.ox, self.oy = p, ox, oy
        self.govde = K.govde(p)
        self.heads = {(g, a): K.bas(p, g, a) for g in ('acik', 'kapali') for a in ('kapali', 'acik')}
        self.kol = K.on_kol(p)
        rnd = random.Random(11 if p['d'] > 0 else 23)
        self.blinks, t = [], 1.0
        while t < 120:
            t += rnd.uniform(2.4, 4.6)
            self.blinks.append(t)

    def blink(self, t):
        return any(0 <= t - b < 0.13 for b in self.blinks)


def compose(t, base, tbl, prp, hdr, A, B, ev, total, bubbles):
    fr = base.copy()
    # konuşan / yazan
    talking = None
    for e in ev:
        if e['t_type'] <= t < e['t_show'] + 0.7 and e['text'] != '#KARAR':
            talking = e['who']
    for who, k in (('A', A), ('B', B)):
        br = math.sin(t * 2 * math.pi / 4.2 + (0 if who == 'A' else 1.7)) * 2.5
        fr.alpha_composite(k.govde, (k.ox, int(k.oy + br)))
        mouth = 'kapali'
        tilt = 0.0
        if talking == who:
            mouth = 'acik' if int(t * 7.5) % 2 == 0 else 'kapali'
            tilt = 2.2 * k.p['d']
        elif talking:
            tilt = -0.8 * k.p['d']  # dinleyen hafif geri
        head = k.heads[('kapali' if k.blink(t) else 'acik', mouth)]
        # baş eğimi: boyun noktası etrafında döndür
        if abs(tilt) > 0.01:
            head = head.rotate(-tilt, resample=Image.BICUBIC, center=(K.HX, 290))
        fr.alpha_composite(head, (k.ox, int(k.oy + br * 1.2)))
    fr.alpha_composite(tbl)
    fr.alpha_composite(A.kol, (A.ox, A.oy))
    fr.alpha_composite(B.kol, (B.ox, B.oy))
    fr.alpha_composite(prp)
    # balon yığını
    slots = []
    for e in ev:
        if t < e['t_type']:
            break
        bi = bubbles[e['i']]
        if t < e['t_show']:
            ti = typing_img(e['who'], t)
            grow = ease((t - e['t_type']) / 0.25)
            slots.append((e, ti, ti.height * grow, 1.0, grow))
        else:
            p = (t - e['t_show']) / 0.32
            tih = 116
            hh = tih + (bi.height - tih) * ease(p)
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
        x = LX if e['who'] == 'A' else RXB - img.width
        layer.alpha_composite(img, (int(x), int(top + (hh - img.height))))
    fr.alpha_composite(layer)
    fr.alpha_composite(hdr)
    # giriş: soru kartı
    if t < INTRO + 0.5:
        a = 1.0 if t < INTRO - 0.6 else max(0.0, 1 - (t - (INTRO - 0.6)) / 0.9)
        ov = Image.new('RGBA', (W, H), (10, 14, 22, int(215 * a)))
        d = ImageDraw.Draw(ov)
        f = F(CORM_I, 104)
        lines = SORU.split('\n')
        yy = 640 - (1 - ease(t / 0.8)) * 30
        for l in lines:
            d.text(((W - f.getlength(l)) / 2, yy), l, font=f, fill=CREAM + (int(255 * a * ease(t / 0.6)),))
            yy += 118
        m = F(MONO, 26)
        s = 'YARGITAY NE DEDİ?'
        d.text(((W - m.getlength(s)) / 2, yy + 40), s, font=m, fill=GOLD + (int(255 * a * ease((t - 0.5) / 0.6)),))
        fr.alpha_composite(ov)
    # kapanış kartı
    t_end = total - OUTRO + 0.4
    if t >= t_end:
        a = ease((t - t_end) / 0.8)
        ov = Image.new('RGBA', (W, H), NAVY + (int(250 * a),))
        d = ImageDraw.Draw(ov)
        f = F(CORM, 96)
        s = 'Emsal var mı?'
        d.text(((W - f.getlength(s)) / 2, 690), s, font=f, fill=CREAM + (int(255 * a),))
        f2 = F(CORM_I, 56)
        s2 = 'Kararı bil, hakkını bil.'
        d.text(((W - f2.getlength(s2)) / 2, 810), s2, font=f2, fill=GOLD + (int(255 * a),))
        m = F(MONO, 22)
        d.text(((W - m.getlength(KUNYE)) / 2, 940), KUNYE, font=m, fill=(170, 178, 190, int(255 * a)))
        r = F(INTER_R, 26)
        for k, s3 in enumerate(['Genel bilgilendirme amaçlıdır; hukuki görüş değildir.',
                                'Karakterler temsilîdir; dosyanın tarafları değildir.']):
            d.text(((W - r.getlength(s3)) / 2, 1010 + k * 40), s3, font=r, fill=(150, 158, 170, int(255 * a)))
        fr.alpha_composite(ov)
    return fr.convert('RGB')


def build():
    ev, total = timeline()
    base = background()
    tbl = table()
    prp = props()
    hdr = header()
    A = Kisi(K.KADIN, 70, 950, (400, 600))
    B = Kisi(K.ERKEK, 530, 950, (80, 606))
    bubbles = {e['i']: bubble_img(e['who'], e['text']) for e in ev}
    return ev, total, base, tbl, prp, hdr, A, B, bubbles


def sesler(ev, total, path):
    sr = 48000
    n = int(sr * total)
    a = np.zeros(n, dtype=np.float32)
    def pop(t0, f0, f1, dur=0.09, vol=0.16):
        i0 = int(t0 * sr); m = int(dur * sr)
        tt = np.arange(m) / sr
        f = np.linspace(f0, f1, m)
        ph = 2 * np.pi * np.cumsum(f) / sr
        env = np.exp(-tt * 38) * (1 - np.exp(-tt * 900))
        s = np.sin(ph) * env * vol
        a[i0:i0 + m] += s[:max(0, min(m, n - i0))]
    for e in ev:
        if e['who'] == 'A':
            pop(e['t_show'], 900, 640)
        else:
            pop(e['t_show'], 700, 520)
    pop(0.15, 520, 780, 0.22, 0.10)
    pop(total - OUTRO + 0.4, 660, 440, 0.35, 0.10)
    pcm = (np.clip(a, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--kare', nargs='*', type=float)
    ap.add_argument('--cikti')
    a = ap.parse_args()
    ev, total, base, tbl, prp, hdr, A, B, bubbles = build()
    print('süre: %.1f sn' % total)
    if a.kare:
        for t in a.kare:
            compose(t, base, tbl, prp, hdr, A, B, ev, total, bubbles).save(f'/home/claude/ko2/sohbet/kare_{t:05.1f}.png')
        return
    out = a.cikti
    tmp = out[:-4] + '.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                          '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16',
                          '-pix_fmt', 'yuv420p', '-movflags', '+faststart', tmp], stdin=subprocess.PIPE)
    nf = int(round(total * FPS))
    for i in range(nf):
        p.stdin.write(compose(i / FPS, base, tbl, prp, hdr, A, B, ev, total, bubbles).tobytes())
    p.stdin.close()
    if p.wait() != 0:
        sys.exit('ffmpeg hata')
    wav = out[:-4] + '.wav'
    sesler(ev, total, wav)
    tmp2 = out[:-4] + '.tmp2.mp4'
    r = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-i', wav, '-map', '0:v', '-map', '1:a',
                        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', tmp2])
    if r.returncode == 0:
        os.replace(tmp2, out)
        os.remove(tmp)
    print('done', out)


if __name__ == '__main__':
    main()
