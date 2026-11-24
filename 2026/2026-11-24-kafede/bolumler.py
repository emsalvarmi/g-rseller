"""Kafede Hukuk bölümleri — 23.11.2026 (Bölüm 13–16). Her bölüm tek bir Yargıtay kararının tam metninden hazırlanır.
duraklar: (etiket1, etiket2, tarih, olaydan_bu_yana_gun|None, renk)
Gün sayıları Python ile hesaplandı (datetime.date farkı); olay tarihi metinde gün olarak yazmıyorsa None.
"""

BOLUMLER = {
    'b13_atm': dict(
        no=13, saat='ogle',
        soru=['Yaşlı adam ATM’de yardım istedi.', 'Kartı takıldı, 530 lirası gitti.', 'Hangi suç?'],
        duraklar=[('OLAY', 'ATM', '18.09.2009', 0, 'gri'),
                  ('DOLANDIRICILIK', 'ASLİYE CEZA', '14.04.2011', 573, 'kirmizi'),
                  ('YAĞMA', 'AĞIR CEZA', '11.11.2020', 4072, 'kirmizi'),
                  ('DİRENME', 'AĞIR CEZA', '09.03.2023', 4920, 'gri'),
                  ('DÜŞME', 'GENEL KURUL', '19.11.2025', 5906, 'altin')],
        # Metne göre: 18.09.2009'da emekli maaşını çekmek için ATM'ye gelen yaşlı mağdur, tanımadığı bir kişiden yardım
        # istedi; kart takıldı, şifre girildi; CGK'nın kabulüne göre sanık işlemin yapıldığı cihazdaki 530 TL'yi aldı,
        # kimliği belirlenemeyen kişi kartı mağdura verip ayrıldı. Sanık olayla ilgisi olmadığını savundu.
        # Asliye ceza 14.04.2011 dolandırıcılık (2 yıl + 4.000 TL APC); 15. CD 20.06.2019 görevsizlik (yağma olabilir)
        # için bozma; ağır ceza 11.11.2020 nitelikli yağma 4 yıl 2 ay; 6. CD 26.10.2022 "hırsızlık boyutunda" bozma;
        # ağır ceza 09.03.2023 direnme. CGK 19.11.2025: kamerada cebir yok → yağma değil; para rızasız alındı →
        # dolandırıcılık değil; kart üzerindeki zilyetlik sürüyor → TCK 245 değil; para fiziken alındı → bilişim
        # yoluyla hırsızlık değil; TCK 141/1 hırsızlık. 8 yıllık asli zamanaşımı 14.04.2019'da doldu → bozma + düşme (oy birliği).
        tahmin='DOLANDIRICILIK', dogru=False,
        kalp_not='Düşme kararı suçluluk ya da masumiyet tespiti değildir.',
        karne_baslik='ATM’de yardım', karne_tahmin='Dolandırıcılık', karne_sonuc='Hırsızlık; zamanaşımı: düşme',
        toplam_dogru=6, toplam_yanlis=7,
        kunyeler=['Yargıtay Ceza Genel Kurulu · 19.11.2025 · E. 2024/500 · K. 2025/485'],
    ),
    'b14_whatsapp': dict(
        no=14, saat='aksamustu',
        soru=['Satıcı WhatsApp’tan “cahil, gerzek” yazdı;', 'müşteri “Sensin cahil!” dedi.', 'Müşteri ceza alır mı?'],
        duraklar=[('MESAJLAŞMA', 'WHATSAPP', 'suç tarihi', None, 'gri'),
                  ('CEZA YOK', 'İLK DERECE', '2015', None, 'gri'),
                  ('ONAMA', 'YARGITAY', '23.05.2023', None, 'altin')],
        # Metne göre (iddia): internetten ücretini göndererek ürün alan sanık, teslimat gecikince ve satıcı (katılan)
        # hakkındaki olumsuz yorumları görünce WhatsApp'tan ürünün bir an önce teslimi için yazıştı; katılan
        # "..cahil..gerzek..senin terbiyenden şüphe ederim..ruh hastaları.." diye yazdı, sanık "..sensin cahil..sensin
        # gerzek edepli ol..." diye karşılık verdi. Yerel mahkeme hakaretten CMK 223/4-c ceza verilmesine yer olmadığı;
        # Yargıtay 4. CD: sanık hakareti katılanın hakaretine ve haksız fiiline karşı işledi → onama (oy birliği).
        tahmin='CEZA ALIR', dogru=False,
        kalp_not='Ceza verilmesine yer olmadığı kararı onandı.',
        karne_baslik='WhatsApp’ta karşılık', karne_tahmin='Müşteri ceza alır', karne_sonuc='Ceza verilmesine yer yok: onama',
        toplam_dogru=6, toplam_yanlis=8,
        kunyeler=['Yargıtay 4. CD · 23.05.2023 · E. 2021/9548 · K. 2023/18825'],
    ),
    'b15_telefon': dict(
        no=15, saat='gece',
        soru=['Tamirden dönen telefon yanlış dükkâna', 'gönderildi. Dükkân sahibi iade etmedi.', 'Hangi suç?'],
        duraklar=[('YANLIŞ ADRES', 'GÖNDERİ', 'suç tarihi', None, 'gri'),
                  ('GÜVENİ K.K.', 'İLK DERECE', 'mahkûmiyet', None, 'kirmizi'),
                  ('BOZMA', 'YARGITAY', '24.06.2020', None, 'altin')],
        # Metne göre: katılanın camı kırılan telefonu, alındığı iş yerince tamir için başka ildeki bir iş yerine
        # gönderildi; garanti dışı olduğu için iade edilirken sehven sanığın başka ilçedeki iş yerine gönderildi;
        # sanık kendisine yanlışlıkla gönderilen telefonu iade etmedi. İlk derece TCK 155/2 hizmet nedeniyle güveni
        # kötüye kullanmadan mahkûmiyet; Yargıtay 15. CD: eylem TCK 160 kaybolmuş veya hata sonucu ele geçmiş eşya
        # üzerinde tasarruf (uzlaştırma kapsamındaki suçlardan, CMK 253/1-b); suç vasfında yanılgı → bozma (oy birliği).
        tahmin='HATA SONUCU', dogru=True,
        kalp_not='Bozma suçluluk ya da masumiyet tespiti değildir.',
        karne_baslik='Yanlış dükkâna giden telefon', karne_tahmin='Hata sonucu ele geçen eşya', karne_sonuc='Bozma: TCK 160',
        toplam_dogru=7, toplam_yanlis=8,
        kunyeler=['Yargıtay 15. CD · 24.06.2020 · E. 2020/2957 · K. 2020/6614'],
    ),
    'b16_hizmetci': dict(
        no=16, saat='gece',
        soru=['Önüne park eden araç çekilirken', 'trafik polisine “Sen benim hizmetçimsin” dedi.', 'Hakaret mi?'],
        duraklar=[('ARAÇ ÇEKME', 'TARTIŞMA', 'suç tarihi', None, 'gri'),
                  ('PARA CEZASI', 'İLK DERECE', '2016', None, 'kirmizi'),
                  ('BOZMA', 'YARGITAY', '26.03.2024', None, 'altin')],
        # Metne göre: sanık, aracının önüne park eden aracın çekilmesiyle ilgili trafik polisi katılanla tartıştı;
        # yerel mahkeme kamu görevlisine hakaretten (TCK 125/1, 125/3-a, 125/4) 7.080 TL adli para cezası verdi.
        # Yargıtay 4. CD: "Sen benim hizmetçimsin" kaba ifade, onur/şeref/saygınlığı rencide edici boyutta değil;
        # hakaretin unsurları oluşmadı; kabule göre ek savunma hakkı verilmeden 125/4 uygulandı (CMK 226) → bozma (oy birliği).
        tahmin='HAKARET DEĞİL', dogru=True,
        kalp_not='Bozma suçluluk ya da masumiyet tespiti değildir.',
        karne_baslik='“Sen benim hizmetçimsin”', karne_tahmin='Hakaret değil', karne_sonuc='Bozma: unsurlar oluşmadı',
        toplam_dogru=8, toplam_yanlis=8,
        kunyeler=['Yargıtay 4. CD · 26.03.2024 · E. 2021/24502 · K. 2024/3960'],
    ),
}
