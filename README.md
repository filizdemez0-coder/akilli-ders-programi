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
