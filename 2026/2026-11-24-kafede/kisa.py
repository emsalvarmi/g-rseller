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
    'b13': dict(kaynak='b13_atm',
        kanca=['Yaşlı adam ATM’de yardım istedi.', 'Kartı takıldı, 530 lirası gitti.'],
        kanca_soru='Hangi suç?',
        satirlar=[
            ('A', 'Yaşlı bir adam ATM’de yardım istiyor; kartı takılıyor, 530 lirası gidiyor. Sence hangi suç?',
                  'Yaşlı bir adam bankamatikte yardım istiyor; kartı takılıyor, beş yüz otuz lirası gidiyor. Sence hangi suç?', 'kanca', None),
            ('M', 'Yardım bahanesiyle kandırmışlar. Bence dolandırıcılık.', None, 'tahmin', None),
            ('A', 'Gerçek dava. İlk derece dolandırıcılık dedi; dosya ağır cezaya gitti, yağma cezası çıktı.', None, None, 2),
            ('A', 'Yargıtay “yağma değil” diye bozdu; yerel mahkeme direndi.', None, None, 3),
            ('A', 'Sonunda Ceza Genel Kurulu karar verdi: dava düştü.', None, 'sonuc', 4),
            ('A', 'Kamerada itme yok, para rızası dışında alınmış: suç hırsızlık. Ama zamanaşımı çoktan dolmuş.', None, None, None),
            ('M', 'Ne dolandırıcılık ne yağma, hırsızlıkmış. Bunu bilemedim.', None, None, None),
        ]),
    'b14': dict(kaynak='b14_whatsapp',
        kanca=['Satıcı WhatsApp’tan “cahil, gerzek” yazdı;', 'müşteri “Sensin cahil!” diye cevap verdi.'],
        kanca_soru='Müşteri ceza alır mı?',
        satirlar=[
            ('A', 'Sipariş gecikiyor. Satıcı WhatsApp’tan “cahil, gerzek” yazıyor; müşteri “Sensin cahil” diye karşılık veriyor. Ceza alır mı?', None, 'kanca', None),
            ('M', 'Hakaret hakarettir. Bence müşteri de ceza alır.', None, 'tahmin', None),
            ('A', 'Gerçek dava. Üstelik şikâyetçi olan satıcı; dava müşteriye açıldı.', None, None, 0),
            ('A', 'İlk derece mahkemesi ceza verilmesine yer olmadığına karar verdi.', None, None, 1),
            ('A', 'Yargıtay da onadı.', None, 'sonuc', 2),
            ('A', 'Gerekçe: müşteri, satıcının hakaretine ve haksız fiiline karşılık vermiş.', None, None, None),
            ('M', 'İlk hakareti eden sensen, karşılığı ceza getirmeyebilir. Bunu bilemedim.', None, None, None),
        ]),
    'b15': dict(kaynak='b15_telefon',
        kanca=['Tamirden dönen telefon', 'yanlış dükkâna gönderildi. İade edilmedi.'],
        kanca_soru='Hangi suç?',
        satirlar=[
            ('A', 'Tamirden dönen telefon yanlışlıkla başka bir dükkâna gidiyor; dükkân sahibi iade etmiyor. Sence hangi suç?', None, 'kanca', None),
            ('M', 'Telefon ona emanet edilmemiş, yanlışlıkla gelmiş. Bence hata sonucu ele geçen eşya.', None, 'tahmin', None),
            ('A', 'Gerçek dava. Telefon geri yollanırken başka ilçedeki bir dükkâna gitmiş.', None, None, 0),
            ('A', 'İlk derece, hizmet nedeniyle güveni kötüye kullanmadan ceza verdi.', None, None, 1),
            ('A', 'Ama Yargıtay bozdu.', None, 'sonuc', 2),
            ('A', 'Telefon ona teslim edilmemiş, hata sonucu eline geçmiş. Suç vasfında yanılgı var.', None, None, None),
            ('M', 'Yanlış gelen mal yine iade edilir; ama suçun adı başka. Bildim!', None, None, None),
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
