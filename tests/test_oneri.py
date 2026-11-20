"""Hafta 10 - Seçmeli ders öneri modülü birim testleri.
Gerçek yapay zekâ API'si çağrılmaz; model yanıtı sahte bir işlevle verilir (cagir=...)."""
import io
import json
import os
import sys
import unittest
import urllib.error
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import oneri  # noqa: E402


def sube(sid, ders_id, kod, alan, gun, bas, bit, akts=4):
    return {"SubeId": sid, "DersId": ders_id, "DersKodu": kod, "DersAdi": kod + " adı", "Alan": alan,
            "AKTS": akts, "Gun": gun, "Saat": bas, "BitisSaati": bit, "HocaAdi": "Hoca " + kod}


# Öğrencinin programı: Pazartesi 09-11 ve Salı 13-15
PROGRAM = [sube(1, 100, "BIL101", "Yazılım", "Pazartesi", "09:00", "11:00", 5),
           sube(2, 101, "MAT101", None, "Salı", "13:00", "15:00", 6)]
SECMELILER = [
    sube(10, 200, "SEC301", "Veri ve Yapay Zekâ", "Pazartesi", "10:00", "12:00"),   # programla çakışır
    sube(11, 200, "SEC301", "Veri ve Yapay Zekâ", "Çarşamba", "09:00", "11:00"),    # uygun
    sube(12, 201, "SEC302", "Web ve Mobil", "Salı", "09:00", "11:00"),
    sube(13, 201, "SEC302", "Web ve Mobil", "Cuma", "13:00", "15:00"),
    sube(14, 202, "SEC306", "İşletme ve Girişimcilik", "Çarşamba", "10:00", "12:00"),  # SEC301-Çarşamba ile çakışır
    sube(15, 203, "SEC999", "Ağ ve Güvenlik", "Perşembe", "09:00", "11:00", akts=20),  # AKTS'ye sığmaz
    sube(16, 100, "BIL101", "Yazılım", "Cuma", "09:00", "11:00"),                     # zaten alınmış ders
]
PROFIL = {"ilgi_alanlari": ["Veri ve Yapay Zekâ", "Web ve Mobil"], "basari": {"Veri ve Yapay Zekâ": 3.5}}
KALAN = 30 - 11


def yanit(*oneriler, genel="Genel not"):
    return lambda istem: json.dumps({"oneriler": list(oneriler), "genel_not": genel}, ensure_ascii=False)


class AdayTestleri(unittest.TestCase):

    def test_kural_tabanli_on_eleme(self):
        adaylar = {d["ders_kodu"]: d for d in oneri.adaylari_hazirla(SECMELILER, PROGRAM, KALAN)}
        self.assertEqual(set(adaylar), {"SEC301", "SEC302", "SEC306"})          # SEC999 (AKTS) ve BIL101 elendi
        self.assertEqual([s["sube_id"] for s in adaylar["SEC301"]["subeler"]], [11])  # çakışan şube elendi
        self.assertEqual(adaylar["SEC302"]["subeler"][0]["gun_yuku_dk"], 120)   # Salı'da 2 saat ders var

    def test_kural_tabanli_oneri_denge_ve_cakisma(self):
        adaylar = oneri.adaylari_hazirla(SECMELILER, PROGRAM, KALAN)
        sonuc = oneri.kural_tabanli_oneri(adaylar, PROFIL, KALAN)
        kodlar = [o["ders"]["ders_kodu"] for o in sonuc]
        self.assertEqual(kodlar[0], "SEC301")                                   # ilgi + yüksek ortalama
        self.assertNotIn("SEC306", kodlar)                                      # SEC301 ile aynı saatte
        sec302 = next(o for o in sonuc if o["ders"]["ders_kodu"] == "SEC302")
        self.assertEqual(sec302["sube"]["gun"], "Cuma")                         # dolu Salı yerine boş Cuma
        self.assertTrue(all(o["gerekce"] for o in sonuc))


