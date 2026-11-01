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


# ---------------- Ortak sayfa şablonu ----------------
SABLON = """
<!doctype html><html lang="tr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ baslik }}</title>
<style>
 body{font-family:system-ui,Segoe UI,Arial,sans-serif;margin:24px;max-width:1100px;color:#222}
 table{border-collapse:collapse;width:100%;margin:8px 0 20px}
 th,td{border:1px solid #ccc;padding:6px 8px;text-align:left;vertical-align:top}
 th{background:#f2f2f2}
 .hata{background:#fdecea;border:1px solid #f5c2c0;padding:10px;border-radius:6px}
 .uyari{background:#fff4e5;border:1px solid #ffd59e;padding:10px;border-radius:6px}
 .basari{background:#e8f5e9;border:1px solid #b7dfb9;padding:10px;border-radius:6px}
 tr.cakisan td{background:#fdecea}
 .etiket{font-size:12px;padding:2px 6px;border-radius:10px;background:#eee}
 .gun-hucre div{background:#eef3ff;border-left:3px solid #4a6cf7;margin:3px 0;padding:3px 5px;font-size:13px}
 .gun-hucre div.cakisan{background:#fdecea;border-left-color:#d93025}
 form.satir{display:inline}
 input,select{padding:4px;margin:2px}
</style></head><body>
<p><a href="/panel">Panel</a> · <a href="/dersler">Ders Kataloğu</a>
{% if session.get('rol') == 'yonetici' %} · <a href="/yonetici/katalog">Katalog Yönetimi</a>{% endif %}
{% if session.get('kullanici_id') %} · <a href="/cikis">Çıkış ({{ session.get('kullanici_adi') }})</a>{% endif %}</p>
{% with mesajlar = get_flashed_messages(with_categories=true) %}
  {% for kat, m in mesajlar %}<p class="{{ kat }}">{{ m }}</p>{% endfor %}
{% endwith %}
"""


def sayfa(govde, **baglam):
    baglam.setdefault("baslik", "Akıllı Ders Programı")
    return render_template_string(SABLON + govde + "</body></html>", **baglam)


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
            return "<h2>403 - Yetkisiz Erişim!</h2><p>Bu sayfaya yalnızca <b>Yönetici</b> rolündeki kullanıcılar erişebilir.</p><a href='/panel'>Panele Dön</a>", 403
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
    return """
    <h2>Akıllı Ders Programı ve Seçmeli Ders Öneri Sistemi</h2>
    <p><a href="/giris">Giriş Yap</a> | <a href="/kayit">Kayıt Ol</a></p>
    """


# 2. Kayıt Ol (Register) - Şifre Hash'lenerek kaydedilir
@app.route('/kayit', methods=['GET', 'POST'])
def kayit():
    mesaj = ""
    if request.method == 'POST':
        kadi = request.form['kullanici_adi']
        eposta = request.form['eposta']
        sifre = request.form['parola']

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

    return render_template_string("""
    <h2>Öğrenci Kayıt Ol</h2>
    {% if mesaj %}<p style="color:red;">{{ mesaj }}</p>{% endif %}
    <form method="POST">
        Kullanıcı Adı: <br><input type="text" name="kullanici_adi" required><br><br>
        E-posta: <br><input type="email" name="eposta" required><br><br>
        Şifre: <br><input type="password" name="parola" required><br><br>
        <button type="submit">Kayıt Ol</button>
    </form>
    <p>Zaten hesabınız var mı? <a href="/giris">Giriş Yap</a></p>
    """, mesaj=mesaj)


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

    return render_template_string("""
    <h2>Kullanıcı Girişi (Hafta 5)</h2>
    {% if mesaj %}<p style="color:red;">{{ mesaj }}</p>{% endif %}
    <form method="POST">
        Kullanıcı Adı: <br><input type="text" name="kullanici_adi" required><br><br>
        Şifre: <br><input type="password" name="parola" required><br><br>
        <button type="submit">Giriş Yap</button>
    </form>
    <p>Hesabınız yok mu? <a href="/kayit">Kayıt Ol</a></p>
    <hr>
    <small><b>Test Hesapları:</b><br>Yönetici: admin / admin123<br>Öğrenci: ogrenci / 123456</small>
    """, mesaj=mesaj)


# 4. Kullanıcı Paneli (Herkes giriş yapınca görür)
@app.route('/panel')
@giris_gerekli
def panel():
    return sayfa("""
    <h2>Kullanıcı Paneli</h2>
    <p>Giriş Yapan: <b>{{ session.kullanici_adi }}</b> — Rolünüz: <b>{{ session.rol }}</b></p>
    <ul>
        <li><a href="/dersler">Ders Kataloğu ve Program Oluşturucu (Hafta 6) + Çakışma Tespiti (Hafta 7)</a></li>
        <li><a href="/yonetici/katalog">Katalog Yönetimi — ders/şube ekle (yalnızca yönetici)</a></li>
        <li><a href="/admin-paneli">Yönetici Özel Sayfası</a> (Rol testi için)</li>
        <li><a href="/cikis">Çıkış Yap</a></li>
    </ul>
    """, baslik="Panel")


