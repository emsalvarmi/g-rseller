# ترکیه بدون تله (Tuzaksız Türkiye) — Farsça Instagram sayfası

Bu klasör `@torkiye_bedoone_tale` Instagram hesabının üretim araçlarını ve kayıtlarını tutar. Deponun geri kalanı (`sablon/`, kökteki `2026/`, `paylasilanlar*.md`, `medya` dalı) **@emsalvarmi** hesabına aittir: oraya dokunmayın, oradaki kuralları bu sayfaya uygulamayın.

- Metricool markası: **FARSİ**, `blogId` **8198062**, saat dilimi `Europe/Istanbul`, ağ: yalnızca Instagram.
- Kitle: Türkiye'de yaşayan ya da gelmeyi düşünen İranlılar ve Farsça konuşanlar.
- Amaç: dolandırılmadan ve sorun yaşamadan önce uyarmak; sayfa bir başvuru kaynağı olsun, çok takipçi kazansın.
- Sayfa anonimdir: hiçbir içerikte avukat, ofis, kişi adı, telefon, "bize yazın" çağrısı ya da hizmet tanıtımı yer almaz. İçerik yalnızca bilgilendirir.

## Dil

- **Video anlatıcısı ve sohbet balonları:** Tahran konuşma dili (محاوره‌ای): «می‌گه», «خونه», «رو», «توی», «یه».
- **Post görselleri ve açıklama metinleri:** yazı dili (resmî ama sade Farsça).
- Türkçe terimler Farsça yazımla korunur ve gerekirse Latin harfle de gösterilir: تاپو (tapu), ایسکان (iskân), کاپورا (kapora), نوتر (noter).
- Vakalar isimsiz ve kurgusaldır; videoda "گفت‌وگو بازسازی‌شده است · نام‌ها واقعی نیستند" notu bulunur. Gerçek kişi, firma, proje adı yok.

## Hukuki doğruluk

- Yalnızca genel ve yerleşik kurallar anlatılır. Tutar, süre, oran, harç gibi rakamlar ve "yeni kanun" haberleri **web'de resmî kaynaktan doğrulanmadan yazılmaz**; doğrulanınca kaynak içerikte belirtilir (ör. Resmî Gazete tarih ve sayı).
- Emin olunmayan konu atlanır, yerine sıradaki konu alınır. Garanti, kesin sonuç ya da bireysel tavsiye dili kullanılmaz.
- Siyasi yorum, İran ya da Türkiye hükümetleri hakkında değerlendirme, bir milleti ya da meslek grubunu toptan suçlayan dil yok ("bazı emlakçılar", "satıcı" denir).

## Video (Reels) — sohbet formatı

```
bash farsi/setup.sh                                  # oturum başına bir kez
python3 farsi/video/ph.py <spec.json>                # okunuş kontrolü (aşağıya bakın)
python3 farsi/video/make_video.py <spec.json> <çıktı-klasörü>
```

Çıktı: `reel.mp4` (1080×1920, sesli), `kapak.jpg`, kontrol kareleri (`kare_uyari.jpg`, `kare_ozet.jpg`, `kare_kapanis.jpg`). Yayından önce kontrol karelerine **bakın** (taşma, kesilme, boş alan) ve `ffprobe` ile ses akışını doğrulayın. Hedef süre 50–65 sn (rahat okunur ve dinlenir, ama oyalanmaz); 65 sn'yi geçerse bir mesaj ya da bir özet maddesi çıkarın.

Örnek spec'ler: `farsi/2026/2026-11-19-sahte-tercuman/spec.json`, `farsi/2026/2026-11-19-elden-odeme/spec.json`. Alanlar:

- `contact`: sohbetteki karşı taraf (`name`, `initial`, `grad` iki renk).
- `intro`: `tag` (ör. «پرونده کلاهبرداری · ۴»), `h1` (2–3 kısa satır, vurgulanan kelime `<span>` içinde), `note`, `voice` (en fazla ~5 sn).
- `events` sırayla: `in` (karşı taraf yazar), `out` (alıcı yazar; `unread: true` tek tik), `flag` (bir önceki `in` mesajını işaretler: `k` etiket, `h` kısa başlık, `p` bir cümle, `voice`), `skip` (zaman atlaması: `big`, `small`), `status` (karşı taraf "son görülme: çok önce" olur).
- `lesson`: `title`, isteğe bağlı `title_voice`, 3–5 `items` (`html`, `voice`, sonuncuda `warn: true` olabilir), isteğe bağlı `src` (kaynak satırı).
- `end`: `h1`, `cta`, `voice`.

Kalıp: kanca → 2–3 mesaj → 1. tehlike işareti → 1–2 mesaj → 2. tehlike işareti → kırılma (zaman atlaması ya da alıcının akıllı cevabı) → özet → kapanış. Mesajlar kısa (en fazla iki satır). Zamanlama seslendirme sürelerinden otomatik hesaplanır.

### Okunuş kontrolü (zorunlu)

