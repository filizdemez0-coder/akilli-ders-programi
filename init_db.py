from werkzeug.security import generate_password_hash
import sqlite3
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))
from sema import sema_guncelle, ornek_veri_ekle

VARSAYILAN_YOL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "proje.db")


def veritabanini_kur(yol=None):
    # Yol verilmezse: VERITABANI_YOLU ortam değişkeni, o da yoksa database/proje.db
    yol = yol or os.environ.get("VERITABANI_YOLU") or VARSAYILAN_YOL
    os.makedirs(os.path.dirname(os.path.abspath(yol)), exist_ok=True)
    baglanti = sqlite3.connect(yol)
    imlec = baglanti.cursor()

    # 1. Ogrenci Tablosu
    imlec.execute("""
    CREATE TABLE IF NOT EXISTS Ogrenci (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Ad TEXT NOT NULL,
        Soyad TEXT NOT NULL,
        OgrenciNo TEXT UNIQUE NOT NULL,
        KullaniciId INTEGER REFERENCES Kullanici(Id)   -- Hafta 6: giriş hesabı bağlantısı
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

    # 3. Sube Tablosu (1-N İlişki: Bir dersin birden çok şubesi olur)
    imlec.execute("""
    CREATE TABLE IF NOT EXISTS Sube (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        DersId INTEGER NOT NULL,
        HocaAdi TEXT NOT NULL,
        Gun TEXT NOT NULL,
        Saat TEXT NOT NULL,          -- Başlangıç saati (SS:DD)
        BitisSaati TEXT,             -- Hafta 7: Bitiş saati (SS:DD)
        FOREIGN KEY (DersId) REFERENCES Ders(Id)
    )
    """)

    # 4. Program Tablosu
    imlec.execute("""
    CREATE TABLE IF NOT EXISTS Program (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        OgrenciId INTEGER NOT NULL,
        Donem TEXT NOT NULL,
        Kaydedildi INTEGER NOT NULL DEFAULT 0,   -- Hafta 6: Kaydet
        PaylasimKodu TEXT,                        -- Hafta 6: Paylaş
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
        DersId INTEGER NOT NULL,
        OncelikSirasi INTEGER NOT NULL,
        FOREIGN KEY (OgrenciId) REFERENCES Ogrenci(Id),
        FOREIGN KEY (DersId) REFERENCES Ders(Id)
    )
    """)
    # 7. Kullanıcı Tablosu (Hafta 5 - Kimlik Doğrulama)
    imlec.execute("""
    CREATE TABLE IF NOT EXISTS Kullanici (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        KullaniciAdi TEXT UNIQUE NOT NULL,
        Eposta TEXT UNIQUE NOT NULL,
        ParolaHash TEXT NOT NULL,
        Rol TEXT NOT NULL DEFAULT 'ogrenci'
    )
    """)

    # --- HAFTA 4: Sentetik (Sahte) Veri Ekleme ---
    # Tablolar boşsa örnek verileri ekleyelim
    imlec.execute("SELECT COUNT(*) FROM Ogrenci")
    if imlec.fetchone()[0] == 0:
        # Örnek Öğrenci
        imlec.execute("INSERT INTO Ogrenci (Ad, Soyad, OgrenciNo) VALUES ('Ahmet', 'Yılmaz', '220101001')")
        
        # Örnek Dersler
        imlec.execute("INSERT INTO Ders (DersKodu, DersAdi, Kredi, AKTS) VALUES ('BIL101', 'Programlama Temelleri', 3, 5)")
        imlec.execute("INSERT INTO Ders (DersKodu, DersAdi, Kredi, AKTS) VALUES ('MAT101', 'Genel Matematik', 4, 6)")
        
        # Örnek Şubeler
        imlec.execute("INSERT INTO Sube (DersId, HocaAdi, Gun, Saat, BitisSaati) VALUES (1, 'Dr. Ali Veli', 'Pazartesi', '09:00', '11:00')")
        imlec.execute("INSERT INTO Sube (DersId, HocaAdi, Gun, Saat, BitisSaati) VALUES (2, 'Doç. Ayşe Kara', 'Salı', '13:00', '15:00')")

    # Örnek Kullanıcılar (Hafta 5)
    imlec.execute("SELECT COUNT(*) FROM Kullanici")
    if imlec.fetchone()[0] == 0:
        admin_hash = generate_password_hash("admin123")
        ogrenci_hash = generate_password_hash("123456")
        
        imlec.execute("INSERT INTO Kullanici (KullaniciAdi, Eposta, ParolaHash, Rol) VALUES (?, ?, ?, ?)",
                      ("admin", "admin@bingol.edu.tr", admin_hash, "yonetici"))
        imlec.execute("INSERT INTO Kullanici (KullaniciAdi, Eposta, ParolaHash, Rol) VALUES (?, ?, ?, ?)",
                      ("ogrenci", "ogrenci@bingol.edu.tr", ogrenci_hash, "ogrenci"))
    baglanti.commit()

    # Hafta 6-7: eski veritabanlarına eksik sütunları ekle + çakışma örnek verileri
    sema_guncelle(baglanti)
    ornek_veri_ekle(baglanti)
    baglanti.close()
    print("Veritabanı ve tablolar başarıyla oluşturuldu, sahte veriler yüklendi!")

if __name__ == "__main__":
    veritabanini_kur()