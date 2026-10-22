# Akıllı Ders Programı ve Seçmeli Ders Öneri Sistemi

## Projenin Amacı
Üniversite öğrencilerinin ders programı oluşturmasını,
ders çakışmalarını tespit etmesini ve ilgi alanlarına
göre seçmeli ders önerileri almasını sağlamak.

## Hedef Kullanıcı
Üniversite öğrencileri.

## Teknolojiler
- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript

## Temel Modüller
- Ders kataloğu
- Program oluşturucu
- Ders çakışma tespiti
- Seçmeli ders önerisi
- Kullanıcı yönetimi
## Hafta 5: Kullanıcı Yönetimi, Kimlik Doğrulama ve Güvenlik Notu
- **Parola Güvenliği:** Kullanıcı parolaları veritabanında kesinlikle düz metin (plain text) olarak saklanmamaktadır. `werkzeug.security` kütüphanesi ile PBKDF2/SHA256 algoritması kullanılarak salt eklenip güvenli şekilde hash'lenmiştir.
- **Oturum Yönetimi:** Giriş yapan kullanıcıların kimlik ve rol bilgileri Flask `session` yapısı ile yönetilmektedir. Kullanıcı çıkış yaptığında oturum tamamen sonlandırılır.
- **Rol Tabanlı Yetkilendirme (RBAC):** Sistemde `ogrenci` ve `yonetici` rolleri tanımlanmıştır. Yönetici gerektiren uç noktalara yetkisiz kullanıcılar erişmek istediğinde HTTP 403 Forbidden engeli uygulanmaktadır.