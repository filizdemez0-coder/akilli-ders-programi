# Demo Senaryosu — Vize (Hafta 8), yaklaşık 5 dakika

**Canlı adres:** https://akilli-ders-programi.onrender.com · **Sürüm:** 0.8.0 (`v0.8.0` etiketi)

> Hazırlık: Demodan 2–3 dakika önce linki bir kez açın (Render ücretsiz planda uyuyan sunucu ~50 sn'de uyanır).
> Yedek: İnternet sorunu olursa `python backend\app.py` ile yerelde http://127.0.0.1:5000 açılır.

| # | Adım | Ne gösterilir / ne söylenir | Modül |
|---|---|---|---|
| 1 | `/saglik` adresini aç | `{"durum":"ok","surum":"0.8.0"}` → uygulama canlıda, sürüm etiketli | Dağıtım |
| 2 | Ana sayfa → **Kayıt ol** ile yeni bir öğrenci aç (ör. `demo1`) | Parola hash'lenerek saklanır; kullanıcı adı boşluksuz olmalı | Kullanıcı (H5) |
| 3 | Yanlış şifreyle 1 kez dene, sonra doğru şifreyle gir | "Hatalı kullanıcı adı veya şifre" (hangi alanın yanlış olduğu söylenmez); 5 hatada kilit | Kullanıcı (H5, H8) |
| 4 | **Ders Programım** → katalogdan **BIL101 Pazartesi 09:00–11:00** ekle | Haftalık ızgarada blok görünür; AKTS artar | Katalog + Program (H6) |
| 5 | Katalogda MAT101 Pazartesi satırına bak | "⚠ BIL101 ile çakışır" etiketi — eklemeden önce uyarı | Çakışma (H7) |
| 6 | **MAT101 Pazartesi 10:00–12:00** → + Ekle | Uyarı ekranı: *Kısmi çakışma, 10:00–11:00, 60 dk* | Çakışma (H7) |
| 7 | **Yine de ekle** → **Programı kaydet** | Izgarada iki ders yan yana kırmızı; kaydet düğmesi pasif, "çakışma var" | Entegrasyon (H6+H7) |
| 8 | MAT101'i **Kaldır** → **FIZ101 Salı** ekle → **Kaydet** | "Program kaydedildi", paylaşım bağlantısı oluşur | Program (H6) |
| 9 | Paylaşım bağlantısını gizli pencerede aç | Giriş yapmadan salt okunur program | Paylaş (H6) |
| 10 | Çıkış → `admin / admin123` ile gir → **Katalog Yönetimi** | Dr. Ali Veli'ye Pazartesi 10:00–12:00 yeni şube açmayı dene → "bu saatte BIL101 dersinde" | Yönetici + Çakışma |
| 11 | (İsteğe bağlı) Terminalde `python -m unittest discover tests -v` | 15 test geçer: 8 birim + 7 entegrasyon | Test (H8) |

**Kapanış cümlesi:** "Kullanıcı yönetimi, veritabanı, ders kataloğu, program oluşturucu ve çakışma tespiti uçtan uca
birlikte çalışıyor; bu durum `v0.8.0` etiketiyle işaretlendi. Sonraki aşama Hafta 9: programı takvim servisine aktarma."

---

# Ek: Hafta 9–10 demo adımları (yaklaşık 3 dakika) · sürüm 0.10.0

| # | Adım | Ne gösterilir / ne söylenir | Modül |
|---|---|---|---|
| 1 | Öğrenciyle gir → **Seçmeli Önerisi** → "Veri ve Yapay Zekâ" ile "Web ve Mobil"i işaretle, Veri alanına BA (3.50) ver → **Profili kaydet** | Tercih/başarı verisi | Öneri (H10) |
| 2 | **✨ Öneri al** | Öneriler, şube, ★ uyum puanı, gerekçe; rozet: "Yapay zekâ önerisi · kodla doğrulandı" (üstte "Yapay zekâ: Gemini") (anahtar yoksa "Kural tabanlı") | Öneri (H10) |
| 3 | Bir öneride **+ Programa ekle** → Ders Programım | Önerilen şube programla çakışmıyor (ön eleme) | Öneri + Çakışma |
| 4 | `admin` ile **AI Günlüğü** | İstem (JSON), ham yanıt, durum (`basarili` / `kismen_gecersiz` / `anahtar_yok`) | Şeffaflık (H10) |
| 5 | Öğrenciyle **Takvim** → **.ics dosyasını indir** → Google Takvim'de içe aktar | Dersler dönem boyunca haftalık tekrar ediyor | Takvim (H9) |
| 6 | Takvim sayfasındaki **Resmî tatiller** kartı | 29 Ekim gibi tatiller; derse denk gelenler takvimden çıkarıldı. API çalışmazsa sarı uyarı ve takvim yine iniyor | Harici API (H9) |

> Canlıda AI ve tatil API'si için Render → Environment'a `GEMINI_API_KEY` (ücretsiz) ve `TATIL_API_ANAHTARI` girilmeli.
> Anahtarsız demo da çalışır: bu durumda hata yönetimi (yedek yol) gösterilmiş olur.
