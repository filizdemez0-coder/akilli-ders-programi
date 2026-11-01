# Akıllı Ders Programı ve Seçmeli Ders Öneri Sistemi

## Projenin Amacı
Üniversite öğrencilerinin ders programı oluşturmasını,
ders çakışmalarını tespit etmesini ve ilgi alanlarına
göre seçmeli ders önerileri almasını sağlamak.

## Hedef Kullanıcı
Üniversite öğrencileri.

## Teknolojiler
- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript

## Temel Modüller
- Ders kataloğu
- Program oluşturucu
- Ders çakışma tespiti
- Seçmeli ders önerisi
- Kullanıcı yönetimi
## Hafta 3-4: Mimari ve Veri Modeli
- Mimari şema: `docs/mimari.png` (sunum / iş / veri katmanları)
- ER diyagramı: `database/er_diyagrami.png` (kaynağı `docs/er.mmd`, Hafta 6-7 sütunlarıyla güncel)
- `.gitignore`: `.venv`, `__pycache__`, `.env` depoya yüklenmez

## Hafta 5: Kullanıcı Yönetimi, Kimlik Doğrulama ve Güvenlik Notu
- **Parola Güvenliği:** Kullanıcı parolaları veritabanında kesinlikle düz metin (plain text) olarak saklanmamaktadır. `werkzeug.security` kütüphanesi ile PBKDF2/SHA256 algoritması kullanılarak salt eklenip güvenli şekilde hash'lenmiştir.
- **Oturum Yönetimi:** Giriş yapan kullanıcıların kimlik ve rol bilgileri Flask `session` yapısı ile yönetilmektedir. Kullanıcı çıkış yaptığında oturum tamamen sonlandırılır. Oturum 30 dakika sonra kendiliğinden düşer; girişte eski oturum temizlenir (session fixation koruması).
- **Rol Tabanlı Yetkilendirme (RBAC):** Sistemde `ogrenci` ve `yonetici` rolleri tanımlanmıştır. Yönetici gerektiren uç noktalara yetkisiz kullanıcılar erişmek istediğinde HTTP 403 Forbidden engeli uygulanmaktadır.

## Hafta 6: Ders Kataloğu ve Program Oluşturucu
**Veri modeli:** `Ders 1─N Sube` · `Kullanici 1─1 Ogrenci` (`Ogrenci.KullaniciId`) · `Ogrenci 1─1 Program` · `Program N─N Sube` (`ProgramDersleri` köprü tablosu, `UNIQUE(ProgramId, SubeId)`).

**Akış:** Giriş → `/dersler` (katalog + haftalık program) → `+ Programa Ekle` → `💾 Programı Kaydet` → paylaşım bağlantısı `/paylas/<kod>` (salt okunur).
Yönetici `/yonetici/katalog` sayfasından ders ve şube ekler/siler.

**İş kuralları ve doğrulama:**
| Kod | Kural |
|---|---|
| K1 | Olmayan şube eklenemez (404) |
| K2 | Aynı dersin iki şubesi aynı programda olamaz |
| K3 | Dönemlik AKTS üst sınırı: 30 |
| K4 | Saat çakışmasında uyarı verilir (Hafta 7) |
| K5 | Sahiplik: öğrenci yalnızca kendi programındaki kaydı silebilir (aksi hâlde 403) |
| K6 | Çakışma içeren veya boş program kaydedilemez |
| Katalog | Ders kodu 3-10 harf/rakam, Kredi 1-10, AKTS 1-15; programda kullanılan şube, şubesi olan ders silinemez |

Tüm değiştiren işlemler POST ile yapılır; HTML Jinja ile otomatik kaçışlanır (XSS'e karşı).

## Hafta 7: Çakışma Tespiti + Entegrasyon
**Model:** Her şube bir zaman aralığıdır: `(Gun, Saat=başlangıç, BitisSaati)`. Bitiş hariçtir: 09:00-11:00 ile 11:00-12:00 çakışmaz.

**Algoritma** (`backend/cakisma.py`): Aynı gündeki A ve B, `A.bas < B.bit` **ve** `B.bas < A.bit` ise çakışır.
Programın tamamı için oturumlar (gün, başlangıç) sırasına dizilir; her oturum yalnızca kendisi bitmeden başlayan sonraki oturumlarla karşılaştırılır (sweep-line).

**Kısmi çakışma:** Çakışmalar üç türe ayrılır: *tam* (aynı aralık), *kapsama* (biri diğerini içerir), *kısmi* (yalnızca bir kısmı örtüşür). Her biri için ortak aralık ve dakika gösterilir.

**Entegrasyon:** Katalogda çakışacak şubeler önceden işaretlenir → eklemede uyarı ekranı (öğrenci isterse "Yine de ekle") → programda çakışan dersler kırmızı → çakışma varken kayıt engellenir → yönetici aynı hocaya aynı saatte iki şube açamaz.

**Testler:** `python -m unittest discover tests`

**Çalıştırma:** `python init_db.py` (isteğe bağlı) → `python backend/app.py`. Eski veritabanı açılışta otomatik güncellenir (`backend/sema.py`), veriler silinmez.

## Hafta 7 (devam): Canlı Dağıtım (Cloud Deployment)
**Platform:** Render (ücretsiz plan). Canlı adres: **https://akilli-ders-programi.onrender.com**

| Dosya | Görevi |
|---|---|
| `requirements.txt` | Bulutta kurulacak paketler (Flask, Werkzeug, gunicorn) — sürümler sabitlendi |
| `Procfile` | Başlatma komutu: `gunicorn --chdir backend app:app --bind 0.0.0.0:$PORT` |
| `render.yaml` | Render servis tanımı (build/start komutu, sağlık kontrolü, ortam değişkenleri) |
| `.python-version` | Python sürümü (3.12) |

**Ortam değişkenleri:**
| Değişken | Açıklama |
|---|---|
| `PORT` | Platform verir; uygulama bu portu dinler (sabit 5000 kullanmak canlıda uygulamanın açılmamasına yol açar) |
| `GIZLI_ANAHTAR` | Oturum çerezlerini imzalar; koda yazılmaz, Render rastgele üretir |
| `CANLI_ORTAM=1` | Debug kapalı, çerez yalnızca HTTPS (`Secure`), vekil sunucu başlıkları (`ProxyFix`) etkin |
| `VERITABANI_YOLU` | (İsteğe bağlı) SQLite dosyasının yolu. Dosya yoksa tablolar ve örnek veriler otomatik oluşturulur |

**Neden gunicorn?** `app.run()` yalnızca geliştirme sunucusudur; tek istekte takılabilir ve güvenli değildir. Canlıda üretim WSGI sunucusu gunicorn kullanılır. SQLite tek dosya olduğu için 1 işçi (worker) + 4 iş parçacığı (thread) seçildi; böylece şema güncellemesi aynı anda iki süreçte çalışmaz.

**Veritabanı:** Uygulama açılışta `sema.py` ile şemayı günceller. Render'ın ücretsiz planında disk kalıcı değildir: her yeniden dağıtımda veritabanı depodaki `database/proje.db` hâline döner (test hesapları ve örnek dersler korunur, sonradan eklenen kayıtlar silinir). Kalıcı veri gerekirse ücretli disk veya PostgreSQL kullanılmalıdır.

**Sağlık kontrolü:** `/saglik` → `{"durum": "ok", "ders_sayisi": N}`

**Test hesapları (canlıda da geçerli):** Öğrenci `ogrenci / 123456` · Yönetici `admin / admin123`
