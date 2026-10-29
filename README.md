# Emsal Var mı? – görseller ve şablonlar

Bu depo @emsalvarmi Instagram hesabının gönderi görsellerini barındırır. Metricool görselleri buradaki `raw.githubusercontent.com` bağlantılarından alıp kendi sunucusuna kopyalar.

## Klasörler

- `2026/<YYYY-MM-DD>-<konu>/01.png … 06.png`: yayınlanan gönderilerin slaytları.
- `sablon/ornek-*/`: slayt şablonları (`.dc.html`). Yeni gönderi için en uygun örneği kopyalayıp yalnızca metinleri değiştirin.
- `sablon/render.js`: `.dc.html` dosyalarını 1080×1350 PNG'ye çevirir.
- `paylasilanlar.md`: paylaşılan kararların listesi. Aynı kararın tekrar paylaşılmaması için her yeni gönderiden sonra güncellenir.

## Slayt düzeni (6 slayt, 1080×1350, Instagram 4:5)

1. **Kapak** (lacivert zemin): üstte "YARGITAY KARARI" ve "1 / 6"; ortada daire adı, kısa altın çizgi, merak uyandıran serif başlık, altın italik alt başlık, tarih · E. · K. künyesi; altta "@emsalvarmi" ve "Kaydırın →".
2. **Olay** (açık zemin): etiketli satırlar ya da numaralı zaman çizelgesi.
3. **Kural / Savunma** (açık zemin): ilgili kanun hükmü ya da karşı tarafın savunması.
4. **Değerlendirme** (lacivert): mahkemenin gerekçesi, 1-2-3 numaralı maddeler; altta "… onadı/bozdu" satırı.
5. **Pratikte / Bilmeniz gerekenler** (açık zemin): kart hâlinde pratik öneriler.
6. **Özetle** (lacivert): tek cümlelik ana fikir, kısa açıklama, künye, "Bu paylaşım genel bilgilendirme amaçlıdır. Her somut olay kendi koşulları içinde değerlendirilmelidir." ve "@emsalvarmi".

Her slaytta üst satırda bölüm etiketi (ör. "02 · OLAY") ve sayfa numarası, alt satırda "@emsalvarmi" ve ok bulunur (son slaytta ok yok).

### Renkler ve yazı tipleri

- Lacivert zemin `#14233C`, açık zemin `#F5F6F8`, kart zemini `#FFFFFF` (kenarlık `#E1E4EA`).
- Altın: lacivert üzerinde `#D2AE66`, açık zemin üzerinde `#7E6026`.
- Metin: açık zeminde başlık `#14233C`, gövde `#3D4757`, ikincil `#5B6576`; lacivert zeminde ikincil `#A9B4C6`, çizgiler `#3A4A64`.
- Başlıklar: Source Serif 4 (600, gerekirse italik). Gövde: Inter (400/500/600).
- Kenar boşluğu 96 px; gövde metni 32 px; hiçbir metin 24 px'ten küçük olmaz.
- Metin uzunluğu sabit 1350 px yüksekliğe sığmalı; uzun metni kısaltın.

## Görsel üretimi

```bash
cd sablon
npm install @fontsource/inter@5.0.18 @fontsource/source-serif-4@5.0.19
node render.js <kaynak-klasör> <çıktı-klasörü> Main.dc.html <2>.dc.html <3>.dc.html <4>.dc.html <5>.dc.html <6>.dc.html
```

Dosyalar verilen sırayla `01.png … 06.png` olarak yazılır. Yayından önce her PNG'ye bakıp taşma ya da bölünmüş kelime olmadığını kontrol edin.

## İçerik kuralları

- Karar her zaman UYAP emsal karar veritabanındaki tam metinden okunur; yalnızca metinde yazanlar kullanılır.
- Tarafların iddiası ile mahkemenin tespiti ayrı tutulur. Yargıtay yalnızca kısa bir onama yaptıysa gerekçe ilk derece ve bölge adliye mahkemesine atfedilir.
- Künye: daire, karar tarihi, E. ve K. numarası.
- Avukatlık reklam yasağı gereği ofise yönlendirme, iletişim çağrısı ya da tanıtım dili kullanılmaz; taraf kimlikleri ve dosya ayrıntıları paylaşılmaz.
- Instagram açıklaması: en fazla 5 hashtag, etkileşim için bir soru ve "Bu paylaşım genel bilgilendirme amaçlıdır." satırı.

## Reels videoları (günde 3 video)

Hesabın ana içeriği 1080×1920 Reels videolarıdır. Her video bir JSON senaryodan (`spec.json`) otomatik üretilir.

- `sablon/video/engine.html`: senaryoyu sahnelere çeviren zaman çizelgesi motoru.
- `sablon/video/make_video.js`: sahneleri kare kare çekip H.264 videoya çevirir, sesi ekler, kapak görselini yazar.
- `sablon/video/audio.py`: videonun zaman çizelgesinden telifsiz müzik ve efekt üretir (hazır ses dosyası kullanılmaz).
- `sablon/video/ornek/*.json`: örnek senaryo.
- Yayınlanan videolar: `2026/<YYYY-MM-DD>-<konu>/reel.mp4`, `kapak.jpg`, `spec.json`.

