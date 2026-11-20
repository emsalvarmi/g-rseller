"""Kafede Hukuk — KISA BİÇİM (21.11.2026 talimatı): durumla açılış, sesli iki kişilik diyalog, ~25–35 sn.
Olgular aynı klasördeki bolumler.py'den (kararların tam metninden hazırlanmış) alınır; burada yalnızca kısaltılır.

kanca:   ilk saniyeden ekranda duran büyük kart (2–3 satır)
satirlar: (konuşan 'A'=Ayşe | 'M'=Mert, ekranda görünen metin, seslendirilen metin (None = aynısı),
           rol: 'kanca'|'tahmin'|'sonuc'|None, durak indeksi|None)
"""
import importlib.util, os
_s = importlib.util.spec_from_file_location('bolumler', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bolumler.py'))
_b = importlib.util.module_from_spec(_s); _s.loader.exec_module(_b)
B = _b.BOLUMLER

KISA = {
    'b5': dict(kaynak='b5_apartman',
        kanca=['Eski yönetim defterleri', 'teslim etmedi:', '“Hırsız girdi.”'],
        kanca_soru='Suç ne?',
        satirlar=[
            ('A', 'Mert, eski apartman yönetimi defterleri teslim etmiyor. “Hırsız girdi, çalındı” diyor. Ne olur?', None, 'kanca', None),
            ('M', 'Emanet edilen şeyi vermemiş. Güveni kötüye kullanma; ceza onanır.', None, 'tahmin', None),
            ('A', 'Gerçek dava. Dosyada hırsızlık tutanağı bile var. İlk derece yine de mahkûmiyet verdi.', None, None, 1),
            ('A', 'Ama Yargıtay bozdu.', None, 'sonuc', 2),
            ('A', 'İddia doğruysa suç başka: özel belgeyi gizlemek. “Hırsız girdi” savunması da hiç tartışılmamış.', None, None, None),
            ('M', 'Yanlış suç, cevapsız savunma… Bunu bilemedim.', None, None, None),
        ]),
    'b6': dict(kaynak='b6_buro',
        kanca=['Muhasebeci işten ayrıldı,', 'kasada açık çıktı.'],
        kanca_soru='Ceza alır mı?',
        satirlar=[
            ('A', 'Muhasebeci işten ayrılıyor, arkasından kasada açık çıkıyor. Sence ceza alır mı?', None, 'kanca', None),
            ('M', 'İspatı zor. Bence beraat.', None, 'tahmin', None),
            ('A', 'Gerçek dava. İddiaya göre geri alınan paralar kasaya işlenmemiş, belgesiz harcamalar var.', None, None, None),
            ('A', 'İlk derece beraat verdi: kesin ve inandırıcı delil yok.', None, None, 1),
            ('A', 'Yargıtay da beraati onadı. Tam 11 yıl sonra.', 'Yargıtay da beraati onadı. Tam on bir yıl sonra.', 'sonuc', 2),
            ('A', 'Ceza davasında şüphe varsa sanık yararlanır.', None, None, None),
            ('M', 'Kasada açık çıkması suçu ispatlamıyor. Bu sefer bildim!', None, None, None),
        ]),
    'b7': dict(kaynak='b7_atm',
        kanca=['Hesapta para yok,', 'ama ATM para veriyor.'],
        kanca_soru='Çekmek suç mu?',
        satirlar=[
            ('A', 'Mert, hesabında para yok ama ATM sana para veriyor. Çekersen suç mu?', None, 'kanca', None),
            ('M', 'Hata bankanın ama para benim değil. Bence suç.', None, 'tahmin', None),
            ('A', 'Gerçek dava. Banka yazılımı hata yapmış; müşteri beş günde defalarca çekmiş, toplam 56 bin lira.',
                  'Gerçek dava. Banka yazılımı hata yapmış; müşteri beş günde defalarca çekmiş, toplam elli altı bin lira.', None, 1),
            ('A', 'Mahkeme mahkûmiyet verdi: hata sonucu ele geçen eşya üzerinde tasarruf.', None, None, 2),
            ('A', 'Yargıtay bozdu. Ama lehine değil!', None, 'sonuc', 3),
            ('A', 'Birden fazla çekim var; zincirleme suç uygulanmalıydı. Ceza eksik kalmış.', None, None, None),
            ('M', 'ATM hata yapınca para senin olmuyor. Bildim!', None, None, None),
        ]),
    'b8': dict(kaynak='b8_oyuncak',
        kanca=['5 liralık taklit oyuncak,', '12 yıla yakın dava.'],
        kanca_soru='Sonunda ne oldu?',
        satirlar=[
            ('A', '5 liralık taklit bir oyuncak yüzünden 12 yıla yakın süren bir dava. Tahmin et, ne oldu?',
                  'Beş liralık taklit bir oyuncak yüzünden on iki yıla yakın süren bir dava. Tahmin et, ne oldu?', 'kanca', None),
            ('M', 'Taklit ürün bulunmuş. Bence ceza çıkar.', None, 'tahmin', None),
            ('A', 'Gerçek dava. Markette arama yapılıyor; rafın altında tek bir taklit oyuncak çıkıyor.', None, None, None),
            ('A', 'İlk derece 10 ay hapis verdi. İstinaf beraat dedi, daire bozdu, istinaf direndi.',
                  'İlk derece on ay hapis verdi. İstinaf beraat dedi, daire bozdu, istinaf direndi.', None, 3),
            ('A', 'Ceza Genel Kurulu beraati onadı.', None, 'sonuc', 4),
            ('A', 'Aramada kanunun istediği iki kişi bulundurulmamış; oyuncak hukuka aykırı delil sayıldı.', None, None, None),
            ('M', 'Delilin nasıl toplandığı da önemliymiş. Bunu bilemedim.', None, None, None),
        ]),
}


def bolum(k):
    """KISA kaydını bolumler.py'deki karar alanlarıyla birleştirir."""
    d = dict(B[KISA[k]['kaynak']]); d.update(KISA[k]); d['anahtar'] = k
    return d


def metin_tsv():
    out = []
    for k, e in KISA.items():
        for i, (spk, goster, ses, rol, durak) in enumerate(e['satirlar']):
            out.append(f"{k}_{spk}_{i:02d}\t{(ses or goster).strip()}")
    return '\n'.join(out) + '\n'


if __name__ == '__main__':
    import sys
    t = metin_tsv(); sys.stdout.write(t)
    print('kelime:', {k: sum(len((s or g).split()) for _, g, s, _, _ in e['satirlar']) for k, e in KISA.items()}, file=sys.stderr)
