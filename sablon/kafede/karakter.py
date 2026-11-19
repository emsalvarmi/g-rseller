"""Emsal Var mı? — sohbet biçimi için özgün çizim karakterler (PIL, 3x örnekleme)."""
from PIL import Image, ImageDraw, ImageChops

SS = 3  # örnekleme katsayısı
CW, CH = 480, 760  # karakter tuvali (son boyut)
HX, HY, RX, RY = 240, 190, 96, 112  # baş merkezi ve yarıçaplar (yerel)


def _c(h, a=255):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


def _canvas(w=CW, h=CH):
    return Image.new('RGBA', (w * SS, h * SS), (0, 0, 0, 0))


def _down(im, w=CW, h=CH):
    return im.resize((w, h), Image.LANCZOS)


def _e(d, cx, cy, rx, ry, fill=None, outline=None, width=0):
    d.ellipse([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS], fill=fill,
              outline=outline, width=int(width * SS))


def _rr(d, x0, y0, x1, y1, r, fill):
    d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], radius=int(r * SS), fill=fill)


def _poly(d, pts, fill):
    d.polygon([(x * SS, y * SS) for x, y in pts], fill=fill)


def _line(d, pts, fill, w):
    d.line([(x * SS, y * SS) for x, y in pts], fill=fill, width=int(w * SS), joint='curve')


def _arc(d, cx, cy, rx, ry, a0, a1, fill, w):
    d.arc([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS], a0, a1, fill=fill, width=int(w * SS))


def _over(im, fn):
    """Yarı saydam çizimleri ayrı katmanda yapıp üstüne birleştir."""
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
    fn(ImageDraw.Draw(lay))
    return Image.alpha_composite(im, lay)


def _clip_over(im, fn, clip):
    """fn ile çizilen katmanı yalnızca clip (L maskesi) içinde birleştir."""
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
    fn(ImageDraw.Draw(lay))
    lay.putalpha(ImageChops.multiply(lay.getchannel('A'), clip))
    return Image.alpha_composite(im, lay)


def _mask(fn, size):
    m = Image.new('L', size, 0)
    fn(ImageDraw.Draw(m))
    return m


# ---------------------------------------------------------------- kişiler
KADIN = dict(
    d=1, skin='#e9b892', skin_d='#cf9470', hair='#3a2620', hair_l='#5c3c30',
    top='#c8933c', top_d='#a5752b', top_l='#ddb062', lips='#b0574e', eyes='#2a1d1a',
    kind='kadin')
ERKEK = dict(
    d=-1, skin='#c48b63', skin_d='#a5704e', hair='#2a2220', hair_l='#463a35',
    top='#4c7a73', top_d='#3a615b', top_l='#6c9a92', lips='#9a5446', eyes='#201715',
    kind='erkek')


def govde(p):
    """Masanın üstünde görünen gövde (omuzlar + göğüs) ve boyun."""
    d = p['d']
    im = _canvas()
    dr = ImageDraw.Draw(im)
    tx = HX - d * 14
    nx = HX + d * 6
    _rr(dr, tx - 192, 318, tx + 192, 760, 130, _c(p['top']))
    _rr(dr, nx - 40, 250, nx + 40, 352, 26, _c(p['skin']))
    im = _over(im, lambda o: _e(o, nx, 292, 40, 26, _c(p['skin_d'], 160)))
    dr = ImageDraw.Draw(im)
    if p['kind'] == 'kadin':
        _e(dr, nx, 338, 72, 34, _c(p['top_d']))
        _e(dr, nx, 330, 57, 25, _c(p['skin']))
        im = _over(im, lambda o: [_line(o, [(tx + k * 78, 420), (tx + k * 82, 600)], _c(p['top_d'], 130), 6) for k in (-1, 1)])
    else:
        _poly(dr, [(nx - 46, 320), (nx - 4, 374), (nx - 58, 394)], _c(p['top_l']))
        _poly(dr, [(nx + 46, 320), (nx + 4, 374), (nx + 58, 394)], _c(p['top_l']))
        _line(dr, [(nx, 374), (nx, 600)], _c(p['top_d']), 4)
        for y in (414, 466, 518):
            _e(dr, nx, y, 5, 5, _c(p['top_l']))
    body = _mask(lambda m: m.rounded_rectangle([(tx - 192) * SS, 318 * SS, (tx + 192) * SS, 760 * SS], 130 * SS, fill=255), im.size)
    im = _clip_over(im, lambda o: _poly(o, [(tx - d * 200, 300), (tx - d * 60, 300), (tx - d * 100, 760), (tx - d * 200, 760)],
                                       _c('#000000', 50)), body)
    return _down(im)


