# Kısa İlerleme Raporu

**Proje:** P18 — Akıllı Ders Programı ve Seçmeli Ders Öneri Sistemi · **Canlı:** https://akilli-ders-programi.onrender.com

## Hafta 8 — Vize ara sürümü (`v0.8.0`, 12.11.2026)

| Modül | Durum | Kanıt |
|---|---|---|
| Kullanıcı yönetimi (kayıt, giriş, roller, kilit) | ✅ Çalışıyor | `test_kayit_giris_cikis`, `test_hatali_giris_kilidi`, `test_rol_kontrolu` |
| Veritabanı + veri erişim katmanı | ✅ Tek bağlantı noktası (`db_manager.py`), FK denetimi açık | `test_saglik_ve_bos_veritabani` |
| Ders kataloğu + program oluşturucu (K1–K6) | ✅ | `test_uctan_uca_program_akisi`, `test_sahiplik_kontrolu` |
| Çakışma tespiti | ✅ tam / kapsayan / kısmi | `tests/test_cakisma.py` (8 test) |
| Canlı dağıtım | ✅ Render + gunicorn | `/saglik` |
| Seçmeli ders önerisi | ⏳ Hafta 10'a planlandı | — |

**Uçtan uca akış:** giriş → katalog → ekleme → çakışma uyarısı → kaydetme engeli → düzeltme → kaydet → paylaş.
**Test:** 15/15 geçti (8 birim + 7 entegrasyon). **Etiket:** `v0.8.0`.

**En çok zorlanılan entegrasyon:** `Kullanici` ile `Ogrenci` arasındaki ilişki; FK denetimi açılınca ortaya çıktı ve
`Ogrenci.KullaniciId` (1–1) ile çözüldü. Ayrıntı: `docs/SOZLU_HAZIRLIK.md` §3.

**Bilinen eksikler (vize sonrası):** seçmeli ders önerisi, takvim entegrasyonu, CSRF belirteci, örnek verilerin her açılışta geri gelmesi.

## Hafta 9–10 (`v0.9.0`, `v0.10.0`, 20.11.2026)

| Hafta | Modül | Durum |
|---|---|---|
| 9 | Takvim: `.ics` dışa aktarma, abonelik bağlantısı, Calendarific resmî tatil API'si | ✅ Kod + 10 test. API anahtarı Render'a girilince tatiller etkinleşir |
| 10 | Seçmeli ders önerisi: ön eleme, Gemini API (ücretsiz), çıktı doğrulama, kural tabanlı yedek, AI günlüğü | ✅ Kod + 14 test. API anahtarı girilmezse kural tabanlı yedek çalışır |

**Düzeltilen bilinen hatalar:** örnek verilerin geri gelmesi, canlıda varsayılan gizli anahtar, eski `frontend/init_db.py`.
**Test:** 40/40 geçti.

**Sonraki adım (Hafta 11):** alternatif programları karşılaştırma modülü; CSRF belirteci; `/cikis`'in POST'a çevrilmesi.