Ses motoru (çevrimdışı Farsça ses) kısa ünlüleri tahmin eder ve işaretlenmezse yanlış okur. `voice` alanlarını yazdıktan sonra `ph.py` çıktısındaki IPA'yı **her kelime için** okuyun ve yanlışları harekeyle düzeltin. `voice` metni yalnızca seslendirilir, ekranda görünmez; ekrandaki metinlere hareke koymayın.

| Durum | Yazım | Örnek |
| --- | --- | --- |
| Tamlama eki (-e) | kelime sonuna kesre | وضعیتِ سند، قراردادِ دفترِ املاک، بدونِ تله |
| ه / ی ile biten kelimede tamlama | ٔ | ادارهٔ تاپو، نشونهٔ اول، ترکیهٔ بدونِ تله |
| ا / و ile biten kelimede tamlama | یِ | جایِ تو |
| «رو» (belirtme) | رُ ya da önceki kelimeye ُ | برگه‌ای رُ، سندُ، مترجمُ |
| می‌شه، می‌گه، می‌کنه | bitişik: میشه، میگه، میکنه | حساب میشه |
| می‌شن | می‌شَن | شامل می‌شَن |
| «تو» (içinde) | توی | توی ترکیه |
| «به‌هت/بهتون» | بِهِت، بِهِتون | |
| «و» (bağlaç, konuşma dili) | önceki kelimeye ُ | صدُ پنجاه، همسرُ بچه‌ها |
| Sayılar | yazıyla | صدُ پنجاه هزار دلار |
| Sık yanlışlar | | گفتگو (گفت‌وگو değil)، میان‌بُر، پِشیمون، خونَش، بِدی، شُمارَش، طبق (kesresiz) |

Marka cümlesi her zaman: «ترکیهٔ بدونِ تله». Kapanış sesi: «قبل از امضا، بپرس. ترکیهٔ بدونِ تله. یه دقیقه ببین، یه عمر پِشیمون نشو.» (haber videolarında son cümle yerine takip çağrısı olabilir).

## Post görselleri

```
python3 farsi/post/make_post.py <spec.json> <çıktı-klasörü>     # 01.png, 02.png … (1080×1350)
```

Spec: `{"slides": ["<gövde html>", …]}`. Logo ve alt satır otomatik eklenir. Sınıflar `farsi/post/post.css` içinde; örnekler `farsi/ornek/`: `post-kelime.json` (Günün Kelimesi, tek görsel), `post-liste.json` (Kontrol Listesi, 3 görsel), `post-dogru-yanlis.json` (Doğru mu Yanlış mı, 2 görsel). "Nereye Gidilir" postu liste örneğinden türetilir. Üretilen her PNG'ye bakın; "UYARI: içerik taşıyor" çıkarsa metni kısaltın.

## Yükleme ve planlama

1. `farsi/medya.sh <klasör>...` dosyaları `medya-farsi` dalına yükler ve her dosya için bağlantı + HTTP kodu yazdırır (hepsi 200 olmalı).
2. Metricool `createScheduledPost`, `blogId` 8198062, `providers [{"network":"instagram"}]`, `autoPublish true`, `draft false`:
   - Video: `instagramData {"type":"REEL","showReelOnFeed":true,"isAiGenerated":true}`, `media [reel.mp4]`, `videoThumbnailUrl kapak.jpg`.
   - Post: `instagramData {"type":"POST","showReelOnFeed":true,"isAiGenerated":false}`, `media` sırayla PNG'ler.
3. Açıklama metni (yazı dili): ilk satır aranacak kelimeleri içeren soru ya da kanca; 2–3 kısa paragraf; videolarda "این گفت‌وگو بازسازی یک سناریوی رایج است و نام‌ها واقعی نیستند." satırı; bir çağrı (kaydet / gönder / yorum yaz). **En fazla 5 etiket** (Instagram sınırı): konuya uygun dört etiket + `#ترکیه_بدون_تله`. Sık kullanılanlar: `#ایرانیان_ترکیه #اقامت_ترکیه #مهاجرت_به_ترکیه #خرید_ملک_در_ترکیه #زندگی_در_ترکیه #تاپو #کلاهبرداری_ملکی #سرمایه_گذاری_در_ترکیه #شهروندی_ترکیه`.
4. Metricool hata verirse metni değiştirip zorlamayın; hatayı kullanıcıya bildirin.

## Kayıt

- Her içeriğin spec dosyası `farsi/2026/<YYYY-MM-DD>-<konu-ascii>/` klasöründe saklanır (video: `spec.json`; postlar: `post-1.json`, `post-2.json` …). mp4/png dosyaları `main` dalına **konmaz**.
- `farsi/paylasilanlar.md`: her içerik için bir satır. Aynı konu, kelime ya da soru tekrar edilmez.
- `farsi/plan.md`: günlük ritim ve konu kuyruğu.
- Commit yazarı `Claude <noreply@anthropic.com>`; kullanıcının e-postası hiçbir yerde kullanılmaz.
