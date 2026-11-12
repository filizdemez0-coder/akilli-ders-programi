"""
Veri erişim katmanı (Hafta 4, Hafta 8'de birleştirildi)
--------------------------------------------------------
Uygulamadaki TÜM veritabanı bağlantıları buradan açılır:
  - Veritabanı yolu tek yerde belirlenir (VERITABANI_YOLU ortam değişkeni ya da database/proje.db).
  - Her bağlantıda yabancı anahtar (FOREIGN KEY) denetimi açılır.
Hafta 8 düzeltmesi: Önceden yol "database/proje.db" olarak göreliydi; betik proje kökü dışından
çalıştırılınca "unable to open database file" hatası veriyordu.
"""
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("VERITABANI_YOLU") or os.path.normpath(
    os.path.join(BASE_DIR, "..", "database", "proje.db"))


def baglanti_al():
    baglanti = sqlite3.connect(DB_PATH)
    baglanti.row_factory = sqlite3.Row
    baglanti.execute("PRAGMA foreign_keys = ON")   # ilişkisel bütünlük kontrolleri açık
    return baglanti


# 1. READ (Dersleri Listele)
def tum_dersleri_getir():
    conn = baglanti_al()
    dersler = conn.execute("SELECT * FROM Ders ORDER BY DersKodu").fetchall()
    conn.close()
    return [dict(d) for d in dersler]


# 2. CREATE (Yeni Ders Ekle)
def ders_ekle(kod, ad, kredi, akts):
    conn = baglanti_al()
    conn.execute("INSERT INTO Ders (DersKodu, DersAdi, Kredi, AKTS) VALUES (?, ?, ?, ?)", (kod, ad, kredi, akts))
    conn.commit()
    conn.close()


# 3. DELETE (Ders Sil)
def ders_sil(ders_id):
    conn = baglanti_al()
    conn.execute("DELETE FROM Ders WHERE Id = ?", (ders_id,))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    print("--- Veritabanindaki Dersler ---")
    for d in tum_dersleri_getir():
        print(f"[{d['DersKodu']}] {d['DersAdi']} (Kredi: {d['Kredi']})")
