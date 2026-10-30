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
- `sablon/video/medya.sh`: videoları tek bir `medya` dalına yükler ve herkese açık bağlantılarını yazdırır (aşağıya bakın).
- Ana dalda (main) her video için yalnızca senaryo tutulur: `2026/<YYYY-MM-DD>-<konu>/spec.json` (ve gerekirse `aciklama.txt`). 29 Ekim 2026 ve öncesindeki videolar main'de duruyor; yenileri main'e eklenmez.

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

### Yayınlama (depo büyümesin diye)

Günde 15 video (yaklaşık 120 MB) main'e eklenirse depo birkaç haftada GitHub sınırlarına yaklaşır. Bu yüzden:

1. Depoyu sığ klonlayın: `git clone --depth 1 --branch main https://github.com/emsalvarmi/g-rseller.git`.
2. Videoları üretin (`reel.mp4`, `kapak.jpg` her biri kendi klasöründe, klasör adı `<YYYY-MM-DD>-<konu-ascii>`).
3. `sablon/video/medya.sh <klasör>...` ile tüm günün videolarını tek seferde `medya` dalına yükleyin. Dal her çalıştırmada üzerine yazılır; komut her dosya için bağlantıyı ve HTTP kodunu yazdırır (200 olmalı).
4. Hemen ardından Metricool'de planlayın ve yanıttaki `media` ile `videoThumbnailUrl` adreslerinin `static.metricool.com` olduğunu kontrol edin (Metricool dosyayı kopyalamış demektir).
5. `spec.json` dosyalarını ve `paylasilanlar.md` güncellemesini main'e commit edip push edin.

Not: Bu ortamda uzak dal silinemiyor; `medya-test` adlı küçük bir deneme dalı kaldı, yok sayın.

### Güncel yayın planı ve içerik talimatı

- **Sıklık:** her gün 09:00'dan 23:00'e kadar saat başı 1 Reels (09:00, 10:00, …, 23:00; günde 15 video).
- **Konu (kullanıcının 29.10.2026 talimatı, ikinci bir talimata kadar):** yalnızca aile hukuku kararları ve özellikle ilgi çekici konular. Örnek alanlar: aldatma ve sadakat, şiddet ve ekonomik şiddet, eşin ailesinin müdahalesi, sosyal medya ve telefon delilleri, kusur ve maddi-manevi tazminat, nafaka (tedbir, iştirak, yoksulluk; artırım, azaltım, kaldırma), velayet ve çocukla kişisel ilişki, düğün takıları ve ziynet, nişan ve hediyeler, mal rejimi ve katılma alacağı, mal kaçırma, aile konutu, soybağı ve babalık, koruma kararları (6284). Kararlar çoğunlukla Yargıtay 2. Hukuk Dairesi ve Hukuk Genel Kurulundan gelir.
- Aynı gün aynı alt konudan en fazla 2 video olsun; gün içinde konuları karıştırın. En çekici kararları akşam saatlerine (19:00–22:00) koyun.
- Yalnızca kısa bir onama ya da usul kararı olan, olayı anlatmayan kararları seçmeyin; olay ve gerekçesi metinde yazan kararları seçin.

### X (Twitter) planı

X hesabı (@emsalvarmi) Metricool'de aynı markaya bağlı (network: `twitter`).

**Konu (kullanıcının 30.10.2026 talimatı, ikinci bir talimata kadar): X'te YALNIZCA SPK, fonlar ve piyasa manipülasyonu (piyasa dolandırıcılığı) konuları.** Instagram bu kuraldan etkilenmez; Instagram'da aile hukuku videoları devam eder. X içeriği Instagram kararlarından ayrı araştırılır. "Sizce?" soru gönderileri şimdilik ASKIDA.

