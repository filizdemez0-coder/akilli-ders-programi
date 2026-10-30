"""
Şema güncellemeleri (migration) - Hafta 6 ve Hafta 7
----------------------------------------------------
Mevcut veritabanındaki verileri SİLMEDEN eksik sütunları ekler.
Uygulama her açıldığında çalışır; ikinci kez çalışması zararsızdır (idempotent).

Hafta 6: Ogrenci.KullaniciId (hesap ↔ öğrenci ilişkisi),
         Program.Kaydedildi, Program.PaylasimKodu   -> Kaydet / Paylaş akışı
Hafta 7: Sube.BitisSaati                             -> Zaman aralığı modeli
         (Sube.Saat sütunu artık BAŞLANGIÇ saati olarak kullanılır)
"""


def _sutunlar(conn, tablo):
    return {r[1] for r in conn.execute(f"PRAGMA table_info({tablo})")}


def _iki_saat_sonra(saat):
    ss, dd = saat.split(":")
    return f"{min(int(ss) + 2, 22):02d}:{dd}"


def sema_guncelle(conn):
    sube = _sutunlar(conn, "Sube")
    if "BitisSaati" not in sube:
        conn.execute("ALTER TABLE Sube ADD COLUMN BitisSaati TEXT")
    # Eski kayıtlarda bitiş saati yoksa varsayılan olarak 2 saatlik ders kabul et
    for sid, saat in conn.execute(
        "SELECT Id, Saat FROM Sube WHERE BitisSaati IS NULL OR BitisSaati = ''"
    ).fetchall():
        conn.execute("UPDATE Sube SET BitisSaati = ? WHERE Id = ?", (_iki_saat_sonra(saat), sid))

    # Hafta 6: Giriş hesabı (Kullanici) ile öğrenci kaydını (Ogrenci) ilişkilendir
    if "KullaniciId" not in _sutunlar(conn, "Ogrenci"):
        conn.execute("ALTER TABLE Ogrenci ADD COLUMN KullaniciId INTEGER REFERENCES Kullanici(Id)")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_ogrenci_kullanici ON Ogrenci(KullaniciId)")

    program = _sutunlar(conn, "Program")
    if "Kaydedildi" not in program:
        conn.execute("ALTER TABLE Program ADD COLUMN Kaydedildi INTEGER NOT NULL DEFAULT 0")
    if "PaylasimKodu" not in program:
        conn.execute("ALTER TABLE Program ADD COLUMN PaylasimKodu TEXT")

    # Aynı şube bir programa iki kez eklenemesin (veritabanı seviyesinde güvence)
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_programdersleri ON ProgramDersleri(ProgramId, SubeId)"
    )
    conn.commit()


# Çakışma senaryolarını gösterebilmek için örnek ders/şube verileri.
# (DersKodu, DersAdi, Kredi, AKTS, [(Hoca, Gun, Baslangic, Bitis), ...])
ORNEK_DERSLER = [
    ("BIL101", "Programlama Temelleri", 3, 5, [("Dr. Ali Veli", "Pazartesi", "09:00", "11:00"),
                                             ("Dr. Ali Veli", "Çarşamba", "13:00", "15:00")]),
    ("MAT101", "Genel Matematik", 4, 6, [("Doç. Ayşe Kara", "Salı", "13:00", "15:00"),
                                         ("Doç. Ayşe Kara", "Pazartesi", "10:00", "12:00")]),
    ("FIZ101", "Fizik I", 3, 5, [("Dr. Mehmet Demir", "Salı", "14:00", "16:00"),
                                 ("Dr. Mehmet Demir", "Perşembe", "09:00", "11:00")]),
    ("BIL103", "Bilgisayar Uygulamaları I", 2, 4, [("Öğr. Gör. Zeynep Ak", "Pazartesi", "09:00", "11:00"),
                                                  ("Öğr. Gör. Zeynep Ak", "Cuma", "10:00", "12:00")]),
    ("ING101", "Temel İngilizce", 2, 3, [("Okt. Can Yıldız", "Pazartesi", "11:00", "12:00")]),
]


def ornek_veri_ekle(conn):
    """Eksik örnek dersleri/şubeleri ekler; var olanlara dokunmaz."""
    for kod, ad, kredi, akts, subeler in ORNEK_DERSLER:
        satir = conn.execute("SELECT Id FROM Ders WHERE DersKodu = ?", (kod,)).fetchone()
        if satir:
            ders_id = satir[0]
        else:
            ders_id = conn.execute(
                "INSERT INTO Ders (DersKodu, DersAdi, Kredi, AKTS) VALUES (?, ?, ?, ?)",
                (kod, ad, kredi, akts),
            ).lastrowid
        for hoca, gun, bas, bit in subeler:
            var = conn.execute(
                "SELECT 1 FROM Sube WHERE DersId=? AND Gun=? AND Saat=?", (ders_id, gun, bas)
            ).fetchone()
            if not var:
                conn.execute(
                    "INSERT INTO Sube (DersId, HocaAdi, Gun, Saat, BitisSaati) VALUES (?, ?, ?, ?, ?)",
                    (ders_id, hoca, gun, bas, bit),
                )
    conn.commit()
