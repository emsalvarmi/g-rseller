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
