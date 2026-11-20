"""Hafta 8 - Uçtan uca entegrasyon (ve regresyon) testleri.

Kullanıcı + veritabanı + ders kataloğu + program oluşturucu + çakışma tespiti modüllerinin
birlikte çalıştığını, gerçek bir tarayıcı yerine Flask test istemcisiyle doğrular.
Her çalıştırmada BOŞ, geçici bir veritabanı kullanılır; proje.db'ye dokunulmaz.

Çalıştırma (proje klasöründe):  python -m unittest discover tests -v
"""
import os
import re
import sys
import tempfile
import unittest

# Uygulama içe aktarılmadan ÖNCE geçici veritabanı yolu verilir (ortam değişkeni)
_GECICI = tempfile.mkdtemp()
os.environ["VERITABANI_YOLU"] = os.path.join(_GECICI, "test.db")
# Testler gerçek harici API'lere gitmez: anahtarlar kaldırılır (takvim ve öneri yedek yola düşer)
os.environ.pop("TATIL_API_ANAHTARI", None)
os.environ.pop("GEMINI_API_KEY", None)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import app as uygulama  # noqa: E402  (ortam değişkeni ayarlandıktan sonra)


def metin(yanit):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", yanit.get_data(as_text=True)))


class EntegrasyonTestleri(unittest.TestCase):

    def setUp(self):
        uygulama._basarisiz_girisler.clear()
        self.c = uygulama.app.test_client()

    # ---- yardımcılar
    def giris(self, kadi, parola, istemci=None):
        return (istemci or self.c).post("/giris", data={"kullanici_adi": kadi, "parola": parola})

    def sube_id(self, kod, gun):
        with uygulama.app.app_context():
            conn = uygulama.db_baglantisi()
            return conn.execute(
                "SELECT Sube.Id FROM Sube JOIN Ders ON Ders.Id = Sube.DersId WHERE DersKodu = ? AND Gun = ?",
                (kod, gun)).fetchone()[0]

    def yeni_ogrenci(self, ad):
        r = self.c.post("/kayit", data={"kullanici_adi": ad, "eposta": f"{ad}@ornek.test", "parola": "gizli123"})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(self.giris(ad, "gizli123").status_code, 302)

    # ---- 1. Boş veritabanından açılış: tablolar + örnek veriler + sürüm
    def test_saglik_ve_bos_veritabani(self):
        veri = self.c.get("/saglik").get_json()
        self.assertEqual(veri["durum"], "ok")
        self.assertEqual(veri["surum"], uygulama.SURUM)
        self.assertGreaterEqual(veri["ders_sayisi"], 5)

    # ---- 2. Kimlik doğrulama modülü
    def test_kayit_giris_cikis(self):
        self.yeni_ogrenci("deniz")
        self.assertEqual(self.c.get("/panel").status_code, 200)
        self.c.get("/cikis")
        self.assertEqual(self.c.get("/panel").status_code, 302)   # çıkıştan sonra panel kapalı

    def test_hatali_giris_kilidi(self):
        for _ in range(uygulama.GIRIS_DENEME_SINIRI):
            self.assertEqual(self.giris("admin", "yanlis").status_code, 200)
        r = self.giris("admin", "admin123")                       # doğru parola bile kilitliyken reddedilir
        self.assertEqual(r.status_code, 429)

    def test_rol_kontrolu(self):
        self.yeni_ogrenci("ece")
        self.assertEqual(self.c.get("/yonetici/katalog").status_code, 403)

    # ---- 3. Katalog + program + çakışma: uçtan uca senaryo
    def test_uctan_uca_program_akisi(self):
        self.yeni_ogrenci("mert")
        bil_pzt = self.sube_id("BIL101", "Pazartesi")
        mat_pzt = self.sube_id("MAT101", "Pazartesi")
        fiz_sal = self.sube_id("FIZ101", "Salı")

        self.assertEqual(self.c.post(f"/program/ekle/{bil_pzt}").status_code, 302)
        self.assertEqual(self.c.post(f"/program/ekle/{fiz_sal}").status_code, 302)

        # Çakışan ders: uyarı ekranı gelir, eklenmez
        r = self.c.post(f"/program/ekle/{mat_pzt}")
        self.assertEqual(r.status_code, 200)
        self.assertIn("Kısmi çakışma", metin(r))
        self.assertIn("60 dk", metin(r))

        # Öğrenci onaylarsa taslağa eklenir, ama program kaydedilemez
        self.c.post(f"/program/ekle/{mat_pzt}", data={"zorla": "1"})
        r = self.c.post("/program/kaydet", follow_redirects=True)
        self.assertIn("çakışma var", metin(r))

        # Aynı dersin ikinci şubesi eklenemez (K2)
        r = self.c.post(f"/program/ekle/{self.sube_id('BIL101', 'Çarşamba')}", follow_redirects=True)
        self.assertIn("zaten programınızda", metin(r))

        # Çakışan dersi kaldır → kaydet → paylaş
        with uygulama.app.app_context():
            kayit = uygulama.db_baglantisi().execute(
                "SELECT Id FROM ProgramDersleri WHERE SubeId = ?", (mat_pzt,)).fetchone()[0]
        self.c.post(f"/program/sil/{kayit}")
        r = self.c.post("/program/kaydet", follow_redirects=True)
        self.assertIn("Program kaydedildi", metin(r))

        kod = re.search(r"/paylas/([\w-]+)", r.get_data(as_text=True)).group(1)
        anonim = uygulama.app.test_client()
        r = anonim.get(f"/paylas/{kod}")
        self.assertEqual(r.status_code, 200)
        self.assertIn("BIL101", metin(r))
        self.assertNotIn("MAT101", metin(r))

    # ---- 4. Sahiplik: başkasının program kaydı silinemez
    def test_sahiplik_kontrolu(self):
        self.yeni_ogrenci("selin")
        self.c.post(f"/program/ekle/{self.sube_id('ING101', 'Pazartesi')}")
        with uygulama.app.app_context():
            kayit = uygulama.db_baglantisi().execute("SELECT MAX(Id) FROM ProgramDersleri").fetchone()[0]
        diger = uygulama.app.test_client()
        diger.post("/kayit", data={"kullanici_adi": "kaan", "eposta": "kaan@ornek.test", "parola": "gizli123"})
        self.giris("kaan", "gizli123", diger)
        self.assertEqual(diger.post(f"/program/sil/{kayit}").status_code, 403)

    # ---- 5. Yönetici katalog yönetimi + iş kuralları
    def test_yonetici_katalog_kurallari(self):
        self.giris("admin", "admin123")
        r = self.c.post("/yonetici/katalog", follow_redirects=True, data={
            "islem": "sube_ekle", "ders_id": 1, "hoca": "Dr. Ali Veli",
            "gun": "Pazartesi", "bas": "10:00", "bit": "12:00"})
        self.assertIn("bu saatte", metin(r))                      # aynı hoca aynı saatte iki derste olamaz
        r = self.c.post("/yonetici/katalog", follow_redirects=True, data={
            "islem": "sube_ekle", "ders_id": 1, "hoca": "Dr. Test", "gun": "Cuma", "bas": "12:00", "bit": "10:00"})
        self.assertIn("önce olmalı", metin(r))                    # ters zaman aralığı
        r = self.c.post("/yonetici/katalog", follow_redirects=True, data={
            "islem": "ders_ekle", "kod": "BIL101", "ad": "Tekrar", "kredi": 3, "akts": 5})
        self.assertIn("zaten var", metin(r))                      # benzersiz ders kodu

    # ---- 6. Hafta 9: takvime aktarma (.ics) + abonelik bağlantısı
    def test_takvim_disa_aktarma(self):
        self.yeni_ogrenci("aylin")
        r = self.c.get("/takvim/program.ics", follow_redirects=True)
        self.assertIn("önce programınıza ders ekleyin", metin(r))
        self.c.post(f"/program/ekle/{self.sube_id('BIL101', 'Pazartesi')}")
        r = self.c.get("/takvim")
        self.assertEqual(r.status_code, 200)
        self.assertIn("Resmî tatiller alınamadı", metin(r))          # anahtar yok → uyarı, sayfa çalışır
        r = self.c.get("/takvim/program.ics")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.content_type.startswith("text/calendar"))
        self.assertIn("attachment", r.headers["Content-Disposition"])
        govde = r.get_data(as_text=True)
        self.assertIn("BEGIN:VEVENT", govde)
        self.assertIn("SUMMARY:BIL101 Programlama Temelleri", govde)
        # Kaydedilmiş program için herkese açık abonelik adresi
        self.assertEqual(self.c.get("/paylas/yok/takvim.ics").status_code, 404)
        r = self.c.post("/program/kaydet", follow_redirects=True)
        kod = re.search(r"/paylas/([\w-]+)", r.get_data(as_text=True)).group(1)
        self.assertIn("BIL101", uygulama.app.test_client().get(f"/paylas/{kod}/takvim.ics").get_data(as_text=True))

    # ---- 7. Hafta 10: seçmeli ders önerisi (API anahtarı yok → kural tabanlı yedek)
    def test_secmeli_oneri_akisi(self):
        self.yeni_ogrenci("baran")
        r = self.c.post("/oneri", data={"islem": "oneri"}, follow_redirects=True)
        self.assertIn("en az bir ilgi alanı", metin(r))
        self.c.post("/oneri", data={"islem": "profil", "ilgi": ["Veri ve Yapay Zekâ", "Uydurma Alan"], "ort1": "3.5"})
        uygulama._son_oneri_zamani.clear()
        r = self.c.post("/oneri", data={"islem": "oneri"})
        self.assertEqual(r.status_code, 200)
        self.assertIn("Kural tabanlı öneri", metin(r))
        self.assertIn("SEC301", metin(r))                               # ilgi alanındaki seçmeli ders
        r = self.c.post("/oneri", data={"islem": "oneri"}, follow_redirects=True)
        self.assertIn("saniye bekleyin", metin(r))                       # art arda istek sınırı
        with uygulama.app.app_context():
            conn = uygulama.db_baglantisi()
            kayit = conn.execute("SELECT Durum, Istem FROM AiGunlugu ORDER BY Id DESC").fetchone()
            ilgi = conn.execute("SELECT IlgiAlanlari FROM Ogrenci JOIN Kullanici ON Kullanici.Id = Ogrenci.KullaniciId "
                                "WHERE KullaniciAdi = 'baran'").fetchone()[0]
        self.assertEqual(kayit["Durum"], "anahtar_yok")
        self.assertIn("SEC301", kayit["Istem"])
        self.assertEqual(ilgi, "Veri ve Yapay Zekâ")                    # listede olmayan alan kaydedilmedi
        self.assertEqual(self.c.get("/yonetici/ai-gunlugu").status_code, 403)

    def test_yonetici_ai_gunlugu(self):
        self.giris("admin", "admin123")
        self.assertEqual(self.c.get("/yonetici/ai-gunlugu").status_code, 200)

    # ---- 8. Regresyon: yöneticinin sildiği örnek ders yeniden başlatmada geri gelmez
    def test_silinen_ornek_veri_geri_gelmez(self):
        self.giris("admin", "admin123")
        sid = self.sube_id("SEC306", "Çarşamba")
        self.c.post("/yonetici/katalog", data={"islem": "sube_sil", "id": sid})
        with uygulama.app.app_context():
            conn = uygulama.db_baglantisi()
            ders_id = conn.execute("SELECT Id FROM Ders WHERE DersKodu = 'SEC306'").fetchone()[0]
        self.c.post("/yonetici/katalog", data={"islem": "ders_sil", "id": ders_id})
        conn = uygulama.baglanti_al()
        uygulama.sema_guncelle(conn)                                     # uygulama yeniden açılıyormuş gibi
        uygulama.ornek_veri_ekle(conn)
        self.assertIsNone(conn.execute("SELECT 1 FROM Ders WHERE DersKodu = 'SEC306'").fetchone())
        conn.close()


if __name__ == "__main__":
    unittest.main()
