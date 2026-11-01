"""
Herkese açık sayfaların (ana sayfa, giriş, kayıt) arayüz şablonları.
Sunum katmanı: yalnızca HTML/CSS içerir, iş mantığı app.py'dedir.
"""

KAMU_SABLON = """<!doctype html>
<html lang="tr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ baslik }} · Akıllı Ders Programı</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root{
  --zemin:#f6f4ef; --kart:#ffffff; --murekkep:#1b2232; --soluk:#5d6577; --cizgi:#e4e0d6;
  --vurgu:#2f4bd8; --vurgu-acik:#e8ecfd; --uyari:#d4472f; --uyari-acik:#fdeae6; --yesil:#1f8a5b;
}
*{box-sizing:border-box}
body{margin:0;background:var(--zemin);color:var(--murekkep);
  font-family:"Plus Jakarta Sans",system-ui,"Segoe UI",sans-serif;line-height:1.55}
a{color:var(--vurgu)}
.kap{max-width:1100px;margin:0 auto;padding:0 20px}
header.ust{display:flex;align-items:center;justify-content:space-between;padding:22px 0}
.logo{display:flex;align-items:center;gap:10px;font-weight:800;font-size:18px;text-decoration:none;color:var(--murekkep)}
.logo i{width:30px;height:30px;border-radius:8px;background:var(--murekkep);display:grid;place-items:center;
  color:#fff;font-style:normal;font-size:15px}
.dugme{display:inline-block;padding:11px 20px;border-radius:10px;font-weight:600;text-decoration:none;
  border:1.5px solid var(--murekkep);color:var(--murekkep);background:transparent;cursor:pointer;font:inherit;font-weight:600}
.dugme.dolu{background:var(--murekkep);color:#fff}
.dugme.dolu:hover{background:#000}
.dugme:hover{transform:translateY(-1px)}
.ust nav{display:flex;gap:10px}

/* ---- Ana sayfa ---- */
.hero{display:grid;grid-template-columns:1.05fr .95fr;gap:48px;align-items:center;padding:40px 0 64px}
.etiket{display:inline-block;font-size:13px;font-weight:600;color:var(--vurgu);background:var(--vurgu-acik);
  padding:5px 12px;border-radius:99px;margin-bottom:18px}
h1{font-size:clamp(34px,5vw,54px);line-height:1.08;letter-spacing:-.02em;margin:0 0 18px;font-weight:800}
h1 em{font-style:normal;color:var(--vurgu)}
.giris-metni{font-size:18px;color:var(--soluk);max-width:520px;margin:0 0 28px}
.hero nav{display:flex;gap:12px;flex-wrap:wrap}

.cizelge{background:var(--kart);border:1px solid var(--cizgi);border-radius:18px;padding:18px;
  box-shadow:0 20px 50px -25px rgba(27,34,50,.35)}
.cizelge-baslik{display:flex;justify-content:space-between;font-size:13px;color:var(--soluk);margin-bottom:12px}
.izgara{display:grid;grid-template-columns:44px repeat(3,1fr);grid-template-rows:24px repeat(5,44px);gap:4px;font-size:12px}
.izgara .gun{text-align:center;font-weight:600;color:var(--soluk)}
.izgara .saat{color:var(--soluk);font-variant-numeric:tabular-nums;padding-top:2px}
.izgara .hucre{background:#faf9f6;border-radius:6px}
.blok{border-radius:8px;padding:6px 8px;font-weight:600;font-size:12px;position:relative;z-index:1}
.blok small{display:block;font-weight:500;opacity:.8}
.b1{background:var(--vurgu-acik);color:var(--vurgu);border-left:3px solid var(--vurgu)}
.b2{background:#e7f5ee;color:var(--yesil);border-left:3px solid var(--yesil)}
.b3{background:var(--uyari-acik);color:var(--uyari);border-left:3px solid var(--uyari);margin-left:14px;
  box-shadow:0 6px 16px -8px rgba(212,71,47,.6)}
.cakisma-notu{margin-top:12px;display:flex;gap:8px;align-items:flex-start;font-size:13px;
  background:var(--uyari-acik);color:#8f2b18;padding:10px 12px;border-radius:10px}

.ozellikler{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;padding-bottom:56px}
.ozellik{background:var(--kart);border:1px solid var(--cizgi);border-radius:14px;padding:20px}
.ozellik b{display:block;margin:10px 0 6px}
.ozellik p{margin:0;color:var(--soluk);font-size:14px}
.ozellik .no{font-size:12px;font-weight:700;color:var(--soluk);letter-spacing:.08em}
.ozellik.yakinda{background:transparent;border-style:dashed}

.adimlar{border-top:1px solid var(--cizgi);padding:44px 0 56px;display:grid;grid-template-columns:240px 1fr;gap:32px}
.adimlar h2{margin:0;font-size:24px;letter-spacing:-.01em}
.adimlar ol{margin:0;padding:0;list-style:none;display:grid;grid-template-columns:repeat(3,1fr);gap:24px;counter-reset:a}
.adimlar li{counter-increment:a;color:var(--soluk);font-size:15px}
.adimlar li::before{content:counter(a);display:grid;place-items:center;width:30px;height:30px;border-radius:50%;
  background:var(--murekkep);color:#fff;font-weight:700;font-size:14px;margin-bottom:10px}
.adimlar li b{display:block;color:var(--murekkep);margin-bottom:4px}
footer{border-top:1px solid var(--cizgi);padding:22px 0 30px;color:var(--soluk);font-size:13px;
  display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}

/* ---- Giriş / kayıt ---- */
.form-kap{min-height:calc(100vh - 90px);display:grid;place-items:center;padding:20px 0 60px}
.form-kart{width:100%;max-width:420px;background:var(--kart);border:1px solid var(--cizgi);border-radius:18px;
  padding:32px;box-shadow:0 20px 50px -30px rgba(27,34,50,.35)}
.form-kart h1{font-size:28px;margin-bottom:6px}
.form-kart .alt{color:var(--soluk);margin:0 0 24px}
label{display:block;font-weight:600;font-size:14px;margin:14px 0 6px}
input{width:100%;padding:12px 14px;border:1.5px solid var(--cizgi);border-radius:10px;font:inherit;background:#fff}
input:focus{outline:none;border-color:var(--vurgu);box-shadow:0 0 0 3px var(--vurgu-acik)}
.form-kart .dugme{width:100%;margin-top:22px;padding:13px}
.hata{background:var(--uyari-acik);color:#8f2b18;padding:10px 12px;border-radius:10px;font-size:14px;margin-bottom:6px}
.test{margin-top:22px;padding:14px;border-radius:10px;background:var(--zemin);font-size:13px;color:var(--soluk)}
.test code{background:#fff;border:1px solid var(--cizgi);padding:1px 6px;border-radius:5px;color:var(--murekkep)}
.form-kart .gecis{text-align:center;margin:18px 0 0;font-size:14px;color:var(--soluk)}

@media (max-width:860px){
  .hero{grid-template-columns:1fr;gap:32px;padding-top:16px}
  .ozellikler{grid-template-columns:1fr 1fr}
  .adimlar{grid-template-columns:1fr}
  .adimlar ol{grid-template-columns:1fr}
}
@media (max-width:520px){
  .ozellikler{grid-template-columns:1fr}
  .ust nav .dugme:not(.dolu){display:none}
}
</style></head>
<body><div class="kap">
<header class="ust">
  <a class="logo" href="/"><i>◷</i>Akıllı Ders Programı</a>
  <nav><a class="dugme" href="/giris">Giriş Yap</a><a class="dugme dolu" href="/kayit">Kayıt Ol</a></nav>
</header>
"""