class AiDogrulamaTestleri(unittest.TestCase):

    def setUp(self):
        self.gunluk = []

    def uret(self, cagir):
        return oneri.oneri_uret(SECMELILER, PROGRAM, PROFIL, KALAN, cagir=cagir,
                                gunluge_yaz=lambda **k: self.gunluk.append(k))

    def test_gecerli_ai_yaniti(self):
        s = self.uret(yanit({"ders_kodu": "SEC301", "sube_id": 11, "uyum_puani": 5, "gerekce": "İlgi ve başarı uyumlu."}))
        self.assertEqual(s["kaynak"], "ai")
        self.assertEqual(s["oneriler"][0]["sube"]["sube_id"], 11)
        self.assertEqual(self.gunluk[-1]["durum"], "basarili")
        self.assertIn("aday_dersler", self.gunluk[-1]["istem"])                # istem günlüğe yazıldı

    def test_uydurma_ve_hatali_oneriler_elenir(self):
        s = self.uret(yanit(
            {"ders_kodu": "SEC301", "sube_id": 11, "uyum_puani": 9, "gerekce": "Uygun."},
            {"ders_kodu": "UYDURMA1", "sube_id": 99, "uyum_puani": 5, "gerekce": "Yok böyle ders."},
            {"ders_kodu": "SEC301", "sube_id": 11, "uyum_puani": 4, "gerekce": "Tekrar."},
            {"ders_kodu": "SEC302", "sube_id": 10, "uyum_puani": 4, "gerekce": "Yanlış şube."},
            {"ders_kodu": "SEC306", "sube_id": 14, "uyum_puani": 3, "gerekce": "SEC301 ile çakışır."},
            {"ders_kodu": "SEC302", "sube_id": 13, "uyum_puani": 4, "gerekce": "  "},
        ))
        self.assertEqual(s["kaynak"], "ai")
        self.assertEqual([o["ders"]["ders_kodu"] for o in s["oneriler"]], ["SEC301"])
        self.assertEqual(s["oneriler"][0]["uyum_puani"], 5)                     # 9 → 5'e kırpıldı
        self.assertEqual(self.gunluk[-1]["durum"], "kismen_gecersiz")
        self.assertIn("aday listesinde olmayan", self.gunluk[-1]["aciklama"])

    def test_bozuk_json_kural_tabanliya_duser(self):
        s = self.uret(lambda istem: "bu JSON değil")
        self.assertEqual(s["kaynak"], "kural")
        self.assertTrue(s["oneriler"])
        self.assertIn("JSON", s["uyari"])
        self.assertEqual(self.gunluk[-1]["durum"], "gecersiz")

    def test_bos_oneri_listesi_kural_tabanliya_duser(self):
        s = self.uret(yanit())
        self.assertEqual(s["kaynak"], "kural")

    def test_api_hatasi_kural_tabanliya_duser(self):
        def hata(istem):
            raise oneri.OneriHatasi("Yapay zekâ API'si zamanında yanıt vermedi.")
        s = self.uret(hata)
        self.assertEqual(s["kaynak"], "kural")
        self.assertIn("zamanında", s["uyari"])
        self.assertIsNone(self.gunluk[-1]["yanit"])

    def test_aday_yoksa_api_cagrilmaz(self):
        cagrildi = []
        s = oneri.oneri_uret(SECMELILER, PROGRAM, PROFIL, 0, cagir=lambda i: cagrildi.append(i))
        self.assertEqual(s["oneriler"], [])
        self.assertEqual(cagrildi, [])


