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

## Hafta 8: Vize — Ara Sürüm (v0.8.0)
- **Sürüm:** `0.8.0`, Git etiketi `v0.8.0` (anlamsal sürümleme; ayrıntılar ve düzeltilen hatalar: `CHANGELOG.md`).
- **Entegrasyon:** Tüm veritabanı bağlantıları `backend/db_manager.py` üzerinden açılır.
- **Testler:** `python -m unittest discover tests -v` → 15 test (8 çakışma birim testi + 7 uçtan uca entegrasyon testi). Entegrasyon testleri geçici, boş bir veritabanı kullanır; `proje.db` değişmez.
- **Güvenlik düzeltmeleri:** 5 hatalı girişte 5 dakika kilit (HTTP 429), kullanıcı adında boşluk temizliği, girişli kullanıcının giriş/kayıt sayfasından panele yönlendirilmesi.
- **Demo:** `docs/DEMO_SENARYOSU.md` · **Sözlü hazırlık:** `docs/SOZLU_HAZIRLIK.md`

## Hafta 9: Harici API Entegrasyonu — Takvim (v0.9.0)
**Modül:** `backend/takvim.py` · **Sayfa:** `/takvim`

| Parça | Açıklama |
|---|---|
| Dışa aktarma | Program iCalendar (`.ics`, RFC 5545) olarak indirilir: `/takvim/program.ics`. Her şube dönem boyunca haftalık tekrar eden etkinliktir (`RRULE:FREQ=WEEKLY;UNTIL=...`). Google Takvim / Outlook / Apple Takvim içe aktarır. |
| Abonelik | Kaydedilmiş program için `/paylas/<kod>/takvim.ics`. Google Takvim → *Diğer takvimler → URL ile* eklenirse takvim servisi programı kendisi güncel tutar. |
| Harici API | **Calendarific** resmî tatil API'si (REST, anahtarla kimlik doğrulama). Dönemdeki resmî tatiller çekilir, derse denk gelen günler takvimden çıkarılır (`EXDATE`). |
| Anahtar | Kodda/depoda **yok**: `TATIL_API_ANAHTARI` ortam değişkeni (Render panelinde *Environment*). Ücretsiz anahtar: calendarific.com |
| Hata yönetimi | Zaman aşımı 5 sn; 401/403 (anahtar), 429 (hız sınırı), bağlantı hatası, bozuk JSON ayrı ayrı yakalanır. API çalışmazsa takvim **yine oluşturulur** (tatiller çıkarılmadan) ve sayfada uyarı gösterilir. Hata mesajlarında URL (dolayısıyla anahtar) yer almaz. |
| Hız sınırı | Tatiller yıl bazında 24 saat önbellekte tutulur; hata sonrası 5 dk, 429'da `Retry-After` süresi kadar API'ye gidilmez. |

Kurallar: boş veya çakışmalı program takvime aktarılamaz (K6 ile tutarlı).

## Hafta 10: Yapay Zekâ Bileşeni — Seçmeli Ders Önerisi (v0.10.0)
**Modül:** `backend/oneri.py` · **Sayfa:** `/oneri` · **Günlük:** `/yonetici/ai-gunlugu`

**Veri:** Öğrenci profilinde ilgi alanlarını (sabit liste) ve her alandaki not ortalamasını (4'lük sistem) girer
(`Ogrenci.IlgiAlanlari`, `AlanBasarisi` tablosu). Dersler `Ders.Secmeli` ve `Ders.Alan` ile etiketlenir.

**Akış:**
1. **Kural tabanlı ön eleme** — programda olmayan, AKTS sınırına sığan ve en az bir şubesi programla çakışmayan seçmeli dersler aday olur. Model bu listenin dışına çıkamaz.
2. **İstem** — ilgi alanları, alan ortalamaları, günlük ders yükü (dakika) ve aday listesi JSON olarak; kurallar sistem isteminde (`oneri.SISTEM_ISTEMI`).
3. **Model** — Claude API (`claude-opus-5-5`), yanıt JSON şemasına uygun üretilir (*structured outputs*). Anahtar: `ANTHROPIC_API_KEY` ortam değişkeni.
4. **Çıktı doğrulama** — ders gerçekten aday mı, şube o derse ait mi, önerilenler birbiriyle çakışıyor mu, AKTS sınırı, boş gerekçe, en fazla 3 öneri, puan 1–5. Geçmeyen öneri gösterilmez, nedeni günlüğe yazılır.
5. **Yedek** — anahtar yoksa, API hata verirse, JSON bozuksa ya da hiçbir öneri doğrulamayı geçmezse kural tabanlı öneri (ilgi + başarı − gün yükü puanı) devreye girer. Ekranda sonucun hangi yöntemle üretildiği yazar.

**Yoğunluk dengesi:** Bir dersin birden çok şubesi varsa mevcut ders yükü daha az olan gün tercih edilir; sayfada günlük yük çubukları gösterilir.
**Günlük (şeffaflık):** Her istekte istem, ham yanıt, durum (`basarili`, `kismen_gecersiz`, `gecersiz`, `hata`, `anahtar_yok`) ve açıklama `AiGunlugu` tablosuna yazılır; yönetici `/yonetici/ai-gunlugu` sayfasından inceler.
**Maliyet / hız sınırı:** Aynı öğrenci 15 saniyede bir öneri isteyebilir; istemci zaman aşımı 25 sn, 1 yeniden deneme.

**Testler:** `python -m unittest discover tests -v` → 36 test (çakışma 8, takvim 9, öneri 8, entegrasyon 11). Testler gerçek API'lere gitmez; yanıtlar taklit edilir.
**Belgeler:** `docs/AI_KULLANIM_GUNLUGU.md`, `docs/ILERLEME_RAPORU.md`, `docs/SOZLU_HAZIRLIK_H9_H10.md`
