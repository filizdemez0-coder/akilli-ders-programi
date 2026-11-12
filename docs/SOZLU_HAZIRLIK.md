# Vize Sözlü Sınavı Hazırlık Notları (Hafta 8)

> Bu notlar ezber için değil, kendi kodunu anlatabilmen için. Her cevabı VS Code'da ilgili dosyayı açarak,
> kendi cümlelerinle anlatmaya çalış. Anlatamadığın satır kalırsa önce onu çalıştırıp dene.

---

## 1) Şu ana kadarki mimarini özetle

Üç katmanlı bir Flask uygulaması (şema: `docs/mimari.png`):

| Katman | Dosya | Görevi |
|---|---|---|
| **Sunum** | `backend/app.py` (rotalar), `backend/sayfalar.py` (HTML/CSS şablonları) | İsteği alır, oturum/rol kontrolü yapar, sayfayı Jinja ile oluşturur |
| **İş kuralları** | `backend/app.py` içindeki K1–K6 kuralları, `backend/cakisma.py` | AKTS sınırı, aynı ders kuralı, sahiplik, çakışma algoritması |
| **Veri** | `backend/db_manager.py` (bağlantı), `backend/sema.py` (şema güncelleme), `init_db.py`, `database/proje.db` | SQLite'a tek yerden bağlanır, yabancı anahtar denetimi açık |

Bir isteğin yolculuğu (öğrenci "+ Ekle"ye basar):
`POST /program/ekle/<sube_id>` → `giris_gerekli` (oturum var mı?) → `program_ekle()` → şube var mı (K1) → aynı ders var mı (K2)
→ AKTS (K3) → `cakisma.yeni_oturum_cakismalari()` (K4) → `ProgramDersleri` tablosuna INSERT → `/dersler` sayfasına yönlendirme.

Canlıda: Render → gunicorn (`Procfile`) → Flask. Port, gizli anahtar ve veritabanı yolu ortam değişkenlerinden okunur.

## 2) Hangi modül hangi veriyi nereden alıyor?

| Modül | Okuduğu / yazdığı tablolar | Nereden |
|---|---|---|
| Kullanıcı (kayıt/giriş) | `Kullanici` | `app.py` → `db_baglantisi()` → `db_manager.baglanti_al()` |
| Öğrenci kaydı | `Ogrenci` (`KullaniciId` ile hesaba bağlı, 1–1) | `ogrenci_id_bul()` — yoksa otomatik oluşturur |
| Ders kataloğu | `Ders` + `Sube` (JOIN) | `SUBE_SORGUSU` |
| Program oluşturucu | `Program` (öğrenci başına 1), `ProgramDersleri` (köprü, N–N) | `program_getir_veya_olustur()`, `program_dersleri()` |
| Çakışma tespiti | Veritabanına **hiç** dokunmaz; `sube_oturum()` ile sözlüğe çevrilmiş şubeleri alır | `cakisma.py` (saf fonksiyonlar) |
| Paylaşım | `Program.PaylasimKodu`, `Program.Kaydedildi` | `/paylas/<kod>` |
| Yönetici katalog | `Ders`, `Sube` (ekle/sil), silmeden önce `ProgramDersleri`'ni kontrol eder | `/yonetici/katalog` |

Çakışma modülünün veritabanından bağımsız olması bilinçli: aynı fonksiyonlar hem uygulamada hem `tests/test_cakisma.py`'de kullanılıyor.

## 3) En çok zorlandığın entegrasyon neydi, nasıl çözdün?

*(Kendi deneyiminle anlat. Bu projede yaşanan gerçek örnekler:)*

- **Kullanici ↔ Ogrenci ilişkisi:** Program tablosu `Ogrenci`'ye bağlıydı ama kod oraya giriş hesabının (`Kullanici`) kimliğini
  yazıyordu. SQLite yabancı anahtarları varsayılan olarak denetlemediği için hata görünmüyordu; denetim açılınca
  `FOREIGN KEY constraint failed` çıktı. Çözüm: `Ogrenci.KullaniciId` sütunu (1–1 ilişki) ve hesabın öğrenci kaydı yoksa otomatik oluşturma.
- **Mevcut veriyi bozmadan şema değiştirmek:** Çakışma için `Sube.BitisSaati` gerekiyordu ama veritabanında kayıtlar vardı.
  `sema.py` eksik sütunları `ALTER TABLE` ile ekliyor, eski kayıtlara varsayılan bitiş saati veriyor; birden çok kez çalışması zararsız.