# 5. Yöneticiye Özel Korunan Sayfa (Yetkisizler giremez)
@app.route('/admin-paneli')
@yonetici_gerekli
def admin_paneli():
    return """
    <h2>Yönetici Paneli (Yalnızca Yönetici Rolü Erişebilir)</h2>
    <p>Tebrikler! Rol tabanlı erişim kontrolü başarıyla çalışıyor.</p>
    <a href="/panel">Geri Dön</a> | <a href="/cikis">Çıkış Yap</a>
    """


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


def haftalik_tablo(dersler, cakisan_ids):
    """Gün bazında, başlangıç saatine göre sıralı ders listesi."""
    tablo = {g: [] for g in GUNLER[:5]}
    for d in sorted(dersler, key=lambda d: dakikaya_cevir(d["Saat"])):
        tablo.setdefault(d["Gun"], []).append({**dict(d), "cakisan": d["SubeId"] in cakisan_ids})
    return tablo


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

    return sayfa("""
    <h2>Ders Kataloğu ve Program Oluşturucu <small>(Hafta 6 + Hafta 7)</small></h2>
    <p>Dönem: <b>{{ program.Donem }}</b> · Toplam AKTS: <b>{{ toplam_akts }}</b> / {{ akts_sinir }}
       · Durum: {% if program.Kaydedildi %}<span class="etiket">✔ Kaydedildi</span>{% else %}<span class="etiket">Taslak</span>{% endif %}</p>

    {% if cakismalar %}
      <div class="hata"><b>⚠ Programınızda {{ cakismalar|length }} çakışma var:</b>
      <ul>{% for c in cakismalar %}
        <li>{{ c.a.DersKodu }} ({{ c.a.Gun }} {{ c.a.Baslangic }}-{{ c.a.Bitis }}) ↔
            {{ c.b.DersKodu }} ({{ c.b.Baslangic }}-{{ c.b.Bitis }})
            — <b>{{ c.tur_aciklama }}</b>, ortak aralık {{ c.ortak_aralik }} ({{ c.dakika }} dk)</li>
      {% endfor %}</ul></div>
    {% endif %}

    <h3>Haftalık Programım</h3>
    <table><tr>{% for g in tablo %}<th>{{ g }}</th>{% endfor %}</tr>
      <tr>{% for g, liste in tablo.items() %}<td class="gun-hucre">
        {% for d in liste %}<div class="{{ 'cakisan' if d.cakisan }}"><b>{{ d.Saat }}-{{ d.BitisSaati }}</b><br>{{ d.DersKodu }}</div>{% endfor %}
      </td>{% endfor %}</tr></table>

    <table>
      <tr><th>Ders</th><th>Öğretim Elemanı</th><th>Gün / Saat</th><th>AKTS</th><th>İşlem</th></tr>
      {% for p in secilenler %}
      <tr class="{{ 'cakisan' if p.SubeId in cakisan_ids }}">
        <td>{{ p.DersKodu }} - {{ p.DersAdi }}</td><td>{{ p.HocaAdi }}</td>
        <td>{{ p.Gun }} {{ p.Saat }}-{{ p.BitisSaati }}</td><td>{{ p.AKTS }}</td>
        <td><form class="satir" method="post" action="/program/sil/{{ p.KayitId }}"><button>Kaldır</button></form></td>
      </tr>
      {% else %}<tr><td colspan="5">Henüz programa ders eklenmedi.</td></tr>{% endfor %}
    </table>

    <form class="satir" method="post" action="/program/kaydet"><button>💾 Programı Kaydet</button></form>
    {% if program.Kaydedildi and program.PaylasimKodu %}
      · Paylaşım bağlantısı: <a href="/paylas/{{ program.PaylasimKodu }}">{{ request.host_url }}paylas/{{ program.PaylasimKodu }}</a>
    {% endif %}

    <hr><h3>Açık Dersler Kataloğu</h3>
    <table>
      <tr><th>Kod</th><th>Ders Adı</th><th>Öğretim Elemanı</th><th>Gün / Saat</th><th>AKTS</th><th>Durum</th></tr>
      {% for k in katalog %}
      <tr>
        <td>{{ k.DersKodu }}</td><td>{{ k.DersAdi }}</td><td>{{ k.HocaAdi }}</td>
        <td>{{ k.Gun }} {{ k.Saat }}-{{ k.BitisSaati }}</td><td>{{ k.AKTS }}</td>
        <td>
          {% if k.secili %}✔ Programda
          {% elif k.ders_secili %}<span style="color:#888">Bu dersin başka şubesi seçili</span>
          {% else %}
            {% if k.cakisma %}<span style="color:#d93025">⚠ {{ k.cakisma[0].b.DersKodu }} ile çakışır</span><br>{% endif %}
            <form class="satir" method="post" action="/program/ekle/{{ k.SubeId }}"><button>+ Programa Ekle</button></form>
          {% endif %}
        </td>
      </tr>{% endfor %}
    </table>
    """, baslik="Ders Kataloğu", program=program, secilenler=secilenler, katalog=katalog_satirlari,
         cakismalar=cakismalar, cakisan_ids=cakisan_ids, tablo=haftalik_tablo(secilenler, cakisan_ids),
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
        return sayfa("""
        <div class="uyari"><h3>⚠ Çakışma Uyarısı</h3>
        <p><b>{{ y.DersKodu }} - {{ y.DersAdi }}</b> ({{ y.Gun }} {{ y.Saat }}-{{ y.BitisSaati }})
           programınızdaki şu derslerle çakışıyor:</p>
        <ul>{% for c in cakismalar %}
          <li>{{ c.b.DersKodu }} - {{ c.b.DersAdi }} ({{ c.b.Baslangic }}-{{ c.b.Bitis }}):
              <b>{{ c.tur_aciklama }}</b>, {{ c.ortak_aralik }} arası, {{ c.dakika }} dakika</li>
        {% endfor %}</ul>
        <p>Çakışan dersle programınız <b>kaydedilemez</b>. Yine de taslağa eklemek istiyor musunuz?</p>
        <form class="satir" method="post"><input type="hidden" name="zorla" value="1">
          <button>Yine de ekle</button></form>
        <a href="/dersler">Vazgeç</a></div>
        """, baslik="Çakışma Uyarısı", y=yeni, cakismalar=cakismalar)

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
    return sayfa("""
    <h2>Paylaşılan Ders Programı — {{ program.Donem }}</h2>
    <table><tr>{% for g in tablo %}<th>{{ g }}</th>{% endfor %}</tr>
      <tr>{% for g, liste in tablo.items() %}<td class="gun-hucre">
        {% for d in liste %}<div><b>{{ d.Saat }}-{{ d.BitisSaati }}</b><br>{{ d.DersKodu }} {{ d.DersAdi }}<br><small>{{ d.HocaAdi }}</small></div>{% endfor %}
      </td>{% endfor %}</tr></table>
    <p>Toplam AKTS: <b>{{ akts }}</b></p>
    """, baslik="Paylaşılan Program", program=program, tablo=haftalik_tablo(secilenler, set()),
         akts=sum(s["AKTS"] for s in secilenler))


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
    return sayfa("""
    <h2>Katalog Yönetimi (Yönetici)</h2>
    <h3>Ders Ekle</h3>
    <form method="post"><input type="hidden" name="islem" value="ders_ekle">
      <input name="kod" placeholder="BIL201" required> <input name="ad" placeholder="Ders adı" required>
      <input name="kredi" type="number" placeholder="Kredi" required> <input name="akts" type="number" placeholder="AKTS" required>
      <button>Ekle</button></form>

    <h3>Şube Ekle</h3>
    <form method="post"><input type="hidden" name="islem" value="sube_ekle">
      <select name="ders_id">{% for d in dersler %}<option value="{{ d.Id }}">{{ d.DersKodu }} - {{ d.DersAdi }}</option>{% endfor %}</select>
      <input name="hoca" placeholder="Öğretim elemanı" required>
      <select name="gun">{% for g in gunler %}<option>{{ g }}</option>{% endfor %}</select>
      <input name="bas" type="time" required> – <input name="bit" type="time" required>
      <button>Ekle</button></form>

    <h3>Dersler</h3>
    <table><tr><th>Kod</th><th>Ad</th><th>Kredi</th><th>AKTS</th><th></th></tr>
    {% for d in dersler %}<tr><td>{{ d.DersKodu }}</td><td>{{ d.DersAdi }}</td><td>{{ d.Kredi }}</td><td>{{ d.AKTS }}</td>
      <td><form class="satir" method="post"><input type="hidden" name="islem" value="ders_sil"><input type="hidden" name="id" value="{{ d.Id }}"><button>Sil</button></form></td></tr>{% endfor %}
    </table>
    <h3>Şubeler</h3>
    <table><tr><th>Ders</th><th>Öğretim Elemanı</th><th>Gün / Saat</th><th></th></tr>
    {% for s in subeler %}<tr><td>{{ s.DersKodu }}</td><td>{{ s.HocaAdi }}</td><td>{{ s.Gun }} {{ s.Saat }}-{{ s.BitisSaati }}</td>
      <td><form class="satir" method="post"><input type="hidden" name="islem" value="sube_sil"><input type="hidden" name="id" value="{{ s.SubeId }}"><button>Sil</button></form></td></tr>{% endfor %}
    </table>
    """, baslik="Katalog Yönetimi", dersler=dersler_, subeler=subeler, gunler=GUNLER)


if __name__ == "__main__":
    # Yerel geliştirme: python backend/app.py  (canlıda gunicorn kullanılır, bkz. Procfile)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1" if not CANLI_ORTAM else "0.0.0.0", port=port, debug=not CANLI_ORTAM)