KAMU_SON = "</div></body></html>"


ANA_SAYFA = """
<section class="hero">
  <div>
    <span class="etiket">Bingöl Üniversitesi · Öğrenci ders planlama aracı</span>
    <h1>Ders programını kur,<br><em>çakışmaları</em> biz yakalayalım.</h1>
    <p class="giris-metni">Açılan dersleri ve şubeleri tek yerde gör, haftalık programını birkaç tıklamayla
      oluştur. Saatleri çakışan dersler eklenmeden önce uyarılırsın; programını kaydedip
      bağlantıyla paylaşabilirsin.</p>
    <nav>
      <a class="dugme dolu" href="/kayit">Ücretsiz kayıt ol</a>
      <a class="dugme" href="/giris">Hesabım var, giriş yap</a>
    </nav>
  </div>

  <div class="cizelge" aria-label="Örnek haftalık program ve çakışma uyarısı">
    <div class="cizelge-baslik"><b>Haftalık programım</b><span>2026-Güz · 16 AKTS</span></div>
    <div class="izgara">
      <span></span><span class="gun">Pzt</span><span class="gun">Sal</span><span class="gun">Çar</span>
      <span class="saat">09:00</span>
      <div class="blok b1" style="grid-column:2;grid-row:2/span 2">BIL101<small>09:00–11:00</small></div>
      <span class="hucre" style="grid-column:3;grid-row:2"></span>
      <span class="hucre" style="grid-column:4;grid-row:2"></span>
      <span class="saat">10:00</span>
      <span class="hucre" style="grid-column:3;grid-row:3"></span>
      <span class="hucre" style="grid-column:4;grid-row:3"></span>
      <span class="saat">11:00</span>
      <span class="hucre" style="grid-column:3;grid-row:4"></span>
      <div class="blok b2" style="grid-column:4;grid-row:4/span 2">FIZ101<small>11:00–13:00</small></div>
      <span class="saat">12:00</span>
      <span class="hucre" style="grid-column:2;grid-row:5"></span>
      <span class="hucre" style="grid-column:3;grid-row:5"></span>
      <span class="saat">13:00</span>
      <span class="hucre" style="grid-column:2;grid-row:6"></span>
      <span class="hucre" style="grid-column:3;grid-row:6"></span>
      <span class="hucre" style="grid-column:4;grid-row:6"></span>
      <div class="blok b3" style="grid-column:2;grid-row:3/span 2">MAT101<small>10:00–12:00</small></div>
    </div>
    <div class="cakisma-notu"><span>⚠</span><span><b>Kısmi çakışma:</b> BIL101 ile MAT101
      Pazartesi 10:00–11:00 arasında 60 dakika çakışıyor.</span></div>
  </div>
</section>

<section class="ozellikler">
  <div class="ozellik"><span class="no">01</span><b>Ders kataloğu</b>
    <p>Tüm derslerin şubeleri, öğretim elemanı, gün-saat ve AKTS bilgisiyle.</p></div>
  <div class="ozellik"><span class="no">02</span><b>Program oluşturucu</b>
    <p>Haftalık tablo, AKTS sınırı ve aynı dersi iki kez almayı engelleyen kurallar.</p></div>
  <div class="ozellik"><span class="no">03</span><b>Çakışma tespiti</b>
    <p>Tam, kapsayan ve kısmi çakışmaları ortak saat aralığıyla gösterir.</p></div>
  <div class="ozellik yakinda"><span class="no">04 · YAKINDA</span><b>Seçmeli ders önerisi</b>
    <p>İlgi alanlarına göre uygun seçmeli derslerin önerilmesi.</p></div>
</section>

<section class="adimlar">
  <h2>Üç adımda hazır</h2>
  <ol>
    <li><b>Hesap oluştur</b>Öğrenci hesabınla giriş yap; parolan şifrelenerek saklanır.</li>
    <li><b>Dersleri seç</b>Katalogdan şubeleri ekle, çakışan dersler anında işaretlensin.</li>
    <li><b>Kaydet ve paylaş</b>Çakışmasız programını kaydet, bağlantısını arkadaşlarınla paylaş.</li>
  </ol>
</section>

<footer>
  <span>Bilgisayar Uygulamaları I · Proje P18 — Akıllı Ders Programı ve Seçmeli Ders Öneri Sistemi</span>
  <span>Flask · SQLite · Render</span>
</footer>
"""


