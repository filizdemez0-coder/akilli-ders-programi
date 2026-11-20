"""Hafta 9 - Takvim modülü birim testleri (ağa çıkılmaz; API çağrısı taklit edilir)."""
import io
import os
import sys
import unittest
import urllib.error
from datetime import date
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import takvim  # noqa: E402

DERS = {"SubeId": 7, "DersKodu": "BIL101", "DersAdi": "Programlama Temelleri", "HocaAdi": "Dr. Ali Veli",
        "Gun": "Pazartesi", "Saat": "09:00", "BitisSaati": "11:00"}
ORNEK_YANIT = {"meta": {"code": 200}, "response": {"holidays": [
    {"name": "Republic Day", "date": {"iso": "2026-10-29"}, "type": ["National holiday"]},
    {"name": "New Year's Eve", "date": {"iso": "2026-12-31T00:00:00+03:00"}, "type": ["Observance"]},
    {"name": "Bozuk kayıt"},
]}}


class IcsTestleri(unittest.TestCase):

    def test_haftalik_tekrar_ve_ilk_gun(self):
        ics = takvim.ics_olustur([DERS], "Test")
        self.assertIn("DTSTART;TZID=Europe/Istanbul:20260921T090000", ics)   # 21.09.2026 Pazartesi
        self.assertIn("DTEND;TZID=Europe/Istanbul:20260921T110000", ics)
        self.assertIn("RRULE:FREQ=WEEKLY;UNTIL=20261231T205959Z", ics)       # yerel 23:59:59 = UTC 20:59:59
        self.assertTrue(ics.startswith("BEGIN:VCALENDAR\r\n") and ics.endswith("END:VCALENDAR\r\n"))

    def test_ilk_ders_gunu_hafta_ortasi(self):
        self.assertEqual(takvim.ilk_ders_gunu("Çarşamba"), date(2026, 9, 23))
        self.assertEqual(len(list(takvim.ders_tarihleri("Pazartesi"))), 15)

    def test_tatil_gunu_cikarilir(self):
        pazartesi_tatil = [(date(2026, 10, 5), "Örnek tatil")]
        ics = takvim.ics_olustur([DERS], "Test", pazartesi_tatil)
        self.assertIn("EXDATE;TZID=Europe/Istanbul:20261005T090000", ics)
        persembe_tatil = [(date(2026, 10, 29), "Cumhuriyet Bayramı")]          # Pazartesi dersini etkilemez
        self.assertNotIn("EXDATE", takvim.ics_olustur([DERS], "Test", persembe_tatil))

    def test_kacis_ve_satir_katlama(self):
        uzun = dict(DERS, DersAdi="Veri Yapıları, Algoritmalar; ve " + "çok uzun bir ders adı " * 5)
        ics = takvim.ics_olustur([uzun], "Test")
        self.assertIn("Veri Yapıları\\, Algoritmalar\\; ve", ics.replace("\r\n ", ""))
        for satir in ics.split("\r\n"):
            self.assertLessEqual(len(satir.encode("utf-8")), 75)


class TatilApiTestleri(unittest.TestCase):

    def setUp(self):
        takvim._onbellek.clear()

    def test_anahtar_yoksa_hata(self):
        with mock.patch.dict(os.environ, {"TATIL_API_ANAHTARI": ""}):
            with self.assertRaises(takvim.TatilApiHatasi):
                takvim.resmi_tatiller(2026)

    def test_yanit_ayristirilir_ve_onbellege_alinir(self):
        with mock.patch.dict(os.environ, {"TATIL_API_ANAHTARI": "test-anahtari"}), \
             mock.patch.object(takvim, "_http_get", return_value=ORNEK_YANIT) as sahte:
            tatiller = takvim.resmi_tatiller(2026)
            takvim.resmi_tatiller(2026)
        self.assertEqual(tatiller, [(date(2026, 10, 29), "Republic Day")])   # yalnızca ulusal tatil
        self.assertEqual(sahte.call_count, 1)                                   # ikinci çağrı önbellekten

    def test_hiz_siniri_429(self):
        hata = urllib.error.HTTPError("https://gizli", 429, "Too Many", {"Retry-After": "120"}, io.BytesIO())
        with mock.patch.dict(os.environ, {"TATIL_API_ANAHTARI": "test-anahtari"}), \
             mock.patch.object(takvim, "_http_get", side_effect=hata) as sahte:
            with self.assertRaises(takvim.TatilApiHatasi) as ctx:
                takvim.resmi_tatiller(2026)
            with self.assertRaises(takvim.TatilApiHatasi):
                takvim.resmi_tatiller(2026)
        self.assertIn("sınır", str(ctx.exception))
        self.assertNotIn("test-anahtari", str(ctx.exception))                # anahtar mesajda görünmez
        self.assertEqual(sahte.call_count, 1)                                   # bekleme süresince API'ye gidilmez

    def test_zaman_asimi_ve_bozuk_yanit(self):
        with mock.patch.dict(os.environ, {"TATIL_API_ANAHTARI": "k"}), \
             mock.patch.object(takvim, "_http_get", side_effect=urllib.error.URLError(TimeoutError())):
            with self.assertRaises(takvim.TatilApiHatasi) as ctx:
                takvim.resmi_tatiller(2026)
        self.assertIn("zaman aşımı", str(ctx.exception))
        with mock.patch.dict(os.environ, {"TATIL_API_ANAHTARI": "k"}), \
             mock.patch.object(takvim, "_http_get", return_value={"meta": {"code": 401}}):
            with self.assertRaises(takvim.TatilApiHatasi):
                takvim.resmi_tatiller(2027)

    def test_donem_tatilleri_hata_durumunda_bos_liste(self):
        with mock.patch.dict(os.environ, {"TATIL_API_ANAHTARI": ""}):
            tatiller, hata = takvim.donem_tatilleri()
        self.assertEqual(tatiller, [])
        self.assertTrue(hata)


if __name__ == "__main__":
    unittest.main()
