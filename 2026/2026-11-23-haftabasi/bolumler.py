"""23.11.2026 — Haftalık rotasyonun ilk günü: 3 biçim × 3 saat.
Her biçim kendi motoruyla çalışır:
- F1 "Suç mu, değil mi?" (sucmu.py) → 09:15
- F2 "Başına Gelirse: 3 Adım" (adim3.py) → 13:15
- F3 "Bunu Yanlış Biliyoruz" (yanlis.py) → 19:15
"""

# ============ F1: Suç mu, değil mi? — Bulunan cüzdandaki 10 bin TL
F1 = {
    's1': dict(
        soru=['Yerde cüzdan buldun,', 'içinde 10 bin lira.', 'Cebine koyup gittin.'],
        soru_ses='Yerde bir cüzdan buldun, içinde on bin lira. Cebine koyup gittin. Suç mu?',
        vurgu='Suç mu?',
        secenekler=('SUÇ', 'SUÇ DEĞİL'), dogru=0,
        sonuc='SUÇ',
        satirlar=[
            ('Suçun adı: Kaybolmuş eşya üzerinde tasarruf', 'Suçun adı var: Kaybolmuş eşya üzerinde tasarruf.', 'bilgi'),
            ('Yargıtay: Sahibine iade etmek ya da polise bildirmek şart', 'Yargıtay diyor ki, sahibine iade etmek ya da polise haber vermek şart.', 'bilgi'),
            ('Ceza: 1 yıla kadar hapis veya adli para cezası', 'Ceza: bir yıla kadar hapis ya da adli para cezası. Şikâyete bağlı.', 'kanun', 'sessiz'),
        ],
        gonder='Para bulan arkadaşına gönder',
        gonder_ses='Para bulan arkadaşına gönder.',
        kunye='TCK m. 160 · YCGK 22.02.2023, K. 2023/101',
    ),
}

# ============ F2: Başına Gelirse: 3 Adım — Trafikte kaza, karşı taraf kaçtı
F2 = {
    'a1': dict(
        senaryo='Trafikte kaza oldu. Karşı taraf kaçtı.',
        senaryo_ses='Trafikte kaza oldu, karşı taraf kaçtı. Üç şey yap.',
        adimlar=[
            ('Plakayı, aracın markasını ve rengini not et. Tanık varsa iletişim bilgisini al.',
             'Bir. Plakayı, aracın markasını ve rengini not et. Tanık varsa iletişim bilgisini al.'),
            ('155\'i ara, olay yerinden ayrılma. Kaza tespit tutanağı tutulmadan hareket etme.',
             'İki. Yüz elli beşi ara. Olay yerinden ayrılma; kaza tespit tutanağı tutulmadan hareket etme.'),
            ('KASKO\'na beş iş günü içinde haber ver. Kaçan sürücü için Güvence Hesabı devrede.',
             'Üç. Kaskona beş iş günü içinde haber ver. Kaçan sürücü için Güvence Hesabı devrede.'),
        ],
        dayanaklar=[
            'KTK m. 81 / Karayolları Trafik Yönetmeliği',
            'Genel bildirim ve olay yerinde kalma yükümlülüğü',
            'KASKO Genel Şartları + 2918 s. K. m. 108 (Güvence Hesabı)',
        ],
        cta='Kaydet, lazım olabilir.',
        cta_ses='Kaydet, lazım olabilir.',
        kunye='KTK m. 81, 108 · Karayolları Trafik Yönetmeliği',
    ),
}

# ============ F3: Bunu Yanlış Biliyoruz — Kilit değiştirme
F3 = {
    'y1': dict(
        iddia='Kirasını ödemeyen kiracının kilidini değiştirebilirim.',
        iddia_ses='Kirasını ödemeyen kiracının kilidini değiştirebilirim.',
        yanlis_ses='Yanlış.',
        gercek=('Ev sahibinin dahi kiracının rızası olmadan konuta girmesi, kilidini değiştirmesi ya da eşyasını çıkarması suçtur. '
                'Tahliye yalnızca icra müdürlüğü aracılığıyla yapılır.'),
        gercek_ses=('Ev sahibinin bile, kiracının rızası olmadan eve girmesi, kilidi değiştirmesi ya da eşyayı çıkarması suçtur. '
                    'Tahliye yalnızca icra müdürlüğü aracılığıyla yapılır.'),
        bedel=('Konut dokunulmazlığını ihlal: 1 yıldan 3 yıla kadar hapis (TCK 116). '
               'Üstüne hürriyeti tahdit ve mala zarar verme eklenebilir.'),
        bedel_ses=('Konut dokunulmazlığını ihlalin cezası, bir yıldan üç yıla kadar hapis. '
                   'Üstüne hürriyeti tahdit ve mala zarar verme eklenebilir.'),
        cta='Bunu "ben yaparım" diyen arkadaşına gönder.',
        cta_ses='Bunu "ben yaparım" diyen arkadaşına gönder.',
        kunye='TCK m. 116 · Yargıtay 8. CD, 01.11.2023, K. 2023/8316',
    ),
}


def metin_tsv():
    out = []
    # F1 - indeks konumunu koru: soru=00, satirlar=01..N, gonder=son;
    # "sessiz" işaretli satırlar seslendirilmez (motor da o dosyayı aramaz).
    e = F1['s1']
    n = len(e['satirlar']) + 2
    out.append(f"s1_A_00\t{e['soru_ses']}")
    for i, row in enumerate(e['satirlar']):
        _, ses, *extra = row
        if 'sessiz' in extra:
            continue
        out.append(f's1_A_{i + 1:02d}\t{ses}')
    out.append(f"s1_A_{n - 1:02d}\t{e['gonder_ses']}")
    # F2 - senaryo + 3 adım + CTA
    e = F2['a1']
    seqs = [e['senaryo_ses']] + [s for _, s in e['adimlar']] + [e['cta_ses']]
    for i, s in enumerate(seqs):
        out.append(f'a1_A_{i:02d}\t{s}')
    # F3 - iddia, YANLIŞ, gerçek, bedel, CTA
    e = F3['y1']
    for i, s in enumerate([e['iddia_ses'], e['yanlis_ses'], e['gercek_ses'], e['bedel_ses'], e['cta_ses']]):
        out.append(f'y1_A_{i:02d}\t{s}')
    return '\n'.join(out) + '\n'


# Motor arayüzleri: her biri kendi sözlüğü bekler, aynı dosyadan alır
BOLUMLER = {}
BOLUMLER.update(F1)
BOLUMLER.update(F2)
BOLUMLER.update(F3)


if __name__ == '__main__':
    import sys
    sys.stdout.write(metin_tsv())