GIRIS_SAYFASI = """
<div class="form-kap"><div class="form-kart">
  <h1>Tekrar hoş geldin</h1>
  <p class="alt">Ders programına devam etmek için giriş yap.</p>
  {% if mesaj %}<div class="hata">{{ mesaj }}</div>{% endif %}
  <form method="POST">
    <label for="k">Kullanıcı adı</label>
    <input id="k" type="text" name="kullanici_adi" autocomplete="username" required>
    <label for="p">Şifre</label>
    <input id="p" type="password" name="parola" autocomplete="current-password" required>
    <button class="dugme dolu" type="submit">Giriş yap</button>
  </form>
  <div class="test"><b>Test hesapları</b><br>
    Öğrenci: <code>ogrenci</code> / <code>123456</code><br>
    Yönetici: <code>admin</code> / <code>admin123</code></div>
  <p class="gecis">Hesabın yok mu? <a href="/kayit">Kayıt ol</a></p>
</div></div>
"""


KAYIT_SAYFASI = """
<div class="form-kap"><div class="form-kart">
  <h1>Hesap oluştur</h1>
  <p class="alt">Öğrenci hesabınla ders programını oluşturmaya başla.</p>
  {% if mesaj %}<div class="hata">{{ mesaj }}</div>{% endif %}
  <form method="POST">
    <label for="k">Kullanıcı adı</label>
    <input id="k" type="text" name="kullanici_adi" autocomplete="username" required>
    <label for="e">E-posta</label>
    <input id="e" type="email" name="eposta" autocomplete="email" required>
    <label for="p">Şifre</label>
    <input id="p" type="password" name="parola" autocomplete="new-password" minlength="6" required>
    <button class="dugme dolu" type="submit">Kayıt ol</button>
  </form>
  <p class="gecis">Zaten hesabın var mı? <a href="/giris">Giriş yap</a></p>
</div></div>
"""


# =====================================================================
# Giriş yapılmış kullanıcı sayfaları (panel, ders kataloğu, yönetim ...)
# =====================================================================

