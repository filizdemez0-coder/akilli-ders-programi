"""Hafta 7 - Çakışma Tespiti birim testleri.
Çalıştırmak için proje klasöründe:  python -m unittest discover tests
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from cakisma import (cakisiyor_mu, cakisma_turu, ortusme_dakikasi, program_cakismalari,
                     yeni_oturum_cakismalari, zaman_araligi_dogrula, dakikaya_cevir)


def o(kod, gun, bas, bit):
    return {"SubeId": kod, "DersKodu": kod, "DersAdi": kod, "Gun": gun, "Baslangic": bas, "Bitis": bit}


class CakismaTestleri(unittest.TestCase):
    def test_farkli_gun_cakismaz(self):
        self.assertFalse(cakisiyor_mu(o("A", "Pazartesi", "09:00", "11:00"), o("B", "Salı", "09:00", "11:00")))

    def test_ardisik_dersler_cakismaz(self):
        # 09:00-10:50 biter, 10:50 başlayan ders çakışmaz (bitiş hariç)
        self.assertFalse(cakisiyor_mu(o("A", "Cuma", "09:00", "10:50"), o("B", "Cuma", "10:50", "12:00")))

    def test_tam_cakisma(self):
        a, b = o("A", "Pazartesi", "09:00", "11:00"), o("B", "Pazartesi", "09:00", "11:00")
        self.assertEqual(cakisma_turu(a, b), "tam")
        self.assertEqual(ortusme_dakikasi(a, b), 120)

    def test_kismi_cakisma(self):
        a, b = o("A", "Pazartesi", "09:00", "11:00"), o("B", "Pazartesi", "10:00", "12:00")
        self.assertEqual(cakisma_turu(a, b), "kismi")
        self.assertEqual(ortusme_dakikasi(a, b), 60)

    def test_kapsama(self):
        a, b = o("A", "Salı", "09:00", "13:00"), o("B", "Salı", "10:00", "11:00")
        self.assertEqual(cakisma_turu(a, b), "kapsama")
        self.assertEqual(cakisma_turu(b, a), "kapsama")

    def test_program_tum_ciftleri_bulur(self):
        program = [
            o("BIL101", "Pazartesi", "09:00", "11:00"),
            o("MAT101", "Pazartesi", "10:00", "12:00"),
            o("ING101", "Pazartesi", "11:00", "12:00"),   # yalnız MAT101 ile çakışır
            o("FIZ101", "Salı", "14:00", "16:00"),
        ]
        ciftler = {(c["a"]["DersKodu"], c["b"]["DersKodu"]) for c in program_cakismalari(program)}
        self.assertEqual(ciftler, {("BIL101", "MAT101"), ("MAT101", "ING101")})

    def test_yeni_oturum(self):
        mevcut = [o("BIL101", "Pazartesi", "09:00", "11:00")]
        self.assertEqual(len(yeni_oturum_cakismalari(o("X", "Pazartesi", "10:30", "11:30"), mevcut)), 1)
        self.assertEqual(yeni_oturum_cakismalari(o("Y", "Pazartesi", "11:00", "12:00"), mevcut), [])

    def test_dogrulama(self):
        self.assertEqual(zaman_araligi_dogrula("Pazartesi", "09:00", "11:00"), [])
        self.assertTrue(zaman_araligi_dogrula("Pazartesi", "11:00", "09:00"))   # ters aralık
        self.assertTrue(zaman_araligi_dogrula("Pazartesi", "07:00", "09:00"))   # çok erken
        self.assertTrue(zaman_araligi_dogrula("Funday", "09:00", "11:00"))      # geçersiz gün
        self.assertTrue(zaman_araligi_dogrula("Cuma", "9:00", "11:00"))         # biçim
        with self.assertRaises(ValueError):
            dakikaya_cevir("25:00")


if __name__ == "__main__":
    unittest.main()
