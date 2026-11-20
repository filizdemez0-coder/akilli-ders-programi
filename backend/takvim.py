"""
HAFTA 9 - Harici API Entegrasyonu: Takvim
-----------------------------------------
İki parçadan oluşur:

1) iCalendar (.ics, RFC 5545) dışa aktarma
   Her şube, dönem boyunca HAFTALIK tekrar eden bir etkinliktir (RRULE:FREQ=WEEKLY;UNTIL=...).
   Dosya Google Takvim, Outlook ve Apple Takvim tarafından içe aktarılabilir; kaydedilmiş programlar
   için verilen abonelik adresi (URL) eklenirse takvim servisi programı kendisi güncel tutar.

2) Resmî tatil API'si (Calendarific - REST, API anahtarı ile kimlik doğrulama)
   Dönem içindeki resmî tatiller çekilir; derse denk gelen günler takvimden çıkarılır (EXDATE).
   - API anahtarı KODDA DEĞİL, ortam değişkeninde: TATIL_API_ANAHTARI
   - Zaman aşımı: istek en fazla ZAMAN_ASIMI saniye bekler, uygulama asılı kalmaz
   - Hız sınırı (rate limit): ücretsiz plan aylık sınırlı istek verir. Sonuçlar yıl bazında
     24 saat önbellekte tutulur; 429 yanıtında Retry-After süresi boyunca API'ye tekrar gidilmez
   - Hata yönetimi: API çalışmazsa takvim YİNE oluşturulur (tatiller çıkarılmadan) ve kullanıcı uyarılır.
     Harici servis, ana işlevi asla durdurmaz.
"""
import json
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone

from cakisma import GUNLER

# 2026-Güz dönemi (akademik takvim). Yeni dönemde yalnızca bu iki satır değişir.
DONEM_BASLANGIC = date(2026, 9, 21)
DONEM_BITIS = date(2026, 12, 31)

API_ADRESI = "https://calendarific.com/api/v2/holidays"
ZAMAN_ASIMI = 5            # saniye
ONBELLEK_SURESI = 24 * 3600
HATA_BEKLEME_SURESI = 300  # başarısız istekten sonra API'ye en erken 5 dk sonra tekrar gidilir

_onbellek = {}             # yil -> (gecerlilik_sonu, tatiller | None, hata | None)
_kilit = threading.Lock()


class TatilApiHatasi(Exception):
    """Kullanıcıya gösterilebilecek, anahtar içermeyen hata mesajı taşır."""


# ---------------------------------------------------------------- Resmî tatil API'si
def _http_get(url):
    """Tek bir GET isteği atar ve JSON döndürür. (Testlerde bu fonksiyon taklit edilir.)"""
    istek = urllib.request.Request(url, headers={"Accept": "application/json",
                                                 "User-Agent": "AkilliDersProgrami/0.10"})
    with urllib.request.urlopen(istek, timeout=ZAMAN_ASIMI) as yanit:
        return json.loads(yanit.read().decode("utf-8"))


def _tatilleri_ayristir(veri):
    """Calendarific yanıtını [(date, ad), ...] listesine çevirir. Beklenmeyen biçimde hata fırlatır."""
    if not isinstance(veri, dict):
        raise TatilApiHatasi("API yanıtı beklenen biçimde değil.")
    kod = (veri.get("meta") or {}).get("code")
    if kod != 200:
        raise TatilApiHatasi(f"API hata kodu döndürdü ({kod}).")
    tatiller = (veri.get("response") or {}).get("holidays")
    if not isinstance(tatiller, list):
        raise TatilApiHatasi("API yanıtında tatil listesi yok.")
    sonuc = []
    for t in tatiller:
        try:
            tur = t.get("type") or []
            if not any("National" in x for x in tur):      # yalnızca resmî (ulusal) tatiller
                continue
            gun = date.fromisoformat(t["date"]["iso"][:10])  # "2026-10-29" veya "2026-10-29T00:00:00+03:00"
            sonuc.append((gun, str(t.get("name", "Resmî tatil"))[:80]))
        except (KeyError, TypeError, ValueError):
            continue                                        # bozuk tek kayıt tüm listeyi düşürmez
    return sorted(set(sonuc))


