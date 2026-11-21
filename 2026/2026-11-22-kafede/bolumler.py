"""Kafede Hukuk bölümleri — 22.11.2026 (Bölüm 9–12). Her bölüm tek bir Yargıtay kararının tam metninden hazırlanır.
duraklar: (etiket1, etiket2, tarih, olaydan_bu_yana_gun|None, renk)
Gün sayıları Python ile hesaplandı (datetime.date farkı); olay tarihi metinde gün olarak yazmıyorsa None.
"""

BOLUMLER = {
    'b9_araba': dict(
        no=9, saat='sabah',
        soru=['Arkadaşı borç aldı, arabasını bıraktı,', 'iki yıl ortadan kayboldu.', 'Arabayı satmak suç mu?'],
        duraklar=[('BORÇ + ANAHTAR', 'EMANET ARAÇ', '2014', None, 'gri'),
                  ('DÜŞME', 'İLK DERECE', '24.06.2021', None, 'gri'),
                  ('MAHKÛMİYET', 'İSTİNAF', '09.03.2022', None, 'kirmizi'),
                  ('BOZMA', 'YARGITAY', '12.10.2026', None, 'altin')],
        # Metne göre: 2014'te katılan, kâr payı karşılığı sanıktan 5.500 TL borç aldı; üzerinde haciz bulunan aracını
        # anahtarıyla emaneten sanığa bıraktı; sanık iki yıl haber alamadı, aracı bir buçuk yıl bekletip sattı.
        # Katılan beyanı: sanık aracı 10.000 TL'ye sattığını, 5.500 TL'yi borca mahsup edip kalanı vereceğini söyledi.
        # İlk derece (24.06.2021) TCK 73/1, 73/4, CMK 223/8 düşme; istinaf (09.03.2022) TCK 155/1, hapisten çevrilme
        # 3.000 TL adli para cezası; Yargıtay: hukuki ihtilaf, unsurlar oluşmadı, beraat yerine mahkûmiyet → bozma (oy birliği).
        tahmin='CEZA ONANIR', dogru=False,
        kalp_not='Bozma suçluluk ya da masumiyet tespiti değildir; dosya istinafa döndü.',
        karne_baslik='Emanet araba', karne_tahmin='Ceza onanır', karne_sonuc='Bozma: hukuki uyuşmazlık',
        toplam_dogru=4, toplam_yanlis=5,
        kunyeler=['Yargıtay 11. CD · 12.10.2026 · E. 2023/662 · K. 2026/8858'],
    ),
    'b10_kombi': dict(
        no=10, saat='ogle',
        soru=['Kiracı, oturduğu evin', 'kombisini söküp sattı.', 'Hırsızlık mı?'],
        duraklar=[('KİRA', 'KONTRAT', '05.07.2021', 0, 'gri'),
                  ('HIRSIZLIK', 'İLK DERECE', '19.09.2022', 441, 'kirmizi'),
                  ('BOZMA', 'KANUN YARARINA', '31.12.2024', 1275, 'altin')],
        # Metne göre: 05.07.2021 tarihli kira kontratıyla kiracı olarak oturduğu evin kombisini söküp sattı; ilk derece
        # TCK 142/2-h hırsızlıktan mahkûmiyet (19.09.2022). Adalet Bakanlığının istemi üzerine Yargıtay C. Başsavcılığı
        # kanun yararına bozma istedi; Yargıtay 2. CD: eylem TCK 155/1 güveni kötüye kullanma; ayrıca konut dokunulmazlığı
        # hükmünde zincirleme/çelişki/hesap hatası. Kanun yararına, aleyhe sonuç doğurmamak üzere bozma (oy birliği).
        tahmin='HIRSIZLIK DEĞİL', dogru=True,
        kalp_not='Kanun yararına bozma, hükümlünün aleyhine sonuç doğurmaz.',
        karne_baslik='Sökülen kombi', karne_tahmin='Güveni kötüye kullanma', karne_sonuc='Kanun yararına bozma',
        toplam_dogru=5, toplam_yanlis=5,
        kunyeler=['Yargıtay 2. CD · 31.12.2024 · E. 2024/16784 · K. 2024/22055'],
    ),
    'b11_dondurma': dict(
        no=11, saat='aksamustu',
        soru=['Satış elemanı müşterinin kartından çekti,', 'malı teslim etmedi.', 'Kimi dolandırdı?'],
        duraklar=[('DAVA', 'ESAS KAYDI', '2012', None, 'gri'),
                  ('MAHKÛMİYET', 'İLK DERECE', '2016', None, 'kirmizi'),
                  ('BOZMA', 'YARGITAY', '21.09.2026', None, 'altin')],
        # Metne göre: dondurma şirketinde pazarlama/satış elemanı; kampanya diyerek bir katılanın kartından 3.435,97 TL,
        # birleşen dosyada diğerinden toplam 8.581,67 TL tahsil edip ürünleri teslim etmediği iddiası. Yargıtay'a göre
        # (sanık ikrarı ve dosya): kart tahsilatlarını gün içi nakit satışlardan göstererek nakit paraları şirkete teslim
        # etmeyip menfaatine geçirdi; müşteriler şirkete icra takibi başlattı. Eylem bütün olarak şirkete karşı uzlaşmaya
        # tabi zincirleme hizmet nedeniyle güveni kötüye kullanma (TCK 155/2); ayrı ayrı nitelikli dolandırıcılık
        # (TCK 158/1-h) mahkûmiyeti hatalı → bozma (oy birliği). Ayrıca hesap hatası ve hükümde çelişki.
        tahmin='MÜŞTERİYİ', dogru=False,
        kalp_not='Bozma suçluluk ya da masumiyet tespiti değildir.',
        karne_baslik='Kartla ödenen dondurma', karne_tahmin='Müşteri dolandırıldı', karne_sonuc='Bozma: işverene güveni k.k.',
        toplam_dogru=5, toplam_yanlis=6,
        kunyeler=['Yargıtay 11. CD · 21.09.2026 · E. 2026/5124 · K. 2026/8130'],
    ),
    'b12_trafik': dict(
        no=12, saat='gece',
        soru=['Adına trafik cezası yazıldı:', '"Araç benim değil, kimliğimi kullanmışlar."', 'Ne olur?'],
        duraklar=[('SUÇ UYDURMA', 'İLK DERECE', '23.06.2016', 0, 'kirmizi'),
                  ('İFTİRA', 'BOZMA', '22.12.2022', 2373, 'gri'),
                  ('10 AY', 'İLK DERECE', '28.03.2024', 2835, 'kirmizi'),
                  ('2 AY 15 GÜN', 'KAZANILMIŞ HAK', '15.01.2026', 3493, 'kirmizi'),
                  ('ONAMA', 'YARGITAY', '14.10.2026', 3765, 'altin')],
        # Metne göre: adına başka plakalı araç için idari para cezası tutanağı; "araç benim değil, kimliğimi kullanan
        # kişiden şikâyetçiyim" başvurusu üzerine tutanağı düzenleyen polis memuru (katılan) hakkında soruşturma;
        # 12.12.2015 bilirkişi raporu: tutanaktaki imza sanığın eli ürünü. 23.06.2016 suç uydurma (TCK 271) mahkûmiyeti;
        # 22.12.2022 bozma (gerçek kişi gösterildiği için iftira); 28.03.2024 iftira 10 ay; 08.01.2025 bozma (bozmaya karşı
        # diyecekleri sorulmadı + kazanılmış hak); 15.01.2026 iftira, kazanılmış hak gereği 2 ay 15 gün; 14.10.2026 onama (oy birliği).
        tahmin='CEZA ALIR', dogru=True,
        kalp_not='Hüküm onandı; ceza, kazanılmış hak nedeniyle 2 ay 15 gün.',
        karne_baslik='Trafik cezası itirazı', karne_tahmin='Ceza alır', karne_sonuc='İftira: onama',
        toplam_dogru=6, toplam_yanlis=6,
        kunyeler=['Yargıtay 8. CD · 14.10.2026 · E. 2026/6539 · K. 2026/11402'],
    ),
}