Kaynaklar:
- UYAP emsal karar araçları: Yargıtay ceza daireleri (piyasa dolandırıcılığı, bilgi suistimali, izinsiz sermaye piyasası faaliyeti, güveni kötüye kullanma), Danıştay 13. Daire (SPK idari para cezaları, işlem yasakları, tedbirler), bölge adliye ve asliye ticaret mahkemeleri (yatırımcı tazminatı, fon, portföy yönetimi, aracı kurum uyuşmazlıkları). Faydalı tırnaklı aramalar: "piyasa dolandırıcılığı", "işlem bazlı piyasa dolandırıcılığı", "bilgi bazlı piyasa dolandırıcılığı", "piyasa bozucu eylem", "bilgi suistimali", "yatırım fonu", "portföy yönetim şirketi", "Sermaye Piyasası Kurulu" "idari para cezası", "örtülü kazanç aktarımı", "işlem yasağı".
- SPK'nın resmi duyuruları ve bültenleri (spk.gov.tr) ile güvenilir haber kaynakları; güncel gelişmeler için WebSearch/WebFetch. Haber niteliğindeki notlarda yalnızca resmi açıklamada ya da birden fazla güvenilir kaynakta yer alan bilgiler kullanılır, tarih belirtilir.
- Kanun metinleri (6362 sayılı SPKn): m. 107/1 işlem bazlı piyasa dolandırıcılığı (3–5 yıl hapis, 5.000–10.000 gün adli para cezası; para cezası menfaatten az olamaz), m. 107/2 bilgi bazlı (3–5 yıl hapis, 5.000 güne kadar adli para cezası), m. 107/3 etkin pişmanlık (menfaatin iki katı, en az 500.000 TL). Başka maddeleri kullanmadan önce metni iki güvenilir kaynaktan doğrula.

Hassasiyet kuralları (çok önemli):
- Devam eden soruşturma ve davalarda kişi, şirket, fon ya da hisse adı verme; suçlu ya da suçsuz gibi hüküm kurma. Bu tür notlarda "Bu kararlar suçun sabit olduğu anlamına gelmez" gibi masumiyet karinesini hatırlatan bir ifade kullan.
- Yatırım tavsiyesi verme; "al", "sat", "fondan çık" gibi yönlendirmeler yok.
- Siyasi yorum yok; kararlarda geçen siyasi ya da örgütsel iddiaları aktarma.
- Avukatlık reklam yasağı ve anonimlik kuralları aynen geçerli.

Her gün (Europe/Istanbul):
- **3 zincir — 12:30, 18:30, 21:30.** Her biri bir mahkeme kararını anlatır (ilk tweet merak uyandıran 1–2 cümle + "Yargıtay ne dedi? 🧵" ya da "İstinaf ne dedi? 🧵" + boş satır + 2 hashtag; altına `descendants` ile 2–3 tweet: olay, alt mahkeme kararları, üst mahkemenin gerekçesi; son tweette künye). Videosuz, düz metin.
- **4–5 tek tweetlik not — 11:30, 14:30, 16:30, 20:00, 23:30.** Kanun maddesi açıklaması, kısa karar notu ya da SPK'nın resmi açıklaması/bülteni hakkında tarafsız bilgi. Biçim: kısa metin + (dayanak) + alt satırda 2 hashtag.
- **Pazar 20:30: haftalık bülten zinciri** — haftanın SPK/fon/manipülasyon paylaşımlarından en önemli 5'i.
- Aynı kararı ikinci kez paylaşma; X'te paylaşılan kararların künyelerini `paylasilanlar-x.md` dosyasına yaz (yoksa oluştur) ve önce oradan kontrol et.

Biçim kuralları:
- Her tweet en fazla 280 karakter (emoji 2 sayılır), hashtagler dahil; göndermeden önce Python ile say.
- Bağlantı (URL) koyma.
- Hashtag: zincirlerin yalnızca ilk tweetinde ve notlarda tam 2 hashtag — #SPK + konuya özgü 1 (#manipülasyon, #fon, #borsa gibi). Zincirdeki diğer tweetlerde hashtag yok.
- Metricool çağrısı: `providers [{"network":"twitter"}]`, `twitterData {"tags":[]}`, zincir için `descendants: [{"text": "...", "media": [], "mediaAltText": []}, ...]`.

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
