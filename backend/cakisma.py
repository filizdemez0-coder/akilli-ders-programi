"""
HAFTA 7 - Çekirdek Modül B: Çakışma Tespiti
--------------------------------------------
Bu modül veritabanından bağımsızdır (saf fonksiyonlar). Böylece hem Flask
uygulaması hem de birim testleri aynı mantığı kullanır.

Veri modeli: Her ders oturumu bir ZAMAN ARALIĞIDIR -> (gun, baslangic, bitis)
    - gun        : "Pazartesi" ... "Pazar"
    - baslangic  : "HH:MM"  (dahil)
    - bitis      : "HH:MM"  (hariç)  -> 09:00-10:50 ile 10:50-12:00 ÇAKIŞMAZ

Algoritma (aralık örtüşmesi):
    İki aralık A ve B aynı gündeyse, ancak ve ancak
        A.baslangic < B.bitis  VE  B.baslangic < A.bitis
    ise çakışır. Örtüşme süresi = min(bitisler) - max(baslangiclar).

Programdaki tüm çakışmaları bulmak için oturumlar (gün, başlangıç) sırasına
göre dizilir; her oturum yalnızca kendisinden SONRA başlayan ve henüz bu
oturum bitmeden başlayan oturumlarla karşılaştırılır (sweep-line). Bitmiş
oturumlara bakılmadığı için gereksiz karşılaştırmalar atlanır.
"""

GUNLER = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
EN_ERKEN = "08:00"
EN_GEC = "22:00"


def dakikaya_cevir(saat):
    """'09:30' -> 570. Geçersiz biçimde ValueError fırlatır."""
    if not isinstance(saat, str) or len(saat.strip()) != 5 or saat.strip()[2] != ":":
        raise ValueError(f"Saat 'SS:DD' biçiminde olmalı: {saat!r}")
    ss, dd = saat.strip().split(":")
    if not (ss.isdigit() and dd.isdigit()):
        raise ValueError(f"Saat yalnızca rakam içermeli: {saat!r}")
    ss, dd = int(ss), int(dd)
    if not (0 <= ss <= 23 and 0 <= dd <= 59):
        raise ValueError(f"Geçersiz saat: {saat!r}")
    return ss * 60 + dd


def dakikadan_saate(dakika):
    return f"{dakika // 60:02d}:{dakika % 60:02d}"


def zaman_araligi_dogrula(gun, baslangic, bitis):
    """İş kuralları. Hata mesajlarının listesini döndürür (boşsa geçerli)."""
    hatalar = []
    if gun not in GUNLER:
        hatalar.append(f"Geçersiz gün: {gun!r}")
    try:
        b = dakikaya_cevir(baslangic)
        s = dakikaya_cevir(bitis)
    except ValueError as e:
        hatalar.append(str(e))
        return hatalar
    if b >= s:
        hatalar.append("Başlangıç saati bitiş saatinden önce olmalı.")
    if b < dakikaya_cevir(EN_ERKEN) or s > dakikaya_cevir(EN_GEC):
        hatalar.append(f"Ders saatleri {EN_ERKEN}-{EN_GEC} arasında olmalı.")
    return hatalar


def ortusme_dakikasi(a, b):
    """a ve b: {'Gun','Baslangic','Bitis'} içeren sözlükler. Örtüşme (dk) ya da 0."""
    if a["Gun"] != b["Gun"]:
        return 0
    a1, a2 = dakikaya_cevir(a["Baslangic"]), dakikaya_cevir(a["Bitis"])
    b1, b2 = dakikaya_cevir(b["Baslangic"]), dakikaya_cevir(b["Bitis"])
    return max(0, min(a2, b2) - max(a1, b1))


def cakisiyor_mu(a, b):
    return ortusme_dakikasi(a, b) > 0


def cakisma_turu(a, b):
    """'tam'     : aralıklar birebir aynı
       'kapsama' : biri diğerini tamamen içine alıyor
       'kismi'   : yalnızca bir kısmı örtüşüyor
       None      : çakışma yok"""
    if not cakisiyor_mu(a, b):
        return None
    a1, a2 = dakikaya_cevir(a["Baslangic"]), dakikaya_cevir(a["Bitis"])
    b1, b2 = dakikaya_cevir(b["Baslangic"]), dakikaya_cevir(b["Bitis"])
    if (a1, a2) == (b1, b2):
        return "tam"
    if (a1 <= b1 and b2 <= a2) or (b1 <= a1 and a2 <= b2):
        return "kapsama"
    return "kismi"


TUR_ACIKLAMA = {"tam": "Tam çakışma", "kapsama": "Kapsayan çakışma", "kismi": "Kısmi çakışma"}


def _cakisma_kaydi(a, b):
    tur = cakisma_turu(a, b)
    return {
        "a": a,
        "b": b,
        "tur": tur,
        "tur_aciklama": TUR_ACIKLAMA[tur],
        "dakika": ortusme_dakikasi(a, b),
        "ortak_aralik": (
            dakikadan_saate(max(dakikaya_cevir(a["Baslangic"]), dakikaya_cevir(b["Baslangic"])))
            + "-"
            + dakikadan_saate(min(dakikaya_cevir(a["Bitis"]), dakikaya_cevir(b["Bitis"])))
        ),
    }


def yeni_oturum_cakismalari(yeni, mevcutlar):
    """Programa eklenmek istenen oturumun mevcut oturumlarla çakışmaları."""
    return [_cakisma_kaydi(yeni, m) for m in mevcutlar if cakisiyor_mu(yeni, m)]


def program_cakismalari(oturumlar):
    """Bir programdaki tüm çakışan çiftleri döndürür (sweep-line)."""
    sirali = sorted(
        oturumlar,
        key=lambda o: (GUNLER.index(o["Gun"]) if o["Gun"] in GUNLER else 99,
                       dakikaya_cevir(o["Baslangic"])),
    )
    sonuc = []
    for i, a in enumerate(sirali):
        a_bitis = dakikaya_cevir(a["Bitis"])
        for b in sirali[i + 1:]:
            if b["Gun"] != a["Gun"] or dakikaya_cevir(b["Baslangic"]) >= a_bitis:
                break  # sıralı olduğu için sonrakiler de çakışamaz
            sonuc.append(_cakisma_kaydi(a, b))
    return sonuc
