"""'Suç mu, değil mi?' — 12–20 sn'lik, gönderilmek için tasarlanmış biçim (kullanıcının 21.11.2026 onayı).
Olgular kararın tam metninden; ceza aralığı kanun metninden (LexPanel madde_ara).
satirlar: (ekran metni, seslendirme metni, tür[, 'sessiz']) — tür: 'bilgi' | 'kanun'; 'sessiz' satır okunmaz, yalnızca kartı görünür
Ses kimlikleri: <anahtar>_A_00 = soru, _A_01.. = satirlar, sonuncusu = gönder çağrısı.
"""
BOLUMLER = {
    's1': dict(
        soru=['Komşun, kapını gören', 'bir güvenlik kamerası', 'taktırdı.'],
        soru_ses='Komşun, kapını gören bir güvenlik kamerası taktırdı. Suç mu?',
        vurgu='Suç mu?',
        secenekler=('SUÇ', 'SUÇ DEĞİL'), dogru=1,
        sonuc='BU DOSYADA: SUÇ DEĞİL',
        satirlar=[
            ('İlk mahkeme: 1 yıl 8 ay hapis', 'Bu dosyada ilk mahkeme, bir yıl sekiz ay hapis verdi.', 'bilgi'),
            ('İstinaf: beraat · Yargıtay: onama', 'Ama istinaf beraat dedi, Yargıtay da onadı.', 'bilgi'),
            ('Kamera evin içini görmüyordu; şikâyetten sonra söküldü', 'Çünkü kamera evin içini görmüyordu; şikâyetten sonra da söküldü.', 'bilgi'),
            ('Evin içini görseydi? Özel hayatın gizliliğini ihlal: 1–3 yıl hapis (TCK 134)', 'Evin içini görseydi? Özel hayatın gizliliğini ihlalin cezası, bir yıldan üç yıla hapis.', 'kanun', 'sessiz'),
        ],
        gonder='Kapısında kamera olan komşuna gönder',
        gonder_ses='Kapısında kamera olan komşuna gönder.',
        kunye='Yargıtay 12. CD · 12.05.2025 · E. 2023/2593 · K. 2025/4314',
    ),
}


def metin_tsv():
    out = []
    for k, e in BOLUMLER.items():
        ses = [e['soru_ses']] + [x[1] for x in e['satirlar']] + [e['gonder_ses']]
        out += [f'{k}_A_{i:02d}\t{s}' for i, s in enumerate(ses)]
    return '\n'.join(out) + '\n'


if __name__ == '__main__':
    import sys
    sys.stdout.write(metin_tsv())