UYGULAMA_SABLON = """<!doctype html>
<html lang="tr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ baslik }} · Akıllı Ders Programı</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root{
  --zemin:#f6f4ef; --kart:#ffffff; --murekkep:#1b2232; --soluk:#5d6577; --cizgi:#e4e0d6; --hafif:#faf9f6;
  --vurgu:#2f4bd8; --vurgu-acik:#e8ecfd; --uyari:#d4472f; --uyari-acik:#fdeae6;
  --yesil:#1f8a5b; --yesil-acik:#e7f5ee; --sari:#a86a00; --sari-acik:#fdf3df;
}
*{box-sizing:border-box}
body{margin:0;background:var(--zemin);color:var(--murekkep);
  font-family:"Plus Jakarta Sans",system-ui,"Segoe UI",sans-serif;line-height:1.5;font-size:15px}
a{color:var(--vurgu)}
.kap{max-width:1160px;margin:0 auto;padding:0 20px 60px}

/* Üst menü */
.ust{background:var(--kart);border-bottom:1px solid var(--cizgi);position:sticky;top:0;z-index:10}
.ust .ic{max-width:1160px;margin:0 auto;padding:12px 20px;display:flex;align-items:center;gap:24px}
.logo{display:flex;align-items:center;gap:10px;font-weight:800;text-decoration:none;color:var(--murekkep);white-space:nowrap}
.logo i{width:28px;height:28px;border-radius:8px;background:var(--murekkep);display:grid;place-items:center;color:#fff;font-style:normal;font-size:14px}
.menu{display:flex;gap:4px;flex:1;overflow-x:auto}
.menu a{padding:8px 12px;border-radius:8px;text-decoration:none;color:var(--soluk);font-weight:600;white-space:nowrap}
.menu a:hover{background:var(--hafif);color:var(--murekkep)}
.menu a.aktif{background:var(--vurgu-acik);color:var(--vurgu)}
.kullanici{display:flex;align-items:center;gap:10px;white-space:nowrap}
.avatar{width:32px;height:32px;border-radius:50%;background:var(--vurgu);color:#fff;display:grid;place-items:center;font-weight:700;text-transform:uppercase}
.kullanici small{display:block;color:var(--soluk);font-size:12px;line-height:1.1}
.kullanici b{display:block;line-height:1.2}

/* Başlık alanı */
.sayfa-bas{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;flex-wrap:wrap;padding:28px 0 20px}
.sayfa-bas h1{margin:0;font-size:28px;letter-spacing:-.02em}
.sayfa-bas p{margin:4px 0 0;color:var(--soluk)}

/* Bileşenler */
.dugme{display:inline-flex;align-items:center;gap:6px;padding:9px 16px;border-radius:9px;font:inherit;font-weight:600;
  text-decoration:none;border:1.5px solid var(--cizgi);background:var(--kart);color:var(--murekkep);cursor:pointer;white-space:nowrap}
.dugme:hover{border-color:var(--murekkep)}
.dugme.dolu{background:var(--murekkep);border-color:var(--murekkep);color:#fff}
.dugme.dolu:hover{background:#000}
.dugme.kucuk{padding:5px 10px;font-size:13px;border-radius:7px}
.dugme.tehlike{color:var(--uyari)}
.dugme.tehlike:hover{border-color:var(--uyari);background:var(--uyari-acik)}
.dugme.ekle{color:var(--vurgu);border-color:var(--vurgu-acik);background:var(--vurgu-acik)}
.dugme.ekle:hover{border-color:var(--vurgu)}
.dugme[disabled]{opacity:.5;cursor:not-allowed}
form.satir{display:inline}
.kart{background:var(--kart);border:1px solid var(--cizgi);border-radius:14px;padding:20px;margin-bottom:20px}
.kart h2{margin:0 0 4px;font-size:18px}
.kart .alt{margin:0 0 16px;color:var(--soluk);font-size:14px}
.kart-bas{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:14px}
.kart-bas h2{margin:0}
.rozet{display:inline-flex;align-items:center;gap:5px;font-size:12px;font-weight:600;padding:3px 9px;border-radius:99px;
  background:var(--hafif);color:var(--soluk);border:1px solid var(--cizgi)}
.rozet.yesil{background:var(--yesil-acik);color:var(--yesil);border-color:transparent}
.rozet.kirmizi{background:var(--uyari-acik);color:var(--uyari);border-color:transparent}
.rozet.sari{background:var(--sari-acik);color:var(--sari);border-color:transparent}
.rozet.mavi{background:var(--vurgu-acik);color:var(--vurgu);border-color:transparent}

.bildirim{padding:12px 14px;border-radius:10px;margin:0 0 12px;font-size:14px;border:1px solid transparent}
.bildirim.hata{background:var(--uyari-acik);color:#8f2b18}
.bildirim.uyari{background:var(--sari-acik);color:#7a4d00}
.bildirim.basari{background:var(--yesil-acik);color:#145c3c}
.bildirim ul{margin:6px 0 0;padding-left:18px}

/* İstatistikler */
.istatistik{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px}
.istatistik > div{background:var(--kart);border:1px solid var(--cizgi);border-radius:14px;padding:16px 18px}
.istatistik small{color:var(--soluk);font-weight:600;font-size:12px;letter-spacing:.04em;text-transform:uppercase}
.istatistik b{display:block;font-size:26px;letter-spacing:-.02em;margin-top:4px}
.istatistik b span{font-size:15px;color:var(--soluk);font-weight:500}
.cubuk{height:6px;background:var(--hafif);border-radius:99px;margin-top:10px;overflow:hidden}
.cubuk i{display:block;height:100%;background:var(--vurgu);border-radius:99px}

/* Panel kısayolları */
.kisayollar{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.kisayol{display:block;background:var(--kart);border:1px solid var(--cizgi);border-radius:14px;padding:20px;text-decoration:none;color:inherit}
.kisayol:hover{border-color:var(--murekkep);transform:translateY(-1px)}
.kisayol .ikon{width:38px;height:38px;border-radius:10px;display:grid;place-items:center;font-size:18px;background:var(--vurgu-acik);margin-bottom:12px}
.kisayol b{display:block;margin-bottom:4px}
.kisayol p{margin:0;color:var(--soluk);font-size:14px}

/* Tablolar */
.tablo-kap{overflow-x:auto;margin:0 -20px;padding:0 20px}
table{border-collapse:collapse;width:100%;font-size:14px}
th{text-align:left;font-size:12px;letter-spacing:.04em;text-transform:uppercase;color:var(--soluk);font-weight:600;
  padding:10px 12px;border-bottom:1px solid var(--cizgi);white-space:nowrap}
td{padding:12px;border-bottom:1px solid var(--cizgi);vertical-align:middle}
tr:last-child td{border-bottom:0}
tbody tr:hover td{background:var(--hafif)}
tr.cakisan td{background:var(--uyari-acik)}
td .kod{font-weight:700}
td .ikincil{display:block;color:var(--soluk);font-size:13px}
.sag{text-align:right}
.bos{color:var(--soluk);text-align:center;padding:28px}

/* Haftalık zaman ızgarası */
.izgara{display:grid;grid-template-columns:52px repeat(5,minmax(110px,1fr));grid-auto-rows:24px;position:relative;min-width:640px}
.izgara .gun{grid-row:1;text-align:center;font-weight:700;font-size:13px;color:var(--soluk);padding-top:2px}
.izgara .saat{grid-column:1;font-size:12px;color:var(--soluk);font-variant-numeric:tabular-nums;transform:translateY(-8px)}
.izgara .zemin{border-top:1px solid var(--cizgi)}
.izgara .zemin.yarim{border-top:1px dashed #efece4}
.blok{margin:2px 3px;min-width:0;border-radius:8px;padding:5px 8px;font-size:12px;line-height:1.3;overflow:hidden;z-index:1;
  background:var(--vurgu-acik);color:var(--vurgu);border-left:3px solid var(--vurgu)}
.blok b{display:block;font-size:13px}
.blok.cakisan{background:var(--uyari-acik);color:var(--uyari);border-left-color:var(--uyari);box-shadow:0 6px 16px -10px rgba(212,71,47,.7)}

/* Formlar */
.form-izgara{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));align-items:end}
label{display:block;font-weight:600;font-size:13px;margin-bottom:5px}
input,select{width:100%;padding:9px 11px;border:1.5px solid var(--cizgi);border-radius:9px;font:inherit;background:#fff;color:var(--murekkep)}
input:focus,select:focus{outline:none;border-color:var(--vurgu);box-shadow:0 0 0 3px var(--vurgu-acik)}
.arama{max-width:260px}
.iki-kolon{display:grid;grid-template-columns:1fr 1fr;gap:20px}

.paylas-kutu{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:14px;padding:12px;background:var(--hafif);border-radius:10px;font-size:14px}
.paylas-kutu input{flex:1;min-width:200px;background:#fff}

@media (max-width:860px){
  .istatistik{grid-template-columns:1fr 1fr}
  .kisayollar,.iki-kolon{grid-template-columns:1fr}
  .kullanici div{display:none}
  .ust .ic{gap:12px}
  .logo span{display:none}
}
</style></head>
<body>
<header class="ust"><div class="ic">
  <a class="logo" href="/"><i>◷</i><span>Akıllı Ders Programı</span></a>
  {% if session.get('kullanici_id') %}
  <nav class="menu">
    <a href="/panel" class="{{ 'aktif' if aktif == 'panel' }}">Panel</a>
    <a href="/dersler" class="{{ 'aktif' if aktif == 'dersler' }}">Ders Programım</a>
    {% if session.get('rol') == 'yonetici' %}<a href="/yonetici/katalog" class="{{ 'aktif' if aktif == 'katalog' }}">Katalog Yönetimi</a>{% endif %}
  </nav>
  <div class="kullanici">
    <span class="avatar">{{ session.get('kullanici_adi', '?')[:1] }}</span>
    <div><b>{{ session.get('kullanici_adi') }}</b><small>{{ 'Yönetici' if session.get('rol') == 'yonetici' else 'Öğrenci' }}</small></div>
    <a class="dugme kucuk" href="/cikis">Çıkış</a>
  </div>
  {% else %}
  <nav class="menu"></nav>
  <a class="dugme" href="/giris">Giriş Yap</a><a class="dugme dolu" href="/kayit">Kayıt Ol</a>
  {% endif %}
</div></header>
<main class="kap">
{% with mesajlar = get_flashed_messages(with_categories=true) %}
  {% if mesajlar %}<div style="padding-top:20px">{% for kat, m in mesajlar %}<div class="bildirim {{ kat }}">{{ m }}</div>{% endfor %}</div>{% endif %}
{% endwith %}
"""

