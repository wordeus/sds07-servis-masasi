# Değişiklik günlüğü

Biçim [Keep a Changelog](https://keepachangelog.com/tr-TR/1.1.0/) yaklaşımını, sürüm numaraları anlamsal sürümlemeyi izler. Her haftalık paket bir sürümdür.

## [0.3.0] - 2026-10-30 (Hafta 3, yayımlanmadı)

### Eklendi
- Category ve Ticket modelleri (migration 0003) ve başlangıç kategorileri (veri migration'ı 0004); talep numarası `INC-000123` birincil anahtardan türetilir.
- Talep oluşturma (`/talepler/yeni/`), listeleme ve filtreleme (durum, öncelik, kategori, atanan; sayfa başına 25), talep ayrıntısı ve süreç şeridi.
- Kayıt bazlı erişim politikası (`services/tickets.py::visible_tickets_for`): talep sahibi yalnız kendi taleplerini görür; başkasının talebine 404.
- Kategori ekleme ve pasifleştirme (`/kategoriler/`, yalnız Yönetici); kategori silinmez.
- Destek kuyruğunda açık talepler; panelde talep durum özeti; menüde Talepler ve Kategoriler bağlantıları.
- Rol-izin matrisine talep ve kategori izinleri; `CURRENT_WEEK = 3`.
- 14 yeni TC kimlikli Django testi (toplam 49): TC-TKT-01..08, TC-CAT-01..03, TC-ARCH-01..02, TC-ROLE-13; 4 yeni tarayıcı senaryosu (`e2e/week3_tickets.py`, TC-E2E-10..13); 4 yeni mutasyon (toplam 8).
- SDD v0.2 (katmanlı yapı, kayıt düzeyi erişim diyagramı, KRR-11..KRR-15); SRS v0.3, STANDARDS v0.3, RISKS v0.3, TEST_PLAN v0.3, PROCEDURES v0.3; Rapor #3.

### Değişti
- `models.py` → `models/` paketi, `views.py` → `views/` paketi; iş kuralları `services/` paketinde (NFR-16).
- E2E sunucusu `DJANGO_DEBUG=0` ve `--insecure` ile çalışır (RSK-23); E2E giriş yardımcısı gezinmeyi bekler (RSK-22).
- `tools/build_report.py::build` küçük fonksiyonlara bölündü (19 → 4); çıktı bayt bayt aynı (RSK-07).

### Düzeltildi
- Kategori adı tekilliğinin Türkçe büyük harfleri (I/ı, İ/i) kaçırması (RSK-21).
- Teslim öncesi kontrol (30.10.2026): `.gitignore`'daki `reports/` ve `*.log` kalıpları `docs/reports/` altındaki raporları ve `docs/evidence/` altındaki kurulum günlüklerini depo dışında bırakıyordu; kalıp köke bağlandı ve kanıt günlükleri için istisna eklendi (RSK-24). Aynı düzeltme Hafta 1 ve 2 paketlerine de uygulandı.
- Teslim öncesi kontrol (30.10.2026): Windows'ta yönlendirilmiş çıktıda Türkçe karakterlerin `UnicodeEncodeError` vermesi; CI'a Python UTF-8 kipi (`PYTHONUTF8: "1"`) eklendi, INSTALL.md'ye Windows notu yazıldı (RSK-25). Aynı CI ayarı Hafta 1 ve 2 paketlerine de eklendi.

## [0.2.0] - 2026-10-30 (Hafta 2, yayımlanmadı)

### Eklendi
- Giriş (Django LoginView) ve yalnız POST ile çıkış; güvenli `next` yönlendirmesi; üç durumda aynı genel hata mesajı.
- Talep Sahibi, Destek Personeli ve Yönetici rol grupları; koddaki matrisin her `migrate` sonrasında uygulanması (`post_migrate`); kullanıcı modeline uygulama izinleri (migration 0002).
- Sunucu tarafı yetkilendirme (`PermissionRequiredMixin`); Türkçe 403, 404, 500 ve CSRF hata sayfaları.
- Role göre panel, destek kuyruğu ve yönetim paneli iskeletleri; panelde yeteneklerin uygulanacağı hafta etiketi; Bootstrap 5.3.8 ve IBM Plex Sans (yerel dosya).
- `seed_demo_users` yönetim komutu (yalnız geliştirme ortamında).
- 27 yeni TC kimlikli Django testi (toplam 35), 9 tarayıcı (E2E) senaryosu (`e2e/week2_auth_roles.py`), E2E koşu betiği `tools/run_e2e.sh` (port denetimli), mutasyon denetimi `tools/mutation_check.py`.
- SDD v0.1 ve diyagramlar; SRS v0.2, STANDARDS v0.2, RISKS v0.2, TEST_PLAN v0.2; Rapor #2.

### Değişti
- Kök adres yönetim sitesi yerine kullanıcı paneline yönlenir.

## [0.1.0] - 2026-10-30 (Hafta 1, yayımlanmadı)

### Eklendi
- Django 5.2.18 projesi (`config`) ve tek uygulama (`servicedesk`); sabitlenmiş bağımlılıklar.
- Özel kullanıcı modeli (`AbstractUser`), Türkçe yönetim sitesi, UTC saklama ve Europe/Istanbul gösterimi.
- development/production ayar profilleri; üretimde güvensiz yapılandırmayla başlamama; katı ortam değişkeni ayrıştırma.
- 8 TC kimlikli Django testi; TC sonuçlarını JSON'a yazan test koşucusu.
- RTM ve test sonuç tablosunu gerçek sonuçlardan üreten `tools/build_rtm.py` (`--week`); rapor üretici `tools/build_report.py`; temiz kurulum denetimi `tools/install_check.sh`.
- GitHub Actions CI iş akışı (Ubuntu/Windows × Python 3.12/3.13).
- SRS v0.1, RTM, test planı ve sonuçları, risk listesi, standartlar, kalite ölçümleri, prosedürler, kurulum kılavuzu, kod rehberi, Rapor #1.

### Düzeltildi
- RTM özet tablosunda "NOT RUN" durumunun "NOT" olarak sayılması (RSK-06); gerileme testi TC-QA-04.
