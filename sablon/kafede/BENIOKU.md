# Kafede Hukuk — @emsalvarmi video dizisi

## GÜNCEL BİÇİM: KISA + SESLİ (kullanıcının 21.11.2026 talimatı; 21.11.2026 09:15'ten itibaren)

Kullanıcıyla konuşulan ilke: insanlar mahkeme kararını değil, **başlarına gelebilecek tuhaf/tanıdık durumu** merak eder. Bu yüzden video **durumla açılır**, gerçek karar sonda sürpriz olarak gelir. Veriye göre (126 Reels) izlenmeyi belirleyen şey ilk 3 saniyede kaydırılma oranıydı; ortalama izleme süresi 8–9 sn'ydi. Seslendirmeli videolar ortalama 11,2 sn, sessizler 7,1 sn izlendi.

Motor: `kafede_kisa.py` (eski `kafede.py`'nin karakter, şerit, etiket parçalarını kullanır).

### Akış (25–35 sn)
1. **İlk kareden itibaren kanca kartı:** kırmızı "GERÇEK DAVA" etiketi + 2–3 satırlık durum + altın renkli kısa soru ("Çekmek suç mu?") + "MERT TAHMİN EDİYOR · SİZ DE EDİN". Ayşe aynı anda soruyu sesli sorar. Kapak = bu kart (karakterler altta görünür).
2. **Mert'in tahmini hemen gelir** (2. satır); masaya "MERT'İN TAHMİNİ" etiketi düşer.
3. **Ayşe 1–2 satırda olayı anlatır** ("Gerçek dava. …"), üstte "Dosyanın yolculuğu" şeridi ve gün sayacı ilerler.
4. **Sonuç satırı** (kısa: "Ama Yargıtay bozdu.") + büyük karar mührü (BOZMA / ONAMA …) + Mert'in etiketi ✓ ya da ✗.
5. **Neden: tek satır**, sonra **Mert'in kapanış cümlesi** (ders + "Bildim!/Bunu bilemedim.").
6. **Kapanış kartı (≈3,8 sn):** Mert'in karnesi + toplam, "Siz ne tahmin etmiştiniz? Yorumlara yazın.", künye, kısa not (ör. "Bozma suçluluk ya da masumiyet tespiti değildir."), "Genel bilgilendirme amaçlıdır; hukuki görüş değildir.", "Karakterler temsilîdir; dosyanın tarafları değildir."

Toplam 6–7 satır, ≈ 55–70 kelime. Balonlarda ekranda görünen metin = seslendirilen metin (sesi kapalı izleyen de takip eder). Kanca satırı balon olmaz (kart taşır).

### Bölüm dosyası
`2026/<YYYY-MM-DD>-kafede/bolumler.py` (karar verisi: no, saat, duraklar, tahmin, dogru, karne, kunyeler, kalp_not …; eski biçimdeki alanlar) **ve** aynı klasörde `kisa.py`:
```
KISA = {'b9': dict(kaynak='b9_<konu>', kanca=['…', '…'], kanca_soru='… mu?',
        satirlar=[('A', 'ekrandaki metin', 'seslendirilecek metin ya da None', 'kanca'|'tahmin'|'sonuc'|None, durak_indeksi|None), …])}
```
- Örnek: `2026/2026-11-21-kafede/kisa.py`. `bolum(k)` ve `metin_tsv()` işlevlerini aynen kopyalayın.
- Konuşan: `'A'` = Ayşe (kararı okumuş, anlatır), `'M'` = Mert (tahmin eder, tepki verir).
- Tam 1 `kanca`, 1 `tahmin`, 1 `sonuc` satırı. Sonuç satırının durağı son durak olmalı (mühür onu gösterir).
- Sayılar seslendirilecek metinde yazıyla ("elli altı bin lira"), ekranda rakamla.

### Seslendirme (Mac'te Gemini; iki ayrı ses)
1. `python3 kisa.py > metin.tsv` → kimlikler `<anahtar>_<A|M>_<nn>` (ör. `b7_A_02`).
2. `/Users/batinyilmaz/Movies/KararOdasi/metin.tsv` olarak yaz (device_bash ya da device_commit_files), sonra `seslendir_istek.txt`'ye tarih yaz.
3. `seslendir_gemini.sh` `_A_` geçen satırları `ses_adi_A.txt` (Sulafat) ve `ses_tarzi_A.txt`, `_M_` geçenleri `ses_adi_M.txt` (Puck) ve `ses_tarzi_M.txt` ile okur. Bu dosyalar Mac'te hazır; değiştirmeyin.
4. Otomatik başlatma (LaunchAgent) çoğu zaman çalışmıyor: 3 dk içinde `ses_gemini/` altında yeni `<anahtar>_*.wav` yoksa kullanıcıya SendUserMessage ile "Karar Odası klasöründeki seslendir_gemini.applescript dosyasına bir kez çift tıklayın" yazın. 27 satır ≈ 3–4 dk sürer; `ses_gemini/durum.txt` "Tamamlandı … Ayşe: Sulafat / Mert: Puck" olur.
5. wav'ları device_stage_files ile buluta alın, kendi çalışma klasörünüze kopyalayın.
6. **gemini_anahtar.txt dosyasını ASLA okumayın, kopyalamayın.**

**Ses gelmezse (Mac kapalı ya da çift tıklanmadı) o saat BOŞ KALIR** (kullanıcının 21.11.2026 tercihi); sessiz video paylaşılmaz, kullanıcıya bildirilir. (Motor `--ses` verilmeden sessiz kare üretebilir; bu yalnızca kontrol kareleri içindir.)

### Üretim
```
cd sablon/kafede
python3 kafede_kisa.py b7 --dosya ../../2026/<tarih>-kafede/kisa.py --ses <wav klasörü> --kare 0.5 8 20 30   # kontrol kareleri (BAK!)
python3 kafede_kisa.py b7 --dosya ... --ses ... --cikti <klasör>/reel.mp4 --kapak <klasör>/kapak.jpg
```
- Sesler 1,12 kat hızlandırılır (perde değişmez); süre 40 sn'yi aşarsa biraz daha. Hedef 25–35 sn.
- Kontrol: ffprobe ile 1080×1920, ses akışı, süre. Kanca kartı, mühür anı ve kapanış kartı karelerine bakın.
- Bir bölüm 2 çekirdekte ≈ 2–3 dk; iki bölüm aynı anda üretilebilir.

### Paylaşım
- Yükleme: tüm klasörler TEK `sablon/video/medya.sh <klasör>...` çağrısıyla (her bağlantı 200).
- Instagram: REEL, `isAiGenerated: true`, kapak = kapak.jpg. Açıklama: soru + "Yargıtay ne dedi?" / "… Kurulu ne dedi?", "Kafede Hukuk · Bölüm N · Gerçek dava, Mert tahmin ediyor 🎧", 2 kısa paragraf, "Mert'in karnesi: X doğru · Y yanlış. Siz ne tahmin etmiştiniz? Yorumlara yazın.", künye, uyarı ("Bu paylaşım genel bilgilendirme amaçlıdır; hukuki görüş değildir. Her somut olay kendi koşulları içinde değerlendirilmelidir. Karakterler temsilîdir; dosyanın tarafları değildir. Seslendirme sentetik sestir."), en fazla 5 hashtag (#cezahukuku #kafedehukuku dahil).
- X: aynı video (Instagram yanıtındaki static.metricool.com adresi), tek tweet: "Kafede Hukuk · Bölüm N" + boş satır + soru + "Mert tahmin etti; Yargıtay ne dedi? 🎬" + boş satır + kısa künye + boş satır + "#cezahukuku #kafedehukuku" (≤ 280).
- Kayıt: `kafede-hukuk.md` (no, tarih/saat, künye, tahmin, sonuç, toplam), `paylasilanlar.md`, `paylasilanlar-x.md`; açıklamalar `2026/<tarih>-kafede/aciklamalar.md`.

## Yazım kuralları (her iki biçimde)
- Kararın tam metni okunur (UYAP emsal araçları ya da LexPanel `karar_ara`/`karar_getir`). Yalnızca metindekiler; iddia ile mahkemenin kabulü ayrılır ("İddiaya göre", "Savunmasına göre").
- Karar seçimi: hukuki önemine göre değil, **"bunu bir arkadaşına gönderir mi?"** testine göre — günlük hayattan, herkesin başına gelebilecek, sonucu ters köşe olaylar (para, bulunan eşya, alışveriş, kira, komşuluk, sosyal medya, banka/ATM, kargo…). Tarihleri metinde yazan, birden çok aşamalı dosyalar şerit için iyidir.
- Kimlik belirleyici bilgi yok (kişi/şirket adı, yer adı, plaka). Masumiyet karinesi: bozma, düşme, kanun yararına bozma kararlarında bunun suçluluk ya da masumiyet tespiti olmadığı söylenir (kapanış notunda).
- Şiddet ayrıntısı, ölüm/yaralanma ağırlıklı olaylar, cinsel içerik, çocuklar, kamuoyunda süren davalar ve siyaset yok.
- Mert'in tahminleri doğal olmalı; ne hep bilir ne hep bilemez. Karne `kafede-hukuk.md`'den devam eder.
- Avukatlık reklam yasağı: iletişim bilgisi, "bize ulaşın", "uzman" yok.

## ESKİ BİÇİM (20.11.2026; artık kullanılmıyor): uzun, seslendirmesiz
Motor `kafede.py`: 3 sn giriş kartı, 11–12 balon, kararın kalbi (birebir alıntı) kartı, karne, kapanış; 45–60 sn. Bölüm tanımı `bolumler.py` (`2026/2026-11-20-kafede/bolumler.py`). Kısa biçimde kararın kalbi videoda yok; birebir alıntı gerekiyorsa açıklamaya konabilir.