UYGULAMA_SON = "</main></body></html>"


# Haftalık ızgara: app.py'deki haftalik_izgara() fonksiyonunun çıktısını çizer
IZGARA = """
<div class="tablo-kap"><div class="izgara" style="grid-template-rows:28px repeat({{ iz.satir }},24px)">
  {% for g in iz.gunler %}<div class="gun" style="grid-column:{{ loop.index + 1 }}">{{ g }}</div>{% endfor %}
  {% for s in iz.saatler %}
    <div class="saat" style="grid-row:{{ s.satir }}">{{ s.etiket }}</div>
    <div class="zemin" style="grid-column:2/-1;grid-row:{{ s.satir }}"></div>
    <div class="zemin yarim" style="grid-column:2/-1;grid-row:{{ s.satir + 1 }}"></div>
  {% endfor %}
  {% for b in iz.bloklar %}
    <div class="blok {{ 'cakisan' if b.cakisan }}"
         style="grid-column:{{ b.sutun }};grid-row:{{ b.satir }}/span {{ b.uzunluk }};margin-left:calc({{ b.serit }} * 100% / {{ b.serit_sayisi }} + 3px);width:calc(100% / {{ b.serit_sayisi }} - 6px)"
         title="{{ b.DersKodu }} {{ b.DersAdi }} · {{ b.Saat }}–{{ b.BitisSaati }} · {{ b.HocaAdi }}">
      <b>{{ b.DersKodu }}</b>{{ b.Saat }}–{{ b.BitisSaati }}{% if b.uzunluk > 3 %}<br>{{ b.HocaAdi }}{% endif %}
    </div>
  {% endfor %}
</div></div>
"""


