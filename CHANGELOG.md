# Sürüm Notları (CHANGELOG)

Bu proje **anlamsal sürümleme** (Semantic Versioning, `MAJOR.MINOR.PATCH`) kullanır:

- **MAJOR** (1.x.x): geriye uyumsuz büyük değişiklik. Proje henüz geliştirme aşamasında olduğu için `0`.
- **MINOR** (x.8.x): yeni özellik / modül eklendiğinde artar. Ders haftasıyla eşleştirildi (Hafta 8 → `0.8`).
- **PATCH** (x.x.1): yalnızca hata düzeltmesi yapıldığında artar.

Ara sürümler Git etiketiyle (tag) işaretlenir: `git tag -a v0.8.0 -m "..."`.
Uygulamanın çalışan sürümü `/saglik` adresinde ve sayfa altında görünür.

---

## [0.10.0] — 2026-11-20 · Yapay zekâ bileşeni: seçmeli ders önerisi (Git etiketi: `v0.10.0`, 0.9.0 ile birlikte yayımlandı)
### Eklenenler
- `backend/oneri.py`: kural tabanlı ön eleme → Claude API (`claude-opus-5-5`, JSON şeması ile yapılandırılmış çıktı)
  → kodla çıktı doğrulama → hata/geçersiz çıktıda kural tabanlı yedek öneri. Sayfa: `/oneri`.
- Öğrenci profili: ilgi alanları + alan not ortalamaları (`Ogrenci.IlgiAlanlari`, `AlanBasarisi` tablosu).
- `Ders.Secmeli`, `Ders.Alan` sütunları; yönetici ders eklerken tür ve alan seçer; katalogda "Seçmeli" etiketi.
- 7 örnek seçmeli ders (bazı şubeleri bilerek zorunlu derslerle çakışır).
- AI günlüğü (`AiGunlugu` tablosu, `/yonetici/ai-gunlugu`): istem, ham yanıt, doğrulama sonucu.
- Öğrenci başına 15 sn öneri sınırı; `ANTHROPIC_API_KEY` ortam değişkeni; `anthropic==2.6.0`.
- 8 birim + 3 entegrasyon testi (model yanıtı taklit edilir).

### Düzeltilen hatalar
- Örnek veriler her açılışta tamamlandığı için yöneticinin sildiği örnek dersler yeniden başlatmada geri geliyordu
  → örnek veri paketleri `Ayar.OrnekVeriSurumu` ile izleniyor, her paket yalnızca bir kez ekleniyor (regresyon testi eklendi).
- Canlıda `GIZLI_ANAHTAR` tanımlanmazsa uygulama depodaki bilinen anahtarla açılıyordu → `CANLI_ORTAM=1` iken anahtar yoksa açılışta rastgele güçlü bir anahtar üretiliyor.
- Kullanılmayan, eski şemalı `frontend/init_db.py` kopyası kaldırıldı (tek kurulum betiği: `init_db.py`).

## [0.9.0] — 2026-11-20 · Harici API entegrasyonu: takvim
- `backend/takvim.py`: programı iCalendar (`.ics`, RFC 5545) olarak dışa aktarma; haftalık tekrar (`RRULE`), saat dilimi,
  RFC kaçış ve 75 bayt satır katlama. Sayfa: `/takvim`, indirme: `/takvim/program.ics`.
- Kaydedilmiş program için takvim aboneliği: `/paylas/<kod>/takvim.ics` (Google Takvim "URL ile ekle").
- Calendarific resmî tatil API'si: derse denk gelen tatiller `EXDATE` ile çıkarılır. Anahtar `TATIL_API_ANAHTARI`
  ortam değişkeninde; 5 sn zaman aşımı; 401/403/429/bağlantı/bozuk JSON hataları ayrı ayrı yönetilir; 24 saat önbellek,
  429'da `Retry-After` kadar bekleme. API çalışmazsa takvim yine oluşturulur ve kullanıcı uyarılır.
- gunicorn zaman aşımı 60 → 90 sn (harici API çağrıları için pay). 9 birim + 1 entegrasyon testi.

