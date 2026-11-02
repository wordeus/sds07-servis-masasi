# Değişiklik günlüğü

Biçim [Keep a Changelog](https://keepachangelog.com/tr-TR/1.1.0/) yaklaşımını, sürüm numaraları anlamsal sürümlemeyi izler. Her haftalık paket bir sürümdür.

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

### Düzeltildi (teslim öncesi kontrol, 30.10.2026)
Hafta 3 paketinin teslim öncesi kontrolünde bulundu ve ilk commit'ten önce bu pakete de uygulandı. Kod ve testler değişmedi. Ayrıntı ve kanıt Hafta 3 paketindedir: RISKS.md (RSK-24, RSK-25) ve docs/evidence/hafta-03/teslim-oncesi klasörü.
- `.gitignore`: `reports/` ve `*.log` kalıpları `docs/reports/` altındaki raporları ve `docs/evidence/` altındaki kurulum günlüklerini de dışlıyordu; kalıp köke bağlandı (`/reports/`) ve kanıt günlükleri için istisna eklendi.
- CI: Windows işlerinde Türkçe karakterli çıktının `UnicodeEncodeError` vermemesi için Python UTF-8 kipi (`PYTHONUTF8: "1"`) eklendi.

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
