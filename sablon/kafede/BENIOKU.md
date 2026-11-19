# Kafede Hukuk — @emsalvarmi video dizisi (20.11.2026'dan itibaren)

Kullanıcının 19.11.2026 talimatı: Instagram ve X videoları bu biçimde üretilir. **Seslendirme yoktur**; konuşma, iki çizim karakterin (Ayşe ve Mert) balonlarında yazılı olarak akar. Eski Karar Odası (seslendirmeli) şablonu ve Mac'te seslendirme ADIMI ARTIK GEREKMEZ.

## Biçim (her bölümde aynı)
1. **Giriş kartı (≈3 sn):** 3 satırlık merak uyandıran soru + "MERT TAHMİN EDECEK. SİZ DE EDİN."
2. **Kafe sahnesi:** Ayşe (solda, kararı okumuş) olayı anlatır, Mert (sağda) sorar. Arka plan paylaşım saatine göre: 09:15 `sabah`, 13:15 `ogle`, 17:15 `aksamustu`, 21:15 `gece`.
3. **Dosyanın yolculuğu (üst şerit):** olaydan son karara kadar 4–5 durak (OLAY, ilk derece, istinaf/daire, itiraz/direnme, son karar) ve "GEÇEN SÜRE ... GÜN" sayacı. Tarihler YALNIZCA karar metninden; gün sayısı Python ile hesaplanır. Tarihi tam bilinmeyen durakta gün `None` (sayaç ilerlemez; yalnızca yıl yazılabilir).
4. **Mert'in tahmini:** Mert bir tahmin söyler; masaya "MERT'İN TAHMİNİ" etiketi düşer. Sonuç gelince etiket yeşil onay ya da kırmızı çarpı alır. Tahminler doğal olmalı; Mert ne hep bilir ne hep bilemez.
5. **Kararın kalbi:** karar gerekçesinden BİREBİR alıntı (… ile kısaltılabilir, kelime değiştirilmez); belirleyici ibare sarı kalemle işaretlenir. Altına kısa not (ör. "Bozma sonucu belirlemez…").
6. **Mert'in karnesi:** bölüm, tahmin, Yargıtay sonucu, ✓/✗ ve TOPLAM. Toplam `kafede-hukuk.md` dosyasındaki son satırdan devam eder.
7. **Kapanış:** "Emsal var mı? Kararı bil, hakkını bil." + künye + "Genel bilgilendirme amaçlıdır; hukuki görüş değildir. Karakterler temsilîdir; dosyanın tarafları değildir."

## Yazım kuralları
- Kararın tam metni okunur (UYAP emsal araçları ya da LexPanel `karar_ara`/`karar_getir`). Yalnızca metindekiler; iddia ile mahkemenin kabulü ayrılır ("İddiaya göre", "Savunmasına göre").
- Kimlik belirleyici bilgi yok (kişi/şirket adı, yer adı, plaka). Masumiyet karinesi: bozma, düşme, kanun yararına bozma kararlarında bunun suçluluk ya da masumiyet tespiti olmadığı söylenir.
- Şiddet ayrıntısı, ölüm/yaralanma ağırlıklı olaylar, cinsel içerik, çocuklar, kamuoyunda süren davalar ve siyaset yok. Oyunlaştırılmış bu biçim için hafif ve gündelik olaylar seçilir (para, bulunan eşya, kira, komşuluk, alışveriş, sosyal medya…).
- Diyalog 11–12 balon, kısa cümleler; video 45–60 sn (motor zamanlamayı otomatik sıkıştırır, 60,4 sn üstü olmamalı).
- Avukatlık reklam yasağı: iletişim bilgisi, "bize ulaşın", "uzman" yok.

## Üretim
```
cd sablon/kafede
python3 kafede.py <anahtar> --dosya ../../2026/<YYYY-MM-DD>-kafede/bolumler.py --kare 1.9 20 35    # kontrol kareleri (BAK!)
python3 kafede.py <anahtar> --dosya ... --cikti /tmp/kafede/<klasör>/reel.mp4 --kapak /tmp/kafede/<klasör>/kapak.jpg
```
Gerekenler: python3, pillow, numpy, ffmpeg (fontlar `fonts/` klasöründe). Bir bölüm 2 çekirdekte ≈ 2–3 dk sürer; iki bölüm aynı anda üretilebilir.
Bölüm tanımı örneği: `2026/2026-11-20-kafede/bolumler.py` (alanlar dosyanın başında açıklanır).

Yükleme: tüm klasörler TEK `sablon/video/medya.sh <klasör>...` çağrısıyla (her bağlantı 200). Sonra Metricool:
- Instagram: REEL, `isAiGenerated: true`, kapak = kapak.jpg. Açıklama: soru + "Yargıtay ne dedi?" / "… Kurulu ne dedi?", "Kafede Hukuk · Bölüm N", 2 kısa paragraf, "Mert'in karnesi: X doğru · Y yanlış. Siz ne tahmin etmiştiniz? Yorumlara yazın.", künye, uyarı metni (yukarıdaki kapanıştaki iki cümle + "Her somut olay kendi koşulları içinde değerlendirilmelidir."), en fazla 5 hashtag (#cezahukuku #kafedehukuku dahil).
- X: aynı video (Instagram yanıtındaki static.metricool.com adresi), tek tweet: "Kafede Hukuk · Bölüm N" + boş satır + soru + "Mert tahmin etti; Yargıtay ne dedi? 🎬" + boş satır + kısa künye + boş satır + "#cezahukuku #kafedehukuku" (≤ 280).
- Kayıt: `kafede-hukuk.md` tablosuna her bölüm (no, tarih/saat, künye, tahmin, sonuç, toplam), `paylasilanlar.md` ve `paylasilanlar-x.md`.
