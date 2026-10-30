import sqlite3

def veritabanini_kur():
    # SQLite veritabanı dosyasını database klasöründe açar
    baglanti = sqlite3.connect("database/proje.db")
    imlec = baglanti.cursor()

    # 1. Ogrenci Tablosu
    imlec.execute("""
    CREATE TABLE IF NOT EXISTS Ogrenci (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Ad TEXT NOT NULL,
        Soyad TEXT NOT NULL,
        OgrenciNo TEXT UNIQUE NOT NULL
    )
    """)

    # 2. Ders Tablosu
    imlec.execute("""
    CREATE TABLE IF NOT EXISTS Ders (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        DersKodu TEXT UNIQUE NOT NULL,
        DersAdi TEXT NOT NULL,
        Kredi INTEGER NOT NULL,
        AKTS INTEGER NOT NULL
    )
    """)
    # 3. Sube Tablosu (Ders saatleri ve günleri için)
    imlec.execute("""
    CREATE TABLE IF NOT EXISTS Sube (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        DersId INTEGER NOT NULL,
        SubeKodu TEXT NOT NULL,
        Gun TEXT NOT NULL,
        BaslangicSaati TEXT NOT NULL,
        BitisSaati TEXT NOT NULL,
        OgretimElemani TEXT,
        FOREIGN KEY (DersId) REFERENCES Ders(Id)
    )
   """)
    # 3. Sube Tablosu (1-N İliki: Bir dersin birden çok şubesi olur)
    imlec.execute("""
    CREATE TABLE IF NOT EXISTS Sube (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        DersId INTEGER NOT NULL,
        HocaAdi TEXT NOT NULL,
        Gun TEXT NOT NULL,
        Saat TEXT NOT NULL,
        FOREIGN KEY (DersId) REFERENCES Ders(Id)
    )
    """)

    # 4. Program Tablosu
    imlec.execute("""
    CREATE TABLE IF NOT EXISTS Program (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        OgrenciId INTEGER NOT NULL,
        Donem TEXT NOT NULL,
        FOREIGN KEY (OgrenciId) REFERENCES Ogrenci(Id)
    )
    """)

    # 5. ProgramDersleri (N-N Çoka Çok İlişkiyi çözen köprü tablo)
    imlec.execute("""
    CREATE TABLE IF NOT EXISTS ProgramDersleri (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        ProgramId INTEGER NOT NULL,
        SubeId INTEGER NOT NULL,
        FOREIGN KEY (ProgramId) REFERENCES Program(Id),
        FOREIGN KEY (SubeId) REFERENCES Sube(Id),
        UNIQUE(ProgramId, SubeId)
    )
    """)

    # 6. Tercih Tablosu (Seçmeli Ders Öneri Sistemi için)
    imlec.execute("""
    CREATE TABLE IF NOT EXISTS Tercih (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        OgrenciId INTEGER NOT NULL,
        Alan TEXT NOT NULL,
        FOREIGN KEY (OgrenciId) REFERENCES Ogrenci(Id)
    )
    """)

    baglanti.commit()
    baglanti.close()
    print("Veritabanı ve tüm tablolar başarıyla oluşturuldu!")

if __name__ == "__main__":
    veritabanini_kur()