### Üretim

```bash
cd sablon
npm install @fontsource/inter@5.0.18 @fontsource/source-serif-4@5.0.19
pip install --break-system-packages numpy scipy   # yoksa
# Önce kontrol kareleri (tam boy JPG): sahnelerin en kalabalık anlarına bakın, taşma ve bölünme olmasın.
node video/make_video.js <spec.json> <çıktı-klasörü> ./node_modules --snap 4,15,30,45,60
# Sonra tam video:
node video/make_video.js <spec.json> <çıktı-klasörü> ./node_modules
```

Playwright ve ffmpeg gerekir. Çıktı: `reel.mp4`, `kapak.jpg`, `timeline.json`.

### Okuma süresi kuralı

Yazılar okunmadan geçmemeli. Motor her metnin ekranda kalma süresini kelime sayısından hesaplar: `max(1,8 sn; kelime × 0,38 sn + 1,0 sn)`. Aynı anda ekranda kalan metinler için sahne, toplam kelime × 0,34 sn + 1,2 sn'den önce bitmez. Bu yüzden senaryodaki metinleri kısa tutmak videoyu kısaltmanın tek yoludur. Hedef toplam süre yaklaşık 60 sn (en fazla 65 sn). Bunun için:

- `steps` en fazla 2 adım; kart metinleri 4–8 kelime.
- `reveal` sahnesinde `detail` kullanmayın; madde numarasını Instagram açıklamasına yazın.
- `lessons` tek madde (ör. `["Unutmayın:", "…"]`), çünkü cevap zaten `reveal` sahnesinde verildi.
- `quiz` için `countdown: 4`.
- Süre 65 sn'yi geçerse önce `lessons`, sonra `reveal.extra`, sonra `twist` metnini kısaltın.

### Senaryo biçimi

```json
{
  "court": "Yargıtay 2. Hukuk Dairesi",
  "kunye": "30.06.2026 · E. 2026/1776 · K. 2026/7439",
  "note": "Karar oy birliğiyle verildi.",
  "scenes": [
    { "type": "hook", "lines": ["kısa çarpıcı cümle", "durumu açan cümle", "izleyiciye soru"], "icon": "gold", "stamp": "ÇALINTI", "siren": false },
    { "type": "steps", "kicker": "NE OLDU?", "items": [ { "title": "...", "card": { "kind": "info", "icon": "car", "title": "...", "value": "...", "tag": "..." } } ] },
    { "type": "twist", "big": "Ama…", "text": "...", "icon": "car", "badge": { "label": "ŞASİ NO", "from": "...", "to": "..." }, "tape": "EL KONULDU", "siren": true },
    { "type": "quiz", "question": "...", "options": [ { "title": "...", "sub": "..." }, { "title": "...", "sub": "..." } ], "answer": 1, "countdown": 5 },
    { "type": "reveal", "title": "Bozuldu.", "text": "...", "detail": "ilgili madde", "extra": { "label": "ÜSTELİK", "text": "..." } },
    { "type": "lessons", "items": [["Kalın kısım:", "devamı"], ["...", "..."]] },
    { "type": "outro" }
  ]
}
```

- `steps` kart türleri: `info` (icon, title, value, tag), `chat` (title, messages[]), `check` (title, rows[], stamp, good), `seal` (title, seal, sealSub, caption), `text` (icon, text).
- Çizimler (`icon`): `car`, `house`, `phone` (sosyal medya/mesaj), `call` (bilinmeyen numaradan gelen arama), `briefcase`, `family`, `document`, `gavel`, `money`, `gold`.
- `outro` isteğe bağlı `line` (ör. uyarı niteliğindeki videolarda "Bu videoyu anne ve babanıza gönderin.") ve `cta` (düğme metni) alır. Paylaşılmaya uygun konularda `line` kullanın; videonun gönderilmesini artırır.
- `quiz` 2 ya da 3 seçenek alır; `answer` doğru seçeneğin sırasıdır (0'dan başlar). Cevap mutlaka kararın hüküm fıkrasıyla aynı olmalı.
- Kanca (`hook`) ilk 5 saniyede soruyu sormalı; ilk satır videonun ilk karesinde görünür.
- `stamp`, `siren`, `badge`, `tape` isteğe bağlıdır; yalnızca olaya uyuyorsa kullanın.

### Instagram açıklaması

İlk satır anahtar kelimeli bir başlık (ör. "Boşanmada düğün altınları kimin? Yargıtay ne dedi?"), ardından 2–3 cümlelik özet, künye, izleyiciye soru, "Bu paylaşım genel bilgilendirme amaçlıdır." satırı ve en fazla 5 hashtag (konuya özgü 3 + #yargıtay #hukuk gibi 2 genel).