def resmi_tatiller(yil):
    """Bir yılın resmî tatillerini döndürür. Hata durumunda TatilApiHatasi fırlatır."""
    simdi = time.time()
    with _kilit:
        kayit = _onbellek.get(yil)
        if kayit and kayit[0] > simdi:
            if kayit[2]:
                raise TatilApiHatasi(kayit[2])
            return kayit[1]

    anahtar = os.environ.get("TATIL_API_ANAHTARI", "").strip()
    if not anahtar:
        raise TatilApiHatasi("Tatil API anahtarı tanımlı değil (TATIL_API_ANAHTARI).")

    url = API_ADRESI + "?" + urllib.parse.urlencode({"api_key": anahtar, "country": "TR", "year": yil})
    bekleme = HATA_BEKLEME_SURESI
    try:
        tatiller = _tatilleri_ayristir(_http_get(url))
    except urllib.error.HTTPError as e:
        # Not: hata mesajına URL yazılmaz, çünkü URL API anahtarını içerir.
        e.close()
        if e.code == 429:
            try:
                bekleme = max(int(e.headers.get("Retry-After", HATA_BEKLEME_SURESI)), 60)
            except (TypeError, ValueError):
                pass
            hata = "Tatil API'sinin istek sınırı aşıldı; bir süre sonra tekrar denenecek."
        elif e.code in (401, 403):
            hata = "Tatil API anahtarı geçersiz veya yetkisiz."
        else:
            hata = f"Tatil API'si HTTP {e.code} hatası verdi."
        _hata_kaydet(yil, hata, bekleme)
        raise TatilApiHatasi(hata) from None
    except (urllib.error.URLError, TimeoutError, OSError):
        hata = "Tatil API'sine ulaşılamadı (bağlantı hatası veya zaman aşımı)."
        _hata_kaydet(yil, hata, bekleme)
        raise TatilApiHatasi(hata) from None
    except (ValueError, TatilApiHatasi) as e:      # bozuk JSON / beklenmeyen biçim
        hata = str(e) if isinstance(e, TatilApiHatasi) else "Tatil API'si geçersiz JSON döndürdü."
        _hata_kaydet(yil, hata, bekleme)
        raise TatilApiHatasi(hata) from None

    with _kilit:
        _onbellek[yil] = (time.time() + ONBELLEK_SURESI, tatiller, None)
    return tatiller


def _hata_kaydet(yil, hata, sure):
    with _kilit:
        _onbellek[yil] = (time.time() + sure, None, hata)


def donem_tatilleri(baslangic=DONEM_BASLANGIC, bitis=DONEM_BITIS):
    """Dönem aralığındaki tatiller ve (varsa) hata mesajı: ([(date, ad)], hata | None)."""
    tatiller, hatalar = [], []
    for yil in range(baslangic.year, bitis.year + 1):
        try:
            tatiller += [t for t in resmi_tatiller(yil) if baslangic <= t[0] <= bitis]
        except TatilApiHatasi as e:
            hatalar.append(str(e))
    return tatiller, (hatalar[0] if hatalar else None)


# ---------------------------------------------------------------- iCalendar (.ics) üretimi
def _kacis(metin):
    """RFC 5545 metin kaçışı: ters bölü, noktalı virgül, virgül ve satır sonu."""
    return (str(metin).replace("\\", "\\\\").replace(";", "\\;")
            .replace(",", "\\,").replace("\n", "\\n"))


def _katla(satir):
    """RFC 5545: satırlar 75 baytı geçemez; devam satırı bir boşlukla başlar (UTF-8 karakter bölünmez)."""
    parcalar, mevcut = [], ""
    for ch in satir:
        sinir = 75 if not parcalar else 74
        if len((mevcut + ch).encode("utf-8")) > sinir:
            parcalar.append(mevcut)
            mevcut = ch
        else:
            mevcut += ch
    parcalar.append(mevcut)
    return "\r\n ".join(parcalar)