PANEL = """
<div class="sayfa-bas">
  <div><h1>Merhaba, {{ session.kullanici_adi }} 👋</h1>
  <p>{{ program.Donem }} dönemi · {{ 'Yönetici hesabı' if session.rol == 'yonetici' else 'Öğrenci hesabı' }}</p></div>
  <a class="dugme dolu" href="/dersler">Ders programıma git →</a>
</div>

<div class="istatistik">
  <div><small>Seçilen ders</small><b>{{ ders_sayisi }}</b></div>
  <div><small>Toplam AKTS</small><b>{{ akts }} <span>/ {{ akts_sinir }}</span></b>
    <div class="cubuk"><i style="width:{{ (akts * 100 / akts_sinir)|round|int }}%"></i></div></div>
  <div><small>Çakışma</small><b style="color:{{ 'var(--uyari)' if cakisma_sayisi else 'var(--yesil)' }}">{{ cakisma_sayisi }}</b></div>
  <div><small>Program durumu</small><b style="font-size:18px;margin-top:10px">
    {% if program.Kaydedildi %}<span class="rozet yesil">✓ Kaydedildi</span>{% else %}<span class="rozet sari">Taslak</span>{% endif %}</b></div>
</div>

{% if cakisma_sayisi %}
<div class="bildirim hata">Programınızda {{ cakisma_sayisi }} saat çakışması var. Kaydetmeden önce
  <a href="/dersler">ders programınızdan</a> çakışan derslerden birini kaldırın.</div>
{% endif %}

<div class="kart">
  <div class="kart-bas"><h2>Bu haftaki programım</h2><a class="dugme kucuk" href="/dersler">Düzenle</a></div>
  {% if ders_sayisi %}""" + IZGARA + """{% else %}
  <p class="bos">Henüz ders seçmediniz. <a href="/dersler">Katalogdan ders ekleyin →</a></p>{% endif %}
</div>

<div class="kisayollar">
  <a class="kisayol" href="/dersler"><div class="ikon">📚</div><b>Ders kataloğu</b>
    <p>Açık dersleri ve şubeleri incele, programına ekle.</p></a>
  {% if program.Kaydedildi and program.PaylasimKodu %}
  <a class="kisayol" href="/paylas/{{ program.PaylasimKodu }}"><div class="ikon" style="background:var(--yesil-acik)">🔗</div><b>Paylaşım sayfası</b>
    <p>Kaydettiğin programın herkese açık, salt okunur görünümü.</p></a>
  {% else %}
  <div class="kisayol" style="opacity:.6"><div class="ikon" style="background:var(--hafif)">🔗</div><b>Paylaşım sayfası</b>
    <p>Programını kaydettiğinde paylaşım bağlantısı burada görünür.</p></div>
  {% endif %}
  {% if session.rol == 'yonetici' %}
  <a class="kisayol" href="/yonetici/katalog"><div class="ikon" style="background:var(--sari-acik)">🛠</div><b>Katalog yönetimi</b>
    <p>{{ yonetici.ders }} ders, {{ yonetici.sube }} şube, {{ yonetici.kullanici }} kullanıcı. Ders ve şube ekle/sil.</p></a>
  {% else %}
  <div class="kisayol" style="opacity:.6"><div class="ikon" style="background:var(--hafif)">✨</div><b>Seçmeli ders önerisi</b>
    <p>Yakında: ilgi alanlarına göre seçmeli ders önerileri.</p></div>
  {% endif %}
</div>
"""