def bas(p, goz='acik', agiz='kapali'):
    """Baş katmanı: saç + yüz + yüz hatları. 3/4 profil, d yönüne bakar."""
    d = p['d']
    im = _canvas()
    dr = ImageDraw.Draw(im)
    hair, skin = _c(p['hair']), _c(p['skin'])
    fx, fy, frx, fry = HX + d * 8, HY + 10, RX * 0.93, RY * 0.95
    if p['kind'] == 'kadin':
        _e(dr, HX - d * 58, HY - 110, 46, 42, hair)
        _e(dr, HX - d * 10, HY - 6, RX * 1.1, RY * 1.08, hair)
        _rr(dr, HX - d * 96 - 30, HY - 10, HX - d * 96 + 30, HY + 96, 30, hair)
        im = _over(im, lambda o: _e(o, HX - d * 64, HY - 120, 26, 18, _c(p['hair_l'], 170)))
        dr = ImageDraw.Draw(im)
    else:
        _e(dr, HX - d * 8, HY - 16, RX * 1.02, RY * 0.98, hair)
    ex = HX - d * 84
    _e(dr, ex, HY + 14, 18, 26, skin)
    _e(dr, ex + d * 3, HY + 14, 9, 15, _c(p['skin_d']))
    _e(dr, fx, fy, frx, fry, skin)
    face = _mask(lambda m: _e(m, fx, fy, frx, fry, 255), im.size)
    im = _clip_over(im, lambda o: _poly(o, [(fx - d * 200, fy - 200), (fx - d * 46, fy - 200), (fx - d * 70, fy + 200),
                                           (fx - d * 200, fy + 200)], _c(p['skin_d'], 110)), face)
    dr = ImageDraw.Draw(im)
    ey = HY - 2
    e1, e2 = fx + d * 4, fx + d * 50  # uzak göz, yakın göz
    mx, my = fx + d * 40, fy + 60
    if p['kind'] == 'erkek':
        low = _mask(lambda m: (_e(m, fx, fy, frx, fry, 255),
                               m.rectangle([0, 0, im.size[0], int((fy + 18) * SS)], fill=0)), im.size)
        im = _clip_over(im, lambda o: o.rectangle([0, 0, im.size[0], im.size[1]], fill=_c(p['hair'])), low)
        dr = ImageDraw.Draw(im)
        _e(dr, mx + d * 2, my - 16, 30, 11, _c(p['hair']))
        for i in range(-5, 6):
            _e(dr, HX - d * 8 + i * 17, HY - 112 + i * i * 1.6, 17, 15, hair)
        im = _over(im, lambda o: [_e(o, HX - d * 8 + i * 17 - 3, HY - 115 + i * i * 1.6, 7, 6, _c(p['hair_l'], 200))
                                  for i in range(-5, 6)])
        dr = ImageDraw.Draw(im)
    else:
        _poly(dr, [(HX - d * 90, HY - 40), (HX - d * 70, HY - 110), (HX + d * 10, HY - 126),
                   (HX + d * 80, HY - 96), (HX + d * 96, HY - 40), (HX + d * 40, HY - 72), (HX - d * 30, HY - 58)], hair)
        im = _over(im, lambda o: _e(o, fx + d * 56, ey + 46, 18, 11, _c('#e58b7a', 80)))
        dr = ImageDraw.Draw(im)
    _arc(dr, e1, ey - 30, 17, 10, 200, 340, hair, 6)
    _arc(dr, e2, ey - 32, 19, 10, 200, 340, hair, 6)
    if goz == 'acik':
        _e(dr, e1, ey, 8, 11, _c(p['eyes']))
        _e(dr, e2, ey, 9, 12, _c(p['eyes']))
        _e(dr, e1 + 2, ey - 4, 2.6, 2.6, _c('#ffffff'))
        _e(dr, e2 + 2, ey - 4, 3, 3, _c('#ffffff'))
    else:
        _arc(dr, e1, ey - 2, 9, 6, 10, 170, _c(p['eyes']), 4)
        _arc(dr, e2, ey - 2, 10, 6, 10, 170, _c(p['eyes']), 4)
    if p['kind'] == 'erkek':
        g = _c('#151211')
        _e(dr, e1, ey, 24, 20, None, g, 4)
        _e(dr, e2, ey, 26, 21, None, g, 4)
        _line(dr, [(e1 + d * 24, ey - 4), (e2 - d * 26, ey - 4)], g, 4)
        _line(dr, [(e1 - d * 24, ey - 2), (ex + d * 12, HY + 2)], g, 4)
    nx = fx + d * 74
    _line(dr, [(nx - d * 8, ey + 6), (nx + d * 6, ey + 34), (nx - d * 8, ey + 42)], _c(p['skin_d']), 5)
    lips = _c(p['lips']) if p['kind'] == 'kadin' else _c('#b77a68')
    if agiz == 'kapali':
        _arc(dr, mx, my - 8, 18, 10, 20, 160, lips, 5)
    else:
        _e(dr, mx, my, 15, 11, _c('#5e2a27'))
        _e(dr, mx, my + 5, 10, 5, _c('#c0605a'))
    return _down(im)


def on_kol(p):
    """Masanın üstünde, gövdenin önünde duran iki ön kol ve eller."""
    d = p['d']
    im = _canvas()
    dr = ImageDraw.Draw(im)
    tx = HX - d * 14
    arms = [((tx - 176, 548), (tx - 34 + d * 20, 612)), ((tx + 176, 548), (tx + 34 + d * 20, 606))]
    for (ex, ey), (hx, hy) in arms:
        _line(dr, [(ex, ey), (hx, hy)], _c(p['top']), 76)
        _e(dr, ex, ey, 38, 38, _c(p['top']))
    im = _over(im, lambda o: [_line(o, [(ex, ey + 26), (hx, hy + 24)], _c(p['top_d'], 150), 18) for (ex, ey), (hx, hy) in arms])
    dr = ImageDraw.Draw(im)
    for (ex, ey), (hx, hy) in arms:
        k = 1 if hx > ex else -1
        _e(dr, hx, hy, 36, 36, _c(p['top_l']))
        _e(dr, hx + k * 26, hy + 4, 30, 24, _c(p['skin']))
    return _down(im)
