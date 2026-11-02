# SDS-07 Risk ve sorun listesi

| Alan | Değer |
|---|---|
| Doküman kimliği | SDS07-RSK |
| Sürüm | 0.1 (Hafta 1) |
| Tarih | 30.10.2026 |
| Hazırlayan | Burak Nigiz (2100002062) |
| İlişkili süreç | ISO/IEC/IEEE 12207:2026 6.3.4 Risk management; ISO 9001:2026 6.1 |

Ölçek: Olasılık ve etki Düşük / Orta / Yüksek. "Sorun" bu hafta gerçekten yaşanmış ve kanıtı olan durumdur; "Risk" henüz gerçekleşmemiştir. Kimlikler kalıcıdır: kapanan kayıt silinmez, yeni kayıt sıradaki numarayı alır. Proje tek kişilik olduğundan tüm kayıtların sorumlusu Burak Nigiz'dir.

Not: Hafta 1-3 paketleri geç kayıt nedeniyle 30.10.2026'da birlikte hazırlandı. Hafta 1 ve Hafta 2 kodu aynı gün yazıldı; o çalışmadaki geliştirme sorunları (ilk statik analiz koşusu, ilk temiz kurulum denemesi, arayüz sorunları) Hafta 2 paketinde kayıtlıdır.

## 1. Hafta 1'de yaşanan sorunlar