DERSLER = """
<div class="sayfa-bas">
  <div><h1>Ders programım</h1>
  <p>{{ program.Donem }} · {{ secilenler|length }} ders · {{ toplam_akts }} / {{ akts_sinir }} AKTS ·
    {% if program.Kaydedildi %}<span class="rozet yesil">✓ Kaydedildi</span>{% else %}<span class="rozet sari">Taslak</span>{% endif %}</p></div>
  <form class="satir" method="post" action="/program/kaydet">
    <button class="dugme dolu" {{ 'disabled title="Önce çakışmaları giderin"' if cakismalar }}>💾 Programı kaydet</button></form>
</div>

{% if cakismalar %}
<div class="bildirim hata"><b>⚠ Programınızda {{ cakismalar|length }} çakışma var — bu hâliyle kaydedilemez.</b>
  <ul>{% for c in cakismalar %}
    <li>{{ c.a.DersKodu }} ({{ c.a.Gun }} {{ c.a.Baslangic }}–{{ c.a.Bitis }}) ↔ {{ c.b.DersKodu }} ({{ c.b.Baslangic }}–{{ c.b.Bitis }}):
      <b>{{ c.tur_aciklama }}</b>, ortak aralık {{ c.ortak_aralik }} ({{ c.dakika }} dk)</li>
  {% endfor %}</ul></div>
{% endif %}

<div class="kart">
  <div class="kart-bas"><h2>Haftalık görünüm</h2>
    <span>{% if cakismalar %}<span class="rozet kirmizi">Çakışan ders</span> {% endif %}<span class="rozet mavi">Seçili ders</span></span></div>
  {% if secilenler %}""" + IZGARA + """{% else %}<p class="bos">Henüz programa ders eklenmedi. Aşağıdaki katalogdan seçim yapın.</p>{% endif %}

  {% if secilenler %}
  <div class="tablo-kap" style="margin-top:18px"><table>
    <thead><tr><th>Ders</th><th>Öğretim elemanı</th><th>Gün / saat</th><th>AKTS</th><th></th></tr></thead>
    <tbody>{% for p in secilenler %}
    <tr class="{{ 'cakisan' if p.SubeId in cakisan_ids }}">
      <td><span class="kod">{{ p.DersKodu }}</span><span class="ikincil">{{ p.DersAdi }}</span></td>
      <td>{{ p.HocaAdi }}</td><td>{{ p.Gun }} {{ p.Saat }}–{{ p.BitisSaati }}</td><td>{{ p.AKTS }}</td>
      <td class="sag"><form class="satir" method="post" action="/program/sil/{{ p.KayitId }}">
        <button class="dugme kucuk tehlike">Kaldır</button></form></td>
    </tr>{% endfor %}</tbody>
  </table></div>
  {% endif %}

  {% if program.Kaydedildi and program.PaylasimKodu %}
  <div class="paylas-kutu">🔗 <b>Paylaşım bağlantısı</b>
    <input id="plink" readonly value="{{ request.host_url }}paylas/{{ program.PaylasimKodu }}" onclick="this.select()">
    <button class="dugme kucuk" type="button" onclick="navigator.clipboard.writeText(document.getElementById('plink').value);this.textContent='Kopyalandı ✓'">Kopyala</button>
    <a class="dugme kucuk" href="/paylas/{{ program.PaylasimKodu }}" target="_blank">Aç ↗</a>
  </div>
  {% endif %}
</div>

<div class="kart">
  <div class="kart-bas"><div><h2>Açık dersler kataloğu</h2>
    <p class="alt" style="margin:0">Çakışacak şubeler eklemeden önce işaretlenir.</p></div>
    <input class="arama" id="ara" placeholder="Ders, kod veya hoca ara…" oninput="
      var q=this.value.toLocaleLowerCase('tr');
      document.querySelectorAll('#katalog tbody tr').forEach(function(r){r.style.display=r.textContent.toLocaleLowerCase('tr').includes(q)?'':'none'})">
  </div>
  <div class="tablo-kap"><table id="katalog">
    <thead><tr><th>Ders</th><th>Öğretim elemanı</th><th>Gün / saat</th><th>AKTS</th><th class="sag">Durum</th></tr></thead>
    <tbody>{% for k in katalog %}
    <tr>
      <td><span class="kod">{{ k.DersKodu }}</span><span class="ikincil">{{ k.DersAdi }}</span></td>
      <td>{{ k.HocaAdi }}</td><td>{{ k.Gun }} {{ k.Saat }}–{{ k.BitisSaati }}</td><td>{{ k.AKTS }}</td>
      <td class="sag">
        {% if k.secili %}<span class="rozet yesil">✓ Programda</span>
        {% elif k.ders_secili %}<span class="rozet">Başka şubesi seçili</span>
        {% else %}
          {% if k.cakisma %}<span class="rozet kirmizi" title="{{ k.cakisma[0].tur_aciklama }}, {{ k.cakisma[0].ortak_aralik }}">⚠ {{ k.cakisma[0].b.DersKodu }} ile çakışır</span>{% endif %}
          <form class="satir" method="post" action="/program/ekle/{{ k.SubeId }}"><button class="dugme kucuk ekle">+ Ekle</button></form>
        {% endif %}
      </td>
    </tr>{% endfor %}</tbody>
  </table></div>
</div>
"""


CAKISMA_UYARISI = """
<div style="max-width:620px;margin:40px auto">
<div class="kart" style="border-color:#f3c6bc">
  <span class="rozet kirmizi">⚠ Çakışma uyarısı</span>
  <h1 style="font-size:24px;margin:12px 0 6px">{{ y.DersKodu }} programınızla çakışıyor</h1>
  <p style="color:var(--soluk);margin:0 0 16px">{{ y.DersAdi }} · {{ y.Gun }} {{ y.Saat }}–{{ y.BitisSaati }} · {{ y.HocaAdi }}</p>
  {% for c in cakismalar %}
  <div class="bildirim hata" style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap">
    <span><b>{{ c.b.DersKodu }}</b> {{ c.b.DersAdi }} ({{ c.b.Baslangic }}–{{ c.b.Bitis }})</span>
    <span><b>{{ c.tur_aciklama }}</b> · {{ c.ortak_aralik }} · {{ c.dakika }} dk</span>
  </div>
  {% endfor %}
  <p style="font-size:14px;color:var(--soluk)">Çakışan derslerle program <b>kaydedilemez</b>. Yine de taslağa ekleyip
    sonra hangisini bırakacağınıza karar verebilirsiniz.</p>
  <div style="display:flex;gap:10px;margin-top:16px">
    <a class="dugme dolu" href="/dersler">Vazgeç</a>
    <form class="satir" method="post"><input type="hidden" name="zorla" value="1"><button class="dugme tehlike">Yine de ekle</button></form>
  </div>
</div></div>
"""


