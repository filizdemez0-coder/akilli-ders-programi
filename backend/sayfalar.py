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