## [0.8.0] — 2026-11-12 · Vize ara sürümü (Git etiketi: `v0.8.0`)

### Entegrasyon
- Tüm veritabanı bağlantıları tek veri erişim katmanından (`backend/db_manager.py`) açılıyor; veritabanı yolu tek yerde tanımlı.
- Uçtan uca entegrasyon testleri eklendi (`tests/test_entegrasyon.py`, 7 test): boş veritabanından açılış → kayıt/giriş →
  katalogdan ders ekleme → çakışma uyarısı → kaydetme engeli → çakışan dersi kaldırma → kaydet → paylaş;
  sahiplik (403), rol kontrolü (403), hatalı giriş kilidi (429), yönetici katalog kuralları. Toplam 15 test.
- Sürüm numarası uygulamaya eklendi (`SURUM`), `/saglik` yanıtında ve sayfa altında gösteriliyor.
- Demo senaryosu (`docs/DEMO_SENARYOSU.md`) ve sözlü sınav hazırlık notları (`docs/SOZLU_HAZIRLIK.md`) eklendi.

### Düzeltilen hatalar
- `db_manager.py` göreli yol (`database/proje.db`) kullandığı için proje kökü dışından çalıştırılınca
  `unable to open database file` hatası veriyordu → mutlak yol + `VERITABANI_YOLU` desteği.
- Hatalı giriş denemelerinde sınır yoktu (kaba kuvvet saldırısına açık) → aynı kullanıcı adı + IP için
  5 dakikada 5 hatalı denemede 5 dakika kilit (HTTP 429).
- Kayıtta kullanıcı adının başındaki/sonundaki boşluklar da kaydediliyordu ("  ayse  " olarak kayıt olan
  "ayse" ile giriş yapamıyordu) → boşluklar atılıyor, kullanıcı adında boşluğa izin verilmiyor, e-posta küçük harfe çevriliyor.
- Giriş yapmış kullanıcı `/giris` ve `/kayit` sayfalarını yeniden görebiliyordu → panele yönlendiriliyor.
- `with sqlite3.connect(...)` bağlantıyı kapatmadığı için uygulama açılışında ve her `/saglik` isteğinde
  bir bağlantı açık kalıyordu (testlerde `ResourceWarning`) → bağlantılar açıkça kapatılıyor.
- Panelde AKTS doluluk çubuğu sınırı aşan değerlerde taşabiliyordu → en fazla %100.

## [0.7.0] — 2026-11-01 · Çakışma tespiti + canlı dağıtım
- Zaman aralığı modeli (`Sube.BitisSaati`), çakışma algoritması (`backend/cakisma.py`), tam/kapsayan/kısmi çakışma,
  uyarı ekranı, çakışma varken kaydetme engeli, 8 birim testi.
- Render'a dağıtım: `requirements.txt`, `Procfile`, `render.yaml`, ortam değişkenleri, `/saglik`.
  Canlı adres: https://akilli-ders-programi.onrender.com
- Arayüz yenilendi (`backend/sayfalar.py`). Commit'ler: `b28897d`, `6b9bc13`.

## [0.6.0] — 2026-10-30 · Ders kataloğu ve program oluşturucu
- Katalog, program seçim akışı, iş kuralları K1–K6, sahiplik kontrolü, kaydet/paylaş, yönetici katalog yönetimi,
  şema güncelleme modülü (`sema.py`). Hafta 3–5 eksikleri (`.gitignore`, ER, mimari şema, oturum süresi). Commit: `b37ea6e`.

## [0.5.0] — 2026-10-22 · Kullanıcı yönetimi ve kimlik doğrulama
- Kayıt/giriş, parola hash, oturum, öğrenci/yönetici rolleri. Commit: `cd546b8`.

## [0.4.0] — 2026-10-16 · Veritabanı ve veri erişim katmanı
- Tablolar, ilişkiler, kısıtlar, sentetik veri, CRUD. Commit'ler: `e4b12c9`, `c765c17`.

## [0.3.0] — 2026-10-15 · Kurulum, mimari ve ER modeli
- Proje iskeleti, README, ER diyagramı.