def ilk_ders_gunu(gun_adi, baslangic=DONEM_BASLANGIC):
    """Dönem başından itibaren dersin yapıldığı ilk tarih (Pazartesi=0 ... Pazar=6)."""
    hedef = GUNLER.index(gun_adi)
    return baslangic + timedelta(days=(hedef - baslangic.weekday()) % 7)


def ders_tarihleri(gun_adi, baslangic=DONEM_BASLANGIC, bitis=DONEM_BITIS):
    gun = ilk_ders_gunu(gun_adi, baslangic)
    while gun <= bitis:
        yield gun
        gun += timedelta(days=7)


def ics_olustur(dersler, takvim_adi, tatiller=(), baslangic=DONEM_BASLANGIC, bitis=DONEM_BITIS,
                uid_on_ek="program"):
    """dersler: DersKodu, DersAdi, HocaAdi, Gun, Saat, BitisSaati, SubeId alanları olan satırlar.
    tatiller: [(date, ad)] - derse denk gelenler EXDATE ile çıkarılır."""
    tatil_gunleri = {t[0] for t in tatiller}
    damga = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    # UNTIL, DTSTART yerel saatle verildiğinde UTC yazılmalıdır. Türkiye: UTC+3 (yaz saati yok).
    until = (datetime.combine(bitis, datetime.max.time()) - timedelta(hours=3)).strftime("%Y%m%dT%H%M%SZ")

    satirlar = [
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Akilli Ders Programi//TR", "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH", f"X-WR-CALNAME:{_kacis(takvim_adi)}", "X-WR-TIMEZONE:Europe/Istanbul",
        "BEGIN:VTIMEZONE", "TZID:Europe/Istanbul", "BEGIN:STANDARD", "DTSTART:19700101T000000",
        "TZOFFSETFROM:+0300", "TZOFFSETTO:+0300", "TZNAME:+03", "END:STANDARD", "END:VTIMEZONE",
    ]
    for d in dersler:
        ilk = ilk_ders_gunu(d["Gun"], baslangic)
        if ilk > bitis:
            continue
        bas = d["Saat"].replace(":", "") + "00"
        son = d["BitisSaati"].replace(":", "") + "00"
        satirlar += [
            "BEGIN:VEVENT",
            f"UID:{uid_on_ek}-sube{d['SubeId']}@akilli-ders-programi",
            f"DTSTAMP:{damga}",
            f"DTSTART;TZID=Europe/Istanbul:{ilk:%Y%m%d}T{bas}",
            f"DTEND;TZID=Europe/Istanbul:{ilk:%Y%m%d}T{son}",
            f"RRULE:FREQ=WEEKLY;UNTIL={until}",
        ]
        cikarilacak = [g for g in ders_tarihleri(d["Gun"], baslangic, bitis) if g in tatil_gunleri]
        if cikarilacak:
            satirlar.append("EXDATE;TZID=Europe/Istanbul:" + ",".join(f"{g:%Y%m%d}T{bas}" for g in cikarilacak))
        satirlar += [
            f"SUMMARY:{_kacis(d['DersKodu'] + ' ' + d['DersAdi'])}",
            f"DESCRIPTION:{_kacis('Öğretim elemanı: ' + d['HocaAdi'])}",
            "END:VEVENT",
        ]
    satirlar.append("END:VCALENDAR")
    return "\r\n".join(_katla(s) for s in satirlar) + "\r\n"


def derse_denk_gelen_tatiller(dersler, tatiller):
    """Arayüzde göstermek için: hangi tatil hangi dersi iptal ediyor?"""
    gunler = {}
    for d in dersler:
        gunler.setdefault(d["Gun"], []).append(d["DersKodu"])
    return [{"tarih": t, "ad": ad, "gun": GUNLER[t.weekday()], "dersler": gunler.get(GUNLER[t.weekday()], [])}
            for t, ad in tatiller]
