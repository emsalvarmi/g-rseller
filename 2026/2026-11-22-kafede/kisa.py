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
    'b9': dict(kaynak='b9_araba',
        kanca=['Arkadaşı borç aldı, arabasını', 'bıraktı, iki yıl ortadan kayboldu.'],
        kanca_soru='Arabayı satmak suç mu?',
        satirlar=[
            ('A', 'Mert, biri borç alıp arabasını sana bırakıyor, iki yıl ortadan kayboluyor. Satarsan suç mu?', None, 'kanca', None),
            ('M', 'Araba emanet. Satarsan güveni kötüye kullanma; bence ceza onanır.', None, 'tahmin', None),
            ('A', 'Gerçek dava. 5.500 lira borç verilmiş; alacaklı bir buçuk yıl bekleyip arabayı 10 bin liraya satmış.',
                  'Gerçek dava. Beş bin beş yüz lira borç verilmiş; alacaklı bir buçuk yıl bekleyip arabayı on bin liraya satmış.', None, 0),
            ('A', 'İlk derece davayı düşürdü; istinaf ise adli para cezası verdi.', None, None, 2),
            ('A', 'Ama Yargıtay bozdu.', None, 'sonuc', 3),
            ('A', 'Borcu düşüp kalanını vereceğini söylemiş. Yargıtay’a göre bu hukuki uyuşmazlık; suç oluşmamış.', None, None, None),
            ('M', 'Her alacak kavgası ceza davası değilmiş. Bunu bilemedim.', None, None, None),
        ]),
    'b10': dict(kaynak='b10_kombi',
        kanca=['Kiracı, oturduğu evin', 'kombisini söküp sattı.'],
        kanca_soru='Hırsızlık mı?',
        satirlar=[
            ('A', 'Kiracı, oturduğu evin kombisini söküp satıyor. Sence bu hırsızlık mı?', None, 'kanca', None),
            ('M', 'Kombi ona kira sözleşmesiyle teslim edilmiş. Bence hırsızlık değil, güveni kötüye kullanma.', None, 'tahmin', None),
            ('A', 'Gerçek dava. Kira kontratı dosyada. İlk derece yine de hırsızlıktan mahkûmiyet verdi.', None, None, 1),
            ('A', 'Adalet Bakanlığının istemiyle dosya Yargıtay’a gitti.', None, None, None),
            ('A', 'Yargıtay kanun yararına bozdu.', None, 'sonuc', 2),
            ('A', 'Kendisine teslim edilen kombiyi satmak güveni kötüye kullanma. Ama bu bozma hükümlünün aleyhine sonuç doğurmaz.', None, None, None),
            ('M', 'Suçun adı bile önemliymiş. Bildim!', None, None, None),
        ]),
    'b11': dict(kaynak='b11_dondurma',
        kanca=['Satış elemanı müşterinin', 'kartından çekti, malı getirmedi.'],
        kanca_soru='Kimi dolandırdı?',
        satirlar=[
            ('A', 'Satış elemanı müşterinin kartından para çekiyor, malı teslim etmiyor. Sence kimi dolandırdı?', None, 'kanca', None),
            ('M', 'Belli, müşteriyi. Bence nitelikli dolandırıcılık.', None, 'tahmin', None),
            ('A', 'Gerçek dava. Bir dondurma şirketinin elemanı; iki müşteriden 12 bin lirayı aşkın tahsilat.',
                  'Gerçek dava. Bir dondurma şirketinin elemanı; iki müşteriden on iki bin lirayı aşkın tahsilat.', None, None),
            ('A', 'İlk derece her müşteri için ayrı dolandırıcılıktan ceza verdi.', None, None, 1),
            ('A', 'Ama Yargıtay bozdu.', None, 'sonuc', 2),
            ('A', 'Kart ödemeleri şirkete geçmiş; eleman aynı tutarı nakit satışlardan alıp şirkete vermemiş. Zarar gören işveren: güveni kötüye kullanma.', None, None, None),
            ('M', 'Mağdur müşteri değil, şirketmiş. Bunu bilemedim.', None, None, None),
        ]),
    'b12': dict(kaynak='b12_trafik',
        kanca=['Adına trafik cezası yazıldı:', '“Araç benim değil, kimliğimi kullanmışlar.”'],
        kanca_soru='Ne olur?',
        satirlar=[
            ('A', 'Adına trafik cezası yazılıyor. “Araç benim değil, kimliğimi kullanmışlar” diye şikâyetçi oluyor. Ne olur?', None, 'kanca', None),
            ('M', 'Bu kadar emin konuşuyorsa bir bit yeniği var. Bence ceza alır.', None, 'tahmin', None),
            ('A', 'Gerçek dava. Bilirkişi raporuna göre tutanaktaki imza kendi eli ürünü.', None, None, 0),
            ('A', 'Tutanağı yazan polis belli; suçu birine yüklemiş. Dosya iki kez bozuldu.', None, None, 3),
            ('A', 'Sonunda Yargıtay onadı: iftira.', None, 'sonuc', 4),
            ('A', 'Ama ilk hükmü yalnız sanık temyiz ettiği için ceza 2 ay 15 günde kaldı.',
                  'Ama ilk hükmü yalnız sanık temyiz ettiği için ceza iki ay on beş günde kaldı.', None, None),
            ('M', 'Kendi imzana itiraz edilmez. Bildim!', None, None, None),
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
