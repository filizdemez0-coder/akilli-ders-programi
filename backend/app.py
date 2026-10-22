from flask import Flask, request, redirect, url_for, session, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import functools
import os

app = Flask(__name__)
app.secret_key = "akillidersprogrami_gizli_anahtar"

# Veritabanı dosyasının tam yolunu bulalım
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "database", "proje.db")

def db_baglantisi():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Rol Tabanlı Erişim Koruması Dekoratörü (Hafta 5 Gereksinimi)
def yonetici_gerekli(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'kullanici_id' not in session:
            return redirect(url_for('giris'))
        if session.get('rol') != 'yonetici':
            return "<h2>403 - Yetkisiz Erişim!</h2><p>Bu sayfaya yalnızca <b>Yönetici</b> rolündeki kullanıcılar erişebilir.</p><a href='/panel'>Panele Dön</a>", 403
        return f(*args, **kwargs)
    return decorated_function

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
def panel():
    if 'kullanici_id' not in session:
        return redirect(url_for('giris'))
    
    kadi = session.get('kullanici_adi')
    rol = session.get('rol')
    
    return render_template_string("""
    <h2>Kullanıcı Paneli</h2>
    <p>Giriş Yapan: <b>{{ kadi }}</b></p>
    <p>Rolünüz: <b>{{ rol }}</b></p>
    <ul>
        <li><a href="/admin-paneli">Yönetici Özel Sayfasına Git</a> (Rol testi için)</li>
        <li><a href="/cikis">Çıkış Yap</a></li>
    </ul>
    """, kadi=kadi, rol=rol)

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

if __name__ == "__main__":
    app.run(debug=True)