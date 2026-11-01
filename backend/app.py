from flask import Flask, request, redirect, url_for, session, render_template_string, abort, flash, g
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import functools
import os
import secrets
import sys
from datetime import timedelta
from werkzeug.middleware.proxy_fix import ProxyFix

from sema import sema_guncelle, ornek_veri_ekle
from sayfalar import (KAMU_SABLON, KAMU_SON, ANA_SAYFA, GIRIS_SAYFASI, KAYIT_SAYFASI,
                      UYGULAMA_SABLON, UYGULAMA_SON, PANEL, DERSLER, CAKISMA_UYARISI, PAYLAS,
                      KATALOG_YONETIMI, MESAJ_SAYFASI)
from cakisma import (GUNLER, zaman_araligi_dogrula, yeni_oturum_cakismalari,
                     program_cakismalari, dakikaya_cevir)

# -------------------------------------------------------------
# ORTAM DEĞİŞKENLERİ (Hafta 7 - Canlı Dağıtım)
#   GIZLI_ANAHTAR    : oturum çerezlerini imzalayan anahtar (bulutta mutlaka tanımlanır)
#   VERITABANI_YOLU  : SQLite dosyasının yolu (varsayılan: database/proje.db)
#   CANLI_ORTAM      : "1" ise HTTPS'e özel güvenli çerez ayarları açılır
#   PORT             : bulut platformunun verdiği port (Render/Railway otomatik tanımlar)
# Hiçbiri tanımlı değilse uygulama yerelde eskisi gibi çalışır.
# -------------------------------------------------------------
CANLI_ORTAM = os.environ.get("CANLI_ORTAM") == "1"

app = Flask(__name__)
app.secret_key = os.environ.get("GIZLI_ANAHTAR", "akillidersprogrami_gizli_anahtar")
# Oturum yönetimi (Hafta 5): 30 dk sonra oturum düşer, çerez JavaScript ile okunamaz
app.config.update(
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=CANLI_ORTAM,   # canlıda çerez yalnızca HTTPS ile gönderilir
)
# Bulut platformları uygulamanın önüne bir vekil sunucu (proxy) koyar; gerçek https adresini
# ve istemci IP'sini doğru görmek için X-Forwarded-* başlıklarına güvenilir.
if CANLI_ORTAM:
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

# Veritabanı dosyasının tam yolu (uygulama hangi klasörden çalıştırılırsa çalıştırılsın doğru dosyayı bulur)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("VERITABANI_YOLU") or os.path.join(BASE_DIR, "..", "database", "proje.db")

# Veritabanı dosyası yoksa (ör. bulutta boş bir diskte ilk açılış) tabloları ve örnek verileri oluştur
if not os.path.exists(DB_PATH):
    sys.path.insert(0, os.path.join(BASE_DIR, ".."))
    from init_db import veritabanini_kur
    veritabanini_kur(DB_PATH)

AKTIF_DONEM = "2026-Güz"
AKTS_UST_SINIR = 30   # İş kuralı: bir dönemde en fazla 30 AKTS alınabilir


def db_baglantisi():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")   # İlişkisel bütünlük (FK) kontrolleri açık
    g.setdefault("_baglantilar", []).append(conn)
    return conn


@app.teardown_appcontext
def baglantilari_kapat(_hata):
    # Bir hata oluşsa bile açık kalan bağlantıları kapat (veritabanı kilitlenmesin)
    for c in g.pop("_baglantilar", []):
        c.close()


# Uygulama açılırken şemayı güncelle (Hafta 6-7 sütunları) ve örnek verileri tamamla
with sqlite3.connect(DB_PATH) as _c:
    sema_guncelle(_c)
    ornek_veri_ekle(_c)


# ---------------- Ortak sayfa şablonu (arayüz: sayfalar.py) ----------------
def sayfa(govde, **baglam):
    baglam.setdefault("baslik", "Akıllı Ders Programı")
    baglam.setdefault("aktif", "")
    return render_template_string(UYGULAMA_SABLON + govde + UYGULAMA_SON, **baglam)


def mesaj_sayfasi(ikon, baslik, aciklama, kod):
    return sayfa(MESAJ_SAYFASI, ikon=ikon, baslik=baslik, aciklama=aciklama), kod