- **Hafta 8'de testlerin yakaladığı bağlantı sızıntısı:** `with sqlite3.connect(...)` bağlantıyı kapatmıyormuş (yalnızca commit ediyor).
  Entegrasyon testleri `ResourceWarning` verdi; bağlantılar açıkça kapatıldı.

## 4) Yapay zekâdan aldığın bir kod parçasını satır satır açıkla

### a) İki dersin kaç dakika çakıştığı — `cakisma.py`

```python
def ortusme_dakikasi(a, b):
    if a["Gun"] != b["Gun"]:                                      # 1
        return 0
    a1, a2 = dakikaya_cevir(a["Baslangic"]), dakikaya_cevir(a["Bitis"])   # 2
    b1, b2 = dakikaya_cevir(b["Baslangic"]), dakikaya_cevir(b["Bitis"])
    return max(0, min(a2, b2) - max(a1, b1))                     # 3
```

1. Farklı günlerdeki dersler asla çakışmaz → 0 dakika.
2. "09:30" gibi saatleri günün başından itibaren dakikaya çeviriyoruz (09:30 → 570). Böylece saatleri sayı gibi karşılaştırabiliyoruz.
3. Ortak aralığın **başlangıcı** iki başlangıçtan büyük olanı (`max(a1, b1)`), **bitişi** iki bitişten küçük olanıdır (`min(a2, b2)`).
   Bitiş − başlangıç ortak süredir. Aralıklar hiç kesişmiyorsa sonuç negatif çıkar; `max(0, …)` bunu 0 yapar.
   - Örnek: BIL101 09:00–11:00 (540–660), MAT101 10:00–12:00 (600–720) → min(660,720) − max(540,600) = 660 − 600 = **60 dk**.
   - Arka arkaya dersler: 09:00–11:00 ve 11:00–12:00 → 660 − 660 = 0 → **çakışmaz** (bitiş saati hariç tutulur).

Çakışma türü (`cakisma_turu`): aralıklar aynıysa **tam**, biri diğerini içine alıyorsa **kapsama**, yalnız bir kısmı örtüşüyorsa **kısmi**.

### b) Programdaki tüm çakışmaları bulmak — `program_cakismalari`

```python
sirali = sorted(oturumlar, key=lambda o: (GUNLER.index(o["Gun"]), dakikaya_cevir(o["Baslangic"])))  # 1
for i, a in enumerate(sirali):                                   # 2
    a_bitis = dakikaya_cevir(a["Bitis"])
    for b in sirali[i + 1:]:                                     # 3
        if b["Gun"] != a["Gun"] or dakikaya_cevir(b["Baslangic"]) >= a_bitis:
            break                                                # 4
        sonuc.append(_cakisma_kaydi(a, b))                       # 5
```

1. Dersler önce güne (Pazartesi=0 …), sonra başlangıç saatine göre sıralanır.
2. Her ders (`a`) sırayla ele alınır.
3. Yalnızca kendisinden **sonra** gelen derslerle karşılaştırılır; böylece her çift bir kez sayılır.
4. Sıralı olduğu için: `b` başka bir güne geçtiyse ya da `a` bittikten sonra başlıyorsa, ondan sonrakiler de çakışamaz → döngüden çık.
   Bu yönteme **sweep-line** (tarama çizgisi) denir; her dersi her dersle karşılaştırmaktan daha az iş yapar.
5. Çakışan çift; türü, ortak aralığı ve dakikasıyla listeye eklenir.

## 5) Bir sonraki aşamanın planı nedir?

- **Hafta 9 — Takvim entegrasyonu:** Kaydedilmiş programı takvime aktarmak. Önce standart `.ics` (iCalendar) dosyası olarak
  dışa aktarma (her ders haftalık tekrar eden etkinlik), ardından takvim API'si; API anahtarı ortam değişkeninde saklanacak,
  hata ve zaman aşımı yönetimi yapılacak.
- Seçmeli ders öneri modülü (`Tercih` tablosu hazır).
- Her yeni modülde entegrasyon testlerini genişletmek; her ara sürümü etiketlemek (`v0.9.0` …).

---

### Hızlı tekrar: teorik kavramlar
- **Entegrasyon:** Ayrı yazılmış modüllerin birlikte doğru çalışması. Bu projede: giriş → katalog → program → çakışma → kaydet → paylaş.
- **Sürümleme (SemVer):** `MAJOR.MINOR.PATCH`. Bu ara sürüm `0.8.0`; yalnızca hata düzeltirsem `0.8.1`, yeni modül eklersem `0.9.0`.
- **Regresyon:** Yeni bir değişikliğin eskiden çalışan bir özelliği bozması. `python -m unittest discover tests` her değişiklikten sonra çalıştırılarak yakalanır.