| ID | Sorun / standart sapması | Etki | Tespit yöntemi (V&V) | Alınan önlem | Durum | Kanıt |
|---|---|---|---|---|---|---|
| RSK-01 | ISO 9001:2026 (16.09.2026) ve ISO/IEC/IEEE 12207:2026 (2026-04) yayımlanmış. Ders belgeleri eski yapıyı kullanıyor (ör. 25010'da 8 karakteristik). 2026 numaraları 2015'ten farklı (ör. 10.1 Continual improvement, 6.1'in üç alt maddesi). | Yüksek | Kaynak doğrulaması: resmî ISO/IEEE sayfaları ve dağıtıcı örnek içindekiler | Güncel baskılar seçildi. Madde numaraları FDIS/örnek sayfalarından doğrulandı. 2011↔2023 eşlemesi yazıldı. Öğretim elemanına soru eklendi (AK-05). | Kısmen çözüldü (onay bekliyor) | [STANDARDS.md](STANDARDS.md) |
| RSK-02 | Girdiler eksik: ayrıntılı SDS-07 proje dokümanı elde edilemedi; grup numarası atanmadı. | Orta | Girdi incelemesi | Proje talimatı esas alındı. Grup numarası atanmadığı için raporlarda öğrenci numarası ve ad kullanıldı (AK-06, AK-07). Ekip bilgisi netleşti: proje tek kişilik. | Açık | SRS §10 |
| RSK-03 | Tek kişilik ekip: bağımsız kod/belge incelemesi ve görevler ayrılığı yapılamıyor; IEEE 1012'deki bağımsız V&V uygulanamıyor. | Orta | Proje planlaması (ekip bilgisi) | Doğrulama otomatik kapılara bağlandı: test, ruff, `check --deploy`, RTM `--strict`. İnceleme kontrol listesi kendi kendine uygulanır (PRC-03). Öğretim elemanı geri bildirimi bağımsız inceleme yerine kullanılır. | Açık (kısıt) | [PROCEDURES.md](PROCEDURES.md), [STANDARDS.md §4](STANDARDS.md) |
| RSK-04 | Üretim profilinde `check --deploy`, HSTS preload ayarı için uyarı verdi (security.W021). Preload, alan adının tarayıcı ön yükleme listesine kalıcı olarak eklenmesini gerektirir; ders projesinde alan adı yok. | Düşük | Yapılandırma denetimi (`check --deploy --fail-level WARNING`) | `SECURE_HSTS_PRELOAD` açılmadı; uyarı gerekçesiyle `SILENCED_SYSTEM_CHECKS` içinde susturuldu. Diğer HSTS ayarları açık. Susturmasız koşu kanıt olarak saklandı. | Kapandı (gerekçeli) | `evidence/hafta-01/check-deploy-susturmasiz.txt`, `check-deploy.txt` |
| RSK-05 | Uzak depo ve GitHub Actions yok. CI matrisi (Windows dahil) hiç koşmadı. Windows'ta kurulum doğrulanmadı. | Orta | Ortam kontrolü | Yerel eşdeğer komutlar Linux'ta Python 3.12 ve 3.13 ile koşuldu. `ci.yml` actionlint 1.7.12 ile statik denetlendi (0 bulgu). 02.11.2026: depo oluşturuldu, ilk CI koşusunda Ubuntu ve Windows × Python 3.12/3.13 işlerinin dördü de başarılı oldu (02.11.2026, koşu #1, commit 29f962c). | Kapandı | `evidence/hafta-01/manual-checks.json`, `ci-github-actions-2026-11-02.json` |
| RSK-06 | RTM üreticisi özet tablosunda "NOT RUN" durumunu "NOT" olarak sayıyordu (durum adı boşluktan bölünüyordu). Rapor sayılarının yanlış okunmasına yol açabilirdi. | Orta | Hafta 1 RTM üretim çıktısının incelenmesi | Sayım, parantezli ayrıntıyı atacak şekilde düzeltildi (`count_by_status`). Gerileme testi TC-QA-04 eklendi; hatalı kodla FAIL verdiği doğrulandı. | Kapandı | `evidence/hafta-01/rtm-ozet-hatasi-duzeltme-oncesi.txt`, `tc-qa-04-hatali-kodla.txt` |
| RSK-07 | Araç kodunda karmaşıklık eşiği aşıldı: `tools/build_report.py::build` döngüsel karmaşıklığı 19 (hedef ≤ 10). Uygulama kodunda en yüksek değer 4. | Düşük | Kod analizi (ruff C901 ölçümü) | Uygulama kodu etkilenmiyor. Fonksiyon daha küçük parçalara bölünecek. | Açık | [QUALITY_METRICS.md](QUALITY_METRICS.md) |

## 2. Önümüzdeki haftaların riskleri

| ID | Risk | Olasılık | Etki | Önlem | Hafta |
|---|---|---|---|---|---|
| RSK-08 | Kayıt bazlı yetki atlaması: talep sahibi başkasının kaydına numarayla erişir (IDOR). | Orta | Yüksek | Tüm sorgular tek bir politika fonksiyonundan geçer. Her ayrıntı ve işlem adresi için başka kullanıcıyla doğrudan erişim testi yazılır (404 beklenir). | 3 |
| RSK-09 | Durum makinesinin form dışında, doğrudan POST ile atlanması. | Orta | Yüksek | Geçişler tek servis fonksiyonunda. İzin verilmeyen her geçiş çifti için test yazılır. | 5 |
| RSK-10 | SLA sınır hataları (hedefe eşit an, öncelik değişikliği, 7/24 hesap). | Yüksek | Yüksek | SRS §6.3 kuralları. Zamanı sabitleyen testlerle hedefe eşit ve ±1 sn senaryoları. | 7 |
| RSK-11 | Arka plan kontrolünün mükerrer bildirim üretmesi (tekrar veya çakışan çalıştırma). | Orta | Orta | Veritabanı tekillik kısıtı. Komut iki kez çalıştırılınca tek bildirim testi. | 8 |
| RSK-12 | SQLite eşzamanlı yazma kısıtı ("database is locked") demo sırasında. | Düşük | Orta | Kısa işlemler, SQLite `timeout`. Demo verisi önceden yüklenir. Üretimde farklı veritabanı önerisi belgelenir. | 7-14 |
| RSK-13 | Kapsam büyümesi (ek özellik istekleri, gereksiz servisler). | Orta | Orta | Yalnız aktif haftanın kapsamı uygulanır. Yeni istek RTM'ye yeni kimlikle ve hafta önerisiyle eklenir. | Tümü |
| RSK-14 | Windows'a özgü farklar (saat dilimi verisi, yol, satır sonu). | Orta | Orta | `tzdata` koşullu bağımlılık, `.gitattributes`, CI'da windows-latest. | Tümü |
| RSK-15 | Django güvenlik yamalarının kaçırılması. | Orta | Yüksek | Her hafta başında 5.2.x sürüm notlarının kontrolü. Hafta 11-12'de bağımlılık güvenlik taraması. | Tümü |
| RSK-16 | Kodun sunumda ve vizede açıklanamaması. | Orta | Yüksek | Her modülde açıklayıcı belge dizeleri. [KOD_REHBERI.md](KOD_REHBERI.md). Burak Nigiz kodu kendi cümleleriyle anlatabilecek düzeye getirir. | Tümü |