@app.errorhandler(403)
def hata_403(_e):
    return mesaj_sayfasi("🔒", "Bu işlem için yetkiniz yok",
                         "Yalnızca kendi kayıtlarınızı değiştirebilirsiniz.", 403)


@app.errorhandler(404)
def hata_404(_e):
    return mesaj_sayfasi("🔍", "Sayfa bulunamadı",
                         "Aradığınız kayıt silinmiş ya da bağlantı hatalı olabilir.", 404)


# ---------------- Yetkilendirme dekoratörleri (Hafta 5) ----------------
def giris_gerekli(f):
    @functools.wraps(f)
    def sarmal(*args, **kwargs):
        if 'kullanici_id' not in session:
            return redirect(url_for('giris'))
        return f(*args, **kwargs)
    return sarmal


def yonetici_gerekli(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'kullanici_id' not in session:
            return redirect(url_for('giris'))
        if session.get('rol') != 'yonetici':
            return mesaj_sayfasi("🔒", "403 · Yetkisiz erişim",
                                 "Bu sayfaya yalnızca Yönetici rolündeki kullanıcılar erişebilir.", 403)
        return f(*args, **kwargs)
    return decorated_function


# Sağlık kontrolü: bulut platformu uygulamanın ayakta olduğunu bu adresle anlar
@app.route('/saglik')
def saglik():
    with sqlite3.connect(DB_PATH) as c:
        ders_sayisi = c.execute("SELECT COUNT(*) FROM Ders").fetchone()[0]
    return {"durum": "ok", "ders_sayisi": ders_sayisi}


# 1. Ana Sayfa
@app.route('/')
def ana_sayfa():
    if 'kullanici_id' in session:
        return redirect(url_for('panel'))
    return kamu_sayfa(ANA_SAYFA, baslik="Ana Sayfa")


def kamu_sayfa(govde, **baglam):
    """Herkese açık sayfaları (ana sayfa, giriş, kayıt) ortak şablonla oluşturur."""
    return render_template_string(KAMU_SABLON + govde + KAMU_SON, **baglam)


# 2. Kayıt Ol (Register) - Şifre Hash'lenerek kaydedilir
@app.route('/kayit', methods=['GET', 'POST'])
def kayit():
    mesaj = ""
    if request.method == 'POST':
        kadi = request.form['kullanici_adi']
        eposta = request.form['eposta']
        sifre = request.form['parola']

        # Sunucu tarafı doğrulama (tarayıcıdaki kontroller atlanabilir)
        if len(kadi.strip()) < 3 or len(sifre) < 6 or "@" not in eposta:
            return kamu_sayfa(KAYIT_SAYFASI, baslik="Kayıt Ol",
                              mesaj="Kullanıcı adı en az 3, şifre en az 6 karakter olmalı ve geçerli bir e-posta girilmeli.")

        parola_hash = generate_password_hash(sifre)

        try:
            conn = db_baglantisi()
            conn.execute("INSERT INTO Kullanici (KullaniciAdi, Eposta, ParolaHash, Rol) VALUES (?, ?, ?, 'ogrenci')",
                         (kadi, eposta, parola_hash))
            conn.commit()
            conn.close()
            return redirect(url_for('giris'))
        except sqlite3.IntegrityError:
            mesaj = "Bu kullanıcı adı veya e-posta zaten kayıtlı!"

    return kamu_sayfa(KAYIT_SAYFASI, baslik="Kayıt Ol", mesaj=mesaj)


# 3. Giriş Yap (Login) - Hash doğrulaması ve Session başlatma
@app.route('/giris', methods=['GET', 'POST'])
def giris():
    mesaj = ""
    if request.method == 'POST':
        kadi = request.form['kullanici_adi']
        sifre = request.form['parola']

        conn = db_baglantisi()
        kullanici = conn.execute("SELECT * FROM Kullanici WHERE KullaniciAdi = ?", (kadi,)).fetchone()
        conn.close()

        if kullanici and check_password_hash(kullanici['ParolaHash'], sifre):
            session.clear()              # oturum sabitleme (session fixation) saldırısına karşı
            session.permanent = True     # PERMANENT_SESSION_LIFETIME geçerli olsun
            session['kullanici_id'] = kullanici['Id']
            session['kullanici_adi'] = kullanici['KullaniciAdi']
            session['rol'] = kullanici['Rol']
            return redirect(url_for('panel'))
        else:
            mesaj = "Hatalı kullanıcı adı veya şifre!"

    return kamu_sayfa(GIRIS_SAYFASI, baslik="Giriş Yap", mesaj=mesaj)


# 4. Kullanıcı Paneli (Herkes giriş yapınca görür)
@app.route('/panel')
@giris_gerekli
def panel():
    conn = db_baglantisi()
    program = program_getir_veya_olustur(conn, session['kullanici_id'])
    secilenler = program_dersleri(conn, program["Id"])
    yonetici = None
    if session.get('rol') == 'yonetici':
        yonetici = {t: conn.execute(f"SELECT COUNT(*) FROM {tablo}").fetchone()[0]
                    for t, tablo in (("ders", "Ders"), ("sube", "Sube"), ("kullanici", "Kullanici"))}
    conn.close()
    cakismalar = program_cakismalari([sube_oturum(s) for s in secilenler])
    cakisan_ids = {c["a"]["SubeId"] for c in cakismalar} | {c["b"]["SubeId"] for c in cakismalar}
    return sayfa(PANEL, baslik="Panel", aktif="panel", program=program,
                 ders_sayisi=len(secilenler), akts=sum(s["AKTS"] for s in secilenler),
                 akts_sinir=AKTS_UST_SINIR, cakisma_sayisi=len(cakismalar), yonetici=yonetici,
                 iz=haftalik_izgara(secilenler, cakisan_ids))


# 5. Yöneticiye Özel Korunan Sayfa (Yetkisizler giremez)
@app.route('/admin-paneli')
@yonetici_gerekli
def admin_paneli():
    return mesaj_sayfasi("✅", "Yönetici sayfası",
                         "Rol tabanlı erişim kontrolü çalışıyor: bu sayfayı yalnızca yönetici rolü görebilir.", 200)


# 6. Çıkış Yap (Logout)
@app.route('/cikis')
def cikis():
    session.clear()
    return redirect(url_for('giris'))


# =============================================================
# HAFTA 6: Çekirdek Modül A - Ders Kataloğu ve Program Oluşturucu
# =============================================================
#
# Veri modeli ve ilişkiler:
#   Ders 1 ── N Sube            (bir dersin birden çok şubesi olur)
#   Kullanici 1 ── 1 Ogrenci    (Ogrenci.KullaniciId ile giriş hesabına bağlanır)
#   Ogrenci 1 ── 1 Program      (her öğrencinin aktif dönem programı)
#   Program N ── N Sube         (ProgramDersleri köprü tablosu ile)
#
# İş kuralları (program_ekle içinde sırasıyla uygulanır):
#   K1. Şube gerçekten var olmalı (yoksa 404)
#   K2. Aynı dersin iki şubesi aynı programda olamaz
#   K3. Toplam AKTS, AKTS_UST_SINIR'ı aşamaz
#   K4. (Hafta 7) Zaman çakışması varsa uyarı verilir; öğrenci onaylarsa eklenir
#   K5. Programı yalnızca sahibi değiştirebilir (sahiplik kontrolü)
#   K6. Çakışma içeren program "kaydedilemez" (kesinleştirilemez)

def sube_oturum(satir):
    """Veritabanı satırını çakışma modülünün beklediği sözlüğe çevirir."""
    return {
        "SubeId": satir["SubeId"],
        "DersKodu": satir["DersKodu"],
        "DersAdi": satir["DersAdi"],
        "HocaAdi": satir["HocaAdi"],
        "Gun": satir["Gun"],
        "Baslangic": satir["Saat"],
        "Bitis": satir["BitisSaati"],
    }


SUBE_SORGUSU = """
    SELECT Sube.Id AS SubeId, Sube.DersId, Ders.DersKodu, Ders.DersAdi, Ders.Kredi, Ders.AKTS,
           Sube.HocaAdi, Sube.Gun, Sube.Saat, Sube.BitisSaati
    FROM Sube JOIN Ders ON Sube.DersId = Ders.Id
"""


def ogrenci_id_bul(conn, kullanici_id):
    """Kullanici (giriş hesabı) 1 ── 1 Ogrenci. Program tablosu Ogrenci'ye bağlıdır;
    giriş yapan hesabın öğrenci kaydı yoksa otomatik oluşturulur."""
    satir = conn.execute("SELECT Id FROM Ogrenci WHERE KullaniciId = ?", (kullanici_id,)).fetchone()
    if satir:
        return satir["Id"]
    k = conn.execute("SELECT KullaniciAdi FROM Kullanici WHERE Id = ?", (kullanici_id,)).fetchone()
    yeni_id = conn.execute(
        "INSERT INTO Ogrenci (Ad, Soyad, OgrenciNo, KullaniciId) VALUES (?, ?, ?, ?)",
        (k["KullaniciAdi"] if k else "Öğrenci", "-", f"K{kullanici_id:06d}", kullanici_id),
    ).lastrowid
    conn.commit()
    return yeni_id


def program_getir_veya_olustur(conn, kullanici_id):
    ogrenci_id = ogrenci_id_bul(conn, kullanici_id)
    program = conn.execute("SELECT * FROM Program WHERE OgrenciId = ?", (ogrenci_id,)).fetchone()
    if program:
        return program
    conn.execute("INSERT INTO Program (OgrenciId, Donem) VALUES (?, ?)", (ogrenci_id, AKTIF_DONEM))
    conn.commit()
    return conn.execute("SELECT * FROM Program WHERE OgrenciId = ?", (ogrenci_id,)).fetchone()


def program_dersleri(conn, program_id):
    return conn.execute(
        SUBE_SORGUSU.replace("SELECT ", "SELECT ProgramDersleri.Id AS KayitId, ", 1)
        + " JOIN ProgramDersleri ON ProgramDersleri.SubeId = Sube.Id WHERE ProgramDersleri.ProgramId = ?",
        (program_id,),
    ).fetchall()


def haftalik_izgara(dersler, cakisan_ids):
    """Dersleri haftalık zaman ızgarasına yerleştirir (30 dakikalık satırlar).
    Aynı günde çakışan dersler yan yana gösterilir."""
    gunler = GUNLER[:5]
    if any(d["Gun"] in GUNLER[5:] for d in dersler):
        gunler = GUNLER[:7]
    bas = min([8 * 60] + [dakikaya_cevir(d["Saat"]) // 60 * 60 for d in dersler])
    bit = max([17 * 60] + [-(-dakikaya_cevir(d["BitisSaati"]) // 60) * 60 for d in dersler])
    satir = lambda dk: (dk - bas) // 30 + 2          # 1. satır gün başlıkları
    # Çakışan dersler yan yana şeritlere (lane) yerleştirilir: her ders, kendisiyle örtüşen
    # önceki derslerin kullanmadığı ilk şeride girer; grup içindeki şerit sayısı genişliği belirler.
    bloklar = []
    for gun in gunler:
        gunun = sorted((d for d in dersler if d["Gun"] == gun), key=lambda d: dakikaya_cevir(d["Saat"]))
        grup, grup_bitis = [], -1
        for d in gunun + [None]:
            b1 = dakikaya_cevir(d["Saat"]) if d else None
            if d is None or b1 >= grup_bitis:          # yeni çakışma grubu başlıyor
                for b in grup:
                    b["serit_sayisi"] = max(x["serit"] for x in grup) + 1
                bloklar += grup
                grup, grup_bitis = [], -1
                if d is None:
                    break
            b2 = dakikaya_cevir(d["BitisSaati"])
            dolu = {x["serit"] for x in grup if x["_b2"] > b1}
            serit = next(i for i in range(len(grup) + 1) if i not in dolu)
            grup.append({**dict(d), "_b1": b1, "_b2": b2, "serit": serit,
                         "sutun": gunler.index(gun) + 2, "satir": satir(b1),
                         "uzunluk": max(1, (b2 - b1) // 30), "cakisan": d["SubeId"] in cakisan_ids})
            grup_bitis = max(grup_bitis, b2)
    saatler = [{"etiket": f"{dk // 60:02d}:00", "satir": satir(dk)} for dk in range(bas, bit, 60)]
    return {"gunler": gunler, "saatler": saatler, "bloklar": bloklar, "satir": (bit - bas) // 30}


@app.route('/dersler')
@giris_gerekli
def dersler():
    conn = db_baglantisi()
    program = program_getir_veya_olustur(conn, session['kullanici_id'])
    katalog = conn.execute(SUBE_SORGUSU + " ORDER BY Ders.DersKodu, Sube.Gun").fetchall()
    secilenler = program_dersleri(conn, program["Id"])
    conn.close()

    # HAFTA 7 entegrasyonu: programdaki tüm çakışmaları hesapla
    cakismalar = program_cakismalari([sube_oturum(s) for s in secilenler])
    cakisan_ids = {c["a"]["SubeId"] for c in cakismalar} | {c["b"]["SubeId"] for c in cakismalar}

    # Katalogda her şube için "programımla çakışıyor mu?" bilgisini önceden göster
    mevcut = [sube_oturum(s) for s in secilenler]
    secili_sube_ids = {s["SubeId"] for s in secilenler}
    secili_ders_ids = {s["DersId"] for s in secilenler}
    katalog_satirlari = []
    for k in katalog:
        cak = [] if k["SubeId"] in secili_sube_ids else yeni_oturum_cakismalari(sube_oturum(k), mevcut)
        katalog_satirlari.append({**dict(k), "cakisma": cak,
                                  "secili": k["SubeId"] in secili_sube_ids,
                                  "ders_secili": k["DersId"] in secili_ders_ids})

    toplam_akts = sum(s["AKTS"] for s in secilenler)

    return sayfa(DERSLER, baslik="Ders Programım", aktif="dersler", program=program, secilenler=secilenler,
         katalog=katalog_satirlari, cakismalar=cakismalar, cakisan_ids=cakisan_ids,
         iz=haftalik_izgara(secilenler, cakisan_ids),
         toplam_akts=toplam_akts, akts_sinir=AKTS_UST_SINIR)


@app.route('/program/ekle/<int:sube_id>', methods=['POST'])
@giris_gerekli
def program_ekle(sube_id):
    zorla = request.form.get('zorla') == '1'
    conn = db_baglantisi()
    program = program_getir_veya_olustur(conn, session['kullanici_id'])

    # K1: Şube var mı?
    yeni = conn.execute(SUBE_SORGUSU + " WHERE Sube.Id = ?", (sube_id,)).fetchone()
    if not yeni:
        conn.close()
        abort(404)

    secilenler = program_dersleri(conn, program["Id"])

    # K2: Aynı ders iki kez alınamaz
    if any(s["DersId"] == yeni["DersId"] for s in secilenler):
        conn.close()
        flash(f"{yeni['DersKodu']} zaten programınızda! Aynı dersin iki şubesini alamazsınız.", "hata")
        return redirect(url_for('dersler'))

    # K3: AKTS üst sınırı
    toplam = sum(s["AKTS"] for s in secilenler) + yeni["AKTS"]
    if toplam > AKTS_UST_SINIR:
        conn.close()
        flash(f"AKTS sınırı aşılıyor ({toplam} > {AKTS_UST_SINIR}). Önce başka bir dersi kaldırın.", "hata")
        return redirect(url_for('dersler'))

    # K4 (Hafta 7): Zaman çakışması kontrolü
    cakismalar = yeni_oturum_cakismalari(sube_oturum(yeni), [sube_oturum(s) for s in secilenler])
    if cakismalar and not zorla:
        conn.close()
        return sayfa(CAKISMA_UYARISI, baslik="Çakışma Uyarısı", aktif="dersler", y=yeni, cakismalar=cakismalar)

    try:
        conn.execute("INSERT INTO ProgramDersleri (ProgramId, SubeId) VALUES (?, ?)", (program["Id"], sube_id))
        # Program değiştiği için tekrar kaydedilmesi gerekir
        conn.execute("UPDATE Program SET Kaydedildi = 0 WHERE Id = ?", (program["Id"],))
        conn.commit()
        flash(f"{yeni['DersKodu']} programa eklendi.", "uyari" if cakismalar else "basari")
    except sqlite3.IntegrityError:
        flash("Bu şube zaten programınızda.", "hata")
    finally:
        conn.close()
    return redirect(url_for('dersler'))


@app.route('/program/sil/<int:kayit_id>', methods=['POST'])
@giris_gerekli
def program_sil(kayit_id):
    conn = db_baglantisi()
    # K5: Sahiplik kontrolü - kayıt gerçekten bu öğrencinin programına mı ait?
    kayit = conn.execute("""
        SELECT ProgramDersleri.Id, ProgramDersleri.ProgramId FROM ProgramDersleri
        JOIN Program ON ProgramDersleri.ProgramId = Program.Id
        JOIN Ogrenci ON Program.OgrenciId = Ogrenci.Id
        WHERE ProgramDersleri.Id = ? AND Ogrenci.KullaniciId = ?
    """, (kayit_id, session['kullanici_id'])).fetchone()
    if not kayit:
        conn.close()
        abort(403)
    conn.execute("DELETE FROM ProgramDersleri WHERE Id = ?", (kayit_id,))
    conn.execute("UPDATE Program SET Kaydedildi = 0 WHERE Id = ?", (kayit["ProgramId"],))
    conn.commit()
    conn.close()
    flash("Ders programdan kaldırıldı.", "basari")
    return redirect(url_for('dersler'))


@app.route('/program/kaydet', methods=['POST'])
@giris_gerekli
def program_kaydet():
    conn = db_baglantisi()
    program = program_getir_veya_olustur(conn, session['kullanici_id'])
    secilenler = program_dersleri(conn, program["Id"])
    if not secilenler:
        conn.close()
        flash("Boş program kaydedilemez. Önce ders ekleyin.", "hata")
        return redirect(url_for('dersler'))
    # K6: Çakışma varken kaydetme yok
    if program_cakismalari([sube_oturum(s) for s in secilenler]):
        conn.close()
        flash("Programda çakışma var! Kaydetmeden önce çakışan derslerden birini kaldırın.", "hata")
        return redirect(url_for('dersler'))
    kod = program["PaylasimKodu"] or secrets.token_urlsafe(8)
    conn.execute("UPDATE Program SET Kaydedildi = 1, PaylasimKodu = ? WHERE Id = ?", (kod, program["Id"]))
    conn.commit()
    conn.close()
    flash("Program kaydedildi. Paylaşım bağlantısı oluşturuldu.", "basari")
    return redirect(url_for('dersler'))


@app.route('/paylas/<kod>')
def program_paylas(kod):
    """Salt okunur paylaşım sayfası (giriş gerekmez, yalnızca kaydedilmiş programlar)."""
    conn = db_baglantisi()
    program = conn.execute("SELECT * FROM Program WHERE PaylasimKodu = ? AND Kaydedildi = 1", (kod,)).fetchone()
    if not program:
        conn.close()
        abort(404)
    secilenler = program_dersleri(conn, program["Id"])
    conn.close()
    return sayfa(PAYLAS, baslik="Paylaşılan Program", program=program, dersler=secilenler,
         iz=haftalik_izgara(secilenler, set()), akts=sum(s["AKTS"] for s in secilenler))


# ---------------- Katalog yönetimi (yönetici) ----------------
@app.route('/yonetici/katalog', methods=['GET', 'POST'])
@yonetici_gerekli
def katalog_yonetimi():
    conn = db_baglantisi()
    if request.method == 'POST':
        islem = request.form.get('islem')
        hatalar = []

        if islem == 'ders_ekle':
            kod = request.form.get('kod', '').strip().upper()
            ad = request.form.get('ad', '').strip()
            try:
                kredi, akts = int(request.form.get('kredi', '')), int(request.form.get('akts', ''))
            except ValueError:
                kredi = akts = 0
                hatalar.append("Kredi ve AKTS tam sayı olmalı.")
            if not (3 <= len(kod) <= 10 and kod.isalnum()):
                hatalar.append("Ders kodu 3-10 karakter, yalnızca harf/rakam olmalı (örn. BIL201).")
            if not ad:
                hatalar.append("Ders adı boş olamaz.")
            if not (1 <= kredi <= 10) or not (1 <= akts <= 15):
                hatalar.append("Kredi 1-10, AKTS 1-15 arasında olmalı.")
            if not hatalar:
                try:
                    conn.execute("INSERT INTO Ders (DersKodu, DersAdi, Kredi, AKTS) VALUES (?, ?, ?, ?)",
                                 (kod, ad, kredi, akts))
                    conn.commit()
                    flash(f"{kod} eklendi.", "basari")
                except sqlite3.IntegrityError:
                    hatalar.append(f"{kod} kodlu ders zaten var.")

        elif islem == 'sube_ekle':
            ders_id = request.form.get('ders_id', type=int)
            hoca = request.form.get('hoca', '').strip()
            gun, bas, bit = request.form.get('gun'), request.form.get('bas', ''), request.form.get('bit', '')
            if not conn.execute("SELECT 1 FROM Ders WHERE Id = ?", (ders_id,)).fetchone():
                hatalar.append("Geçersiz ders seçimi.")
            if not hoca:
                hatalar.append("Öğretim elemanı boş olamaz.")
            hatalar += zaman_araligi_dogrula(gun, bas, bit)
            if not hatalar:
                # Hafta 7 kuralını katalogda da uygula: aynı hoca aynı anda iki derste olamaz
                hoca_subeleri = conn.execute(SUBE_SORGUSU + " WHERE Sube.HocaAdi = ?", (hoca,)).fetchall()
                yeni = {"SubeId": None, "DersKodu": "", "DersAdi": "", "HocaAdi": hoca,
                        "Gun": gun, "Baslangic": bas, "Bitis": bit}
                for c in yeni_oturum_cakismalari(yeni, [sube_oturum(s) for s in hoca_subeleri]):
                    hatalar.append(f"{hoca} bu saatte {c['b']['DersKodu']} dersinde ({c['b']['Baslangic']}-{c['b']['Bitis']}).")
            if not hatalar:
                conn.execute("INSERT INTO Sube (DersId, HocaAdi, Gun, Saat, BitisSaati) VALUES (?, ?, ?, ?, ?)",
                             (ders_id, hoca, gun, bas, bit))
                conn.commit()
                flash("Şube eklendi.", "basari")

        elif islem in ('sube_sil', 'ders_sil'):
            hedef = request.form.get('id', type=int)
            # İlişkili kayıtlar: programlarda kullanılan şube/ders silinemez
            if islem == 'sube_sil':
                kullanim = conn.execute("SELECT COUNT(*) FROM ProgramDersleri WHERE SubeId = ?", (hedef,)).fetchone()[0]
                if kullanim:
                    hatalar.append(f"Bu şube {kullanim} öğrenci programında kullanılıyor, silinemez.")
                else:
                    conn.execute("DELETE FROM Sube WHERE Id = ?", (hedef,))
            else:
                sube_sayisi = conn.execute("SELECT COUNT(*) FROM Sube WHERE DersId = ?", (hedef,)).fetchone()[0]
                if sube_sayisi:
                    hatalar.append("Önce bu dersin şubelerini silin.")
                else:
                    try:
                        conn.execute("DELETE FROM Ders WHERE Id = ?", (hedef,))
                    except sqlite3.IntegrityError:
                        hatalar.append("Bu ders başka kayıtlarda (ör. tercihler) kullanılıyor, silinemez.")
            if not hatalar:
                conn.commit()
                flash("Silindi.", "basari")

        for h in hatalar:
            flash(h, "hata")
        conn.close()
        return redirect(url_for('katalog_yonetimi'))

    dersler_ = conn.execute("SELECT * FROM Ders ORDER BY DersKodu").fetchall()
    subeler = conn.execute(SUBE_SORGUSU + " ORDER BY Ders.DersKodu").fetchall()
    conn.close()
    return sayfa(KATALOG_YONETIMI, baslik="Katalog Yönetimi", aktif="katalog", dersler=dersler_, subeler=subeler, gunler=GUNLER)


if __name__ == "__main__":
    # Yerel geliştirme: python backend/app.py  (canlıda gunicorn kullanılır, bkz. Procfile)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1" if not CANLI_ORTAM else "0.0.0.0", port=port, debug=not CANLI_ORTAM)