PAYLAS = """
<div class="sayfa-bas">
  <div><span class="rozet mavi">Paylaşılan program · salt okunur</span>
  <h1 style="margin-top:10px">{{ program.Donem }} ders programı</h1>
  <p>{{ dersler|length }} ders · {{ akts }} AKTS</p></div>
</div>
<div class="kart">""" + IZGARA + """</div>
<div class="kart"><div class="tablo-kap"><table>
  <thead><tr><th>Ders</th><th>Öğretim elemanı</th><th>Gün / saat</th><th>AKTS</th></tr></thead>
  <tbody>{% for d in dersler %}<tr><td><span class="kod">{{ d.DersKodu }}</span><span class="ikincil">{{ d.DersAdi }}</span></td>
    <td>{{ d.HocaAdi }}</td><td>{{ d.Gun }} {{ d.Saat }}–{{ d.BitisSaati }}</td><td>{{ d.AKTS }}</td></tr>{% endfor %}</tbody>
</table></div></div>
"""


KATALOG_YONETIMI = """
<div class="sayfa-bas">
  <div><h1>Katalog yönetimi</h1><p>{{ dersler|length }} ders · {{ subeler|length }} şube · yalnızca yöneticiler</p></div>
</div>

<div class="iki-kolon">
  <div class="kart"><h2>Yeni ders</h2><p class="alt">Kod 3–10 harf/rakam, Kredi 1–10, AKTS 1–15.</p>
    <form method="post"><input type="hidden" name="islem" value="ders_ekle">
      <div class="form-izgara">
        <div><label>Ders kodu</label><input name="kod" placeholder="BIL201" required></div>
        <div style="grid-column:span 2"><label>Ders adı</label><input name="ad" placeholder="Veri Yapıları" required></div>
        <div><label>Kredi</label><input name="kredi" type="number" min="1" max="10" required></div>
        <div><label>AKTS</label><input name="akts" type="number" min="1" max="15" required></div>
        <div><button class="dugme dolu" style="width:100%;justify-content:center">Ders ekle</button></div>
      </div></form></div>

  <div class="kart"><h2>Yeni şube</h2><p class="alt">08:00–22:00 arası; aynı hoca aynı saatte iki şubeye atanamaz.</p>
    <form method="post"><input type="hidden" name="islem" value="sube_ekle">
      <div class="form-izgara">
        <div style="grid-column:1/-1"><label>Ders</label><select name="ders_id">{% for d in dersler %}<option value="{{ d.Id }}">{{ d.DersKodu }} — {{ d.DersAdi }}</option>{% endfor %}</select></div>
        <div style="grid-column:1/-1"><label>Öğretim elemanı</label><input name="hoca" placeholder="Dr. Ad Soyad" required></div>
        <div><label>Gün</label><select name="gun">{% for g in gunler %}<option>{{ g }}</option>{% endfor %}</select></div>
        <div><label>Başlangıç</label><input name="bas" type="time" required></div>
        <div><label>Bitiş</label><input name="bit" type="time" required></div>
        <div><button class="dugme dolu" style="width:100%;justify-content:center">Şube ekle</button></div>
      </div></form></div>
</div>

<div class="kart"><h2>Dersler</h2><p class="alt">Şubesi olan ders silinemez; önce şubelerini silin.</p>
  <div class="tablo-kap"><table>
  <thead><tr><th>Kod</th><th>Ders adı</th><th>Kredi</th><th>AKTS</th><th class="sag"></th></tr></thead>
  <tbody>{% for d in dersler %}<tr><td class="kod">{{ d.DersKodu }}</td><td>{{ d.DersAdi }}</td><td>{{ d.Kredi }}</td><td>{{ d.AKTS }}</td>
    <td class="sag"><form class="satir" method="post"><input type="hidden" name="islem" value="ders_sil"><input type="hidden" name="id" value="{{ d.Id }}">
      <button class="dugme kucuk tehlike">Sil</button></form></td></tr>{% endfor %}</tbody>
  </table></div></div>

<div class="kart"><h2>Şubeler</h2><p class="alt">Bir öğrencinin programında kullanılan şube silinemez.</p>
  <div class="tablo-kap"><table>
  <thead><tr><th>Ders</th><th>Öğretim elemanı</th><th>Gün / saat</th><th class="sag"></th></tr></thead>
  <tbody>{% for s in subeler %}<tr><td><span class="kod">{{ s.DersKodu }}</span><span class="ikincil">{{ s.DersAdi }}</span></td>
    <td>{{ s.HocaAdi }}</td><td>{{ s.Gun }} {{ s.Saat }}–{{ s.BitisSaati }}</td>
    <td class="sag"><form class="satir" method="post"><input type="hidden" name="islem" value="sube_sil"><input type="hidden" name="id" value="{{ s.SubeId }}">
      <button class="dugme kucuk tehlike">Sil</button></form></td></tr>{% endfor %}</tbody>
  </table></div></div>
"""


MESAJ_SAYFASI = """
<div style="max-width:520px;margin:60px auto;text-align:center">
<div class="kart" style="padding:36px">
  <div style="font-size:40px">{{ ikon }}</div>
  <h1 style="font-size:24px;margin:8px 0">{{ baslik }}</h1>
  <p style="color:var(--soluk)">{{ aciklama }}</p>
  <a class="dugme dolu" href="/panel" style="margin-top:8px">Panele dön</a>
</div></div>
"""
