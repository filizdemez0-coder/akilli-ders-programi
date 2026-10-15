import sqlite3

def baglanti_al():
    baglanti = sqlite3.connect("database/proje.db")
    baglanti.row_factory = sqlite3.Row
    return baglanti

# 1. READ (Dersleri Listele)
def tum_dersleri_getir():
    conn = baglanti_al()
    dersler = conn.execute("SELECT * FROM Ders").fetchall()
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