"""
Şema güncellemeleri (migration) - Hafta 6 ve Hafta 7
----------------------------------------------------
Mevcut veritabanındaki verileri SİLMEDEN eksik sütunları ekler.
Uygulama her açıldığında çalışır; ikinci kez çalışması zararsızdır (idempotent).

Hafta 6: Ogrenci.KullaniciId (hesap ↔ öğrenci ilişkisi),
         Program.Kaydedildi, Program.PaylasimKodu   -> Kaydet / Paylaş akışı
Hafta 7: Sube.BitisSaati                             -> Zaman aralığı modeli
         (Sube.Saat sütunu artık BAŞLANGIÇ saati olarak kullanılır)
Hafta 10: Ders.Secmeli, Ders.Alan                    -> Seçmeli ders önerisi
          Ogrenci.IlgiAlanlari, AlanBasarisi tablosu -> Öğrencinin tercih/başarı verisi
          AiGunlugu tablosu                          -> Yapay zekâ istem/çıktı günlüğü
          Ayar tablosu (OrnekVeriSurumu)             -> Örnek veriler yalnızca bir kez eklenir
"""

# Seçmeli ders önerisinde kullanılan ilgi alanları (sabit liste: öğrenci serbest metin girmez)
ALANLAR = ["Yazılım", "Veri ve Yapay Zekâ", "Ağ ve Güvenlik", "Web ve Mobil", "İşletme ve Girişimcilik"]


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

    # Hafta 10: Seçmeli ders önerisi için ders türü ve ilgi alanı
    ders = _sutunlar(conn, "Ders")
    if "Secmeli" not in ders:
        conn.execute("ALTER TABLE Ders ADD COLUMN Secmeli INTEGER NOT NULL DEFAULT 0")
    if "Alan" not in ders:
        conn.execute("ALTER TABLE Ders ADD COLUMN Alan TEXT")
    if "IlgiAlanlari" not in _sutunlar(conn, "Ogrenci"):
        conn.execute("ALTER TABLE Ogrenci ADD COLUMN IlgiAlanlari TEXT NOT NULL DEFAULT ''")
    # Başarı verisi: öğrencinin her alandaki not ortalaması (4'lük sistem)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS AlanBasarisi (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            OgrenciId INTEGER NOT NULL REFERENCES Ogrenci(Id),
            Alan TEXT NOT NULL,
            Ortalama REAL NOT NULL CHECK (Ortalama BETWEEN 0 AND 4),
            UNIQUE (OgrenciId, Alan)
        )""")
    # Yapay zekâ günlüğü: her istem, ham yanıt ve doğrulama sonucu saklanır (şeffaflık)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS AiGunlugu (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Zaman TEXT NOT NULL DEFAULT (datetime('now')),
            KullaniciId INTEGER REFERENCES Kullanici(Id),
            Model TEXT,
            Istem TEXT NOT NULL,
            Yanit TEXT,
            Durum TEXT NOT NULL,
            Aciklama TEXT
        )""")
    conn.execute("CREATE TABLE IF NOT EXISTS Ayar (Anahtar TEXT PRIMARY KEY, Deger TEXT NOT NULL)")
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


# Hafta 10: seçmeli dersler (bazı şubeleri bilerek zorunlu derslerle çakışır; öneri bunları elemelidir)
SECMELI_DERSLER = [
    ("SEC301", "Python ile Veri Analizi", 3, 4, [("Dr. Elif Şahin", "Çarşamba", "09:00", "11:00"),
                                               ("Dr. Elif Şahin", "Perşembe", "13:00", "15:00")]),
    ("SEC302", "Web Programlama", 3, 4, [("Öğr. Gör. Burak Aydın", "Salı", "09:00", "11:00"),
                                         ("Öğr. Gör. Burak Aydın", "Cuma", "13:00", "15:00")]),
    ("SEC303", "Siber Güvenliğe Giriş", 2, 3, [("Dr. Kemal Öz", "Pazartesi", "13:00", "15:00")]),
    ("SEC304", "Mobil Uygulama Geliştirme", 3, 4, [("Öğr. Gör. Selin Koç", "Perşembe", "09:00", "11:00")]),
    ("SEC305", "Yapay Zekâya Giriş", 3, 5, [("Doç. Murat Ekinci", "Cuma", "10:00", "12:00"),
                                            ("Doç. Murat Ekinci", "Çarşamba", "13:00", "15:00")]),
    ("SEC306", "Girişimcilik", 2, 3, [("Dr. Ayten Polat", "Çarşamba", "15:00", "17:00")]),
    ("SEC307", "Ağ Temelleri", 3, 4, [("Dr. Kemal Öz", "Salı", "15:00", "17:00")]),
]
SECMELI_ALANLARI = {"SEC301": "Veri ve Yapay Zekâ", "SEC302": "Web ve Mobil", "SEC303": "Ağ ve Güvenlik",
                    "SEC304": "Web ve Mobil", "SEC305": "Veri ve Yapay Zekâ", "SEC306": "İşletme ve Girişimcilik",
                    "SEC307": "Ağ ve Güvenlik"}
ZORUNLU_ALANLARI = {"BIL101": "Yazılım", "BIL103": "Yazılım"}

# Örnek veri paketleri: (sürüm, dersler). Her paket veritabanına yalnızca BİR KEZ eklenir.
# Hafta 10 düzeltmesi: önceden örnek veriler her açılışta tamamlandığı için yöneticinin
# sildiği örnek dersler uygulama yeniden başlayınca geri geliyordu.
ORNEK_PAKETLER = [(1, ORNEK_DERSLER), (2, SECMELI_DERSLER)]


def _dersleri_ekle(conn, dersler, secmeli=False):
    for kod, ad, kredi, akts, subeler in dersler:
        satir = conn.execute("SELECT Id FROM Ders WHERE DersKodu = ?", (kod,)).fetchone()
        if satir:
            ders_id = satir[0]
        else:
            ders_id = conn.execute(
                "INSERT INTO Ders (DersKodu, DersAdi, Kredi, AKTS, Secmeli, Alan) VALUES (?, ?, ?, ?, ?, ?)",
                (kod, ad, kredi, akts, int(secmeli), SECMELI_ALANLARI.get(kod) or ZORUNLU_ALANLARI.get(kod)),
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


def ornek_veri_ekle(conn):
    """Henüz eklenmemiş örnek veri paketlerini ekler (Ayar.OrnekVeriSurumu ile izlenir)."""
    satir = conn.execute("SELECT Deger FROM Ayar WHERE Anahtar = 'OrnekVeriSurumu'").fetchone()
    surum = int(satir[0]) if satir else 0
    for paket_surumu, dersler in ORNEK_PAKETLER:
        if paket_surumu > surum:
            _dersleri_ekle(conn, dersler, secmeli=(paket_surumu == 2))
            surum = paket_surumu
    # Eski veritabanlarındaki zorunlu derslerin alanını tamamla (yalnızca boşsa)
    for kod, alan in ZORUNLU_ALANLARI.items():
        conn.execute("UPDATE Ders SET Alan = ? WHERE DersKodu = ? AND Alan IS NULL", (alan, kod))
    conn.execute("INSERT OR REPLACE INTO Ayar (Anahtar, Deger) VALUES ('OrnekVeriSurumu', ?)", (str(surum),))
    conn.commit()
