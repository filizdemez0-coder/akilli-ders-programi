# Sürüm Notları (CHANGELOG)

Bu proje **anlamsal sürümleme** (Semantic Versioning, `MAJOR.MINOR.PATCH`) kullanır:

- **MAJOR** (1.x.x): geriye uyumsuz büyük değişiklik. Proje henüz geliştirme aşamasında olduğu için `0`.
- **MINOR** (x.8.x): yeni özellik / modül eklendiğinde artar. Ders haftasıyla eşleştirildi (Hafta 8 → `0.8`).
- **PATCH** (x.x.1): yalnızca hata düzeltmesi yapıldığında artar.

Ara sürümler Git etiketiyle (tag) işaretlenir: `git tag -a v0.8.0 -m "..."`.
Uygulamanın çalışan sürümü `/saglik` adresinde ve sayfa altında görünür.

---

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