class GeminiCagriTestleri(unittest.TestCase):
    """gemini_cagir(): ağa çıkılmaz, _http_post taklit edilir."""

    def setUp(self):
        self.ortam = mock.patch.dict(os.environ, {"GEMINI_API_KEY": "test-anahtari"})
        self.ortam.start()
        self.addCleanup(self.ortam.stop)

    def test_basarili_yanit_ve_istek_bicimi(self):
        yanit = {"candidates": [{"finishReason": "STOP", "content": {"parts": [
            {"text": "düşünce", "thought": True}, {"text": '{"oneriler": [], "genel_not": "x"}'}]}}]}
        with mock.patch.object(oneri, "_http_post", return_value=yanit) as sahte:
            metin, model = oneri.gemini_cagir("istem")
        self.assertEqual(json.loads(metin)["genel_not"], "x")                 # düşünce parçası katılmadı
        self.assertEqual(model, oneri.MODELLER[0])
        url, govde, anahtar = sahte.call_args.args
        self.assertNotIn("test-anahtari", url)                               # anahtar URL'de değil
        self.assertEqual(anahtar, "test-anahtari")
        self.assertEqual(govde["generationConfig"]["responseMimeType"], "application/json")
        self.assertEqual(govde["generationConfig"]["responseJsonSchema"], oneri.YANIT_SEMASI)

    def _http_hatasi(self, kod, govde=b""):
        return urllib.error.HTTPError("https://x", kod, "hata", {}, io.BytesIO(govde))

    def test_http_hatalari(self):
        # Google'ın gerçek geçersiz anahtar yanıtı biçimi
        gecersiz = (b'{"error": {"code": 400, "message": "API key not valid.", "status": "INVALID_ARGUMENT",'
                    b' "details": [{"reason": "API_KEY_INVALID"}]}}')
        durumlar = [(lambda: self._http_hatasi(400, gecersiz), "anahtarı geçersiz"),
                    (lambda: self._http_hatasi(429), "istek sınırı"),
                    (lambda: self._http_hatasi(404), "modeli bulunamadı"),
                    (lambda: urllib.error.URLError(TimeoutError()), "bağlanılamadı")]
        for uret, beklenen in durumlar:
            hatalar = [uret(), uret()]
            for h in hatalar:
                if isinstance(h, urllib.error.HTTPError):
                    self.addCleanup(h.close)
            with mock.patch.object(oneri, "_http_post", side_effect=hatalar):
                with self.assertRaises(oneri.OneriHatasi) as ctx:
                    oneri.gemini_cagir("istem")
            self.assertIn(beklenen, str(ctx.exception))
            self.assertNotIn("test-anahtari", str(ctx.exception))

    def test_yogunlukta_ikinci_modele_gecilir(self):
        basarili = {"candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": "{}"}]}}]}
        hata = self._http_hatasi(503, b'{"error": {"status": "UNAVAILABLE", "message": "The model is overloaded."}}')
        with mock.patch.object(oneri, "_http_post", side_effect=[hata, basarili]) as sahte:
            _metin, model = oneri.gemini_cagir("istem")
        self.assertEqual(model, oneri.MODELLER[1])
        self.assertIn(oneri.MODELLER[1], sahte.call_args.args[0])
        # Anahtar hatası geçici değildir: ikinci model boşuna denenmez, Google'ın mesajı günlüğe gider
        hata = self._http_hatasi(400, b'{"error": {"status": "INVALID_ARGUMENT", "message": "API_KEY_INVALID"}}')
        with mock.patch.object(oneri, "_http_post", side_effect=[hata]) as sahte:
            with self.assertRaises(oneri.OneriHatasi) as ctx:
                oneri.gemini_cagir("istem")
        self.assertEqual(sahte.call_count, 1)
        self.assertIn("INVALID_ARGUMENT", ctx.exception.ayrinti)

    def test_engellenen_ve_yarim_kalan_yanit(self):
        for yanit, beklenen in [({"promptFeedback": {"blockReason": "SAFETY"}}, "SAFETY"),
                                ({"candidates": [{"finishReason": "MAX_TOKENS", "content": {"parts": []}}]}, "MAX_TOKENS")]:
            with mock.patch.object(oneri, "_http_post", return_value=yanit):
                with self.assertRaises(oneri.OneriHatasi) as ctx:
                    oneri.gemini_cagir("istem")
            self.assertIn(beklenen, str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
