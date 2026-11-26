# Değişiklik günlüğü

Biçim [Keep a Changelog](https://keepachangelog.com/tr-TR/1.1.0/) yaklaşımını, sürüm numaraları anlamsal sürümlemeyi izler. Her haftalık paket bir sürümdür.

## [1.0.0] - 2026-11-26 (Faz 5, son teslim)

### Eklendi
- Durum makinesi: Açık → İşlemde → Çözüldü → Kapandı; tanımsız geçişlerin doğrudan POST dahil reddi (FR-18). Atanmış personel veya Yönetici ilerletir; çözüm açıklaması zorunlu; talep sahibi veya Yönetici kapatır (FR-19). `services/workflow.py`, `TicketStatusView`, migration 0007.
- İşlem geçmişi görünümü: talep ayrıntısında kronolojik, İstanbul saatiyle, Türkçe etiketli (FR-21); durum geçişleri geçmişe yazılır (FR-20).
- 7 yeni TC kimlikli Django testi (toplam 69): TC-WF-01..06, TC-ROLE-15; 2 tarayıcı senaryosu (`e2e/week5_status.py`, TC-E2E-17..18); 5 yeni mutasyon (toplam 18).
- SRS v0.5, SDD v0.4, RISKS v0.5, TEST_PLAN v0.5, INSTALL v0.5, STANDARDS v0.5; Rapor #5; final belgesi ve sunum.

### Değişti
- AK-01 kapandı: yeniden açma geçişi yok (KRR-19). `CURRENT_WEEK = 5`; rol matrisine ilerletme ve kapatma izinleri.
- E2E betikleri ortak `run_suite` iskeletini kullanır; Hafta 2 senaryoları modül düzeyinde fonksiyonlara bölündü; en yüksek karmaşıklık 18 → 3 (PLN-06, RSK-07 kapandı).

### Düzeltildi
- Durum servisinde talep sahipliği kuralını sınayan test eksikti (RSK-33).

## [0.4.0] - 2026-11-26 (Hafta 4)

### Eklendi
- Talebi üzerine alma (Destek Personeli, Yönetici) ve atama (yalnız Yönetici; yalnız etkin Destek Personeline) (FR-16).
- Yorumlar: talep sahibi kendi talebine, personel ve yönetici tüm taleplere; kapanmış talebe yorum yok; başkasının talebinin yorum adresinde 404 (FR-17, FR-14).
- Öncelik değişikliği (Destek Personeli, Yönetici); AK-03 kapandı (KRR-17).
- İşlem geçmişi (MOD-AUDIT): oluşturma, atama ve öncelik değişikliği aktör, UTC zaman, eski ve yeni değerle; kayıtlar değiştirilemez ve silinemez (FR-20, KRR-16). Hafta 4 öncesi taleplere oluşturma kaydı (migration 0006).
- `services/assignment.py`, `services/comments.py`, `services/audit.py`, `views/ticket_actions.py`; Comment ve TicketEvent modelleri (migration 0005).
- 13 yeni TC kimlikli Django testi (toplam 62): TC-ASN-01..05, TC-CMT-01..04, TC-AUD-01..03, TC-ROLE-14; 3 tarayıcı senaryosu (`e2e/week4_workflow.py`, TC-E2E-14..16); 5 yeni mutasyon (toplam 13).
- `tools/run_e2e.ps1` (Windows E2E), `tools/install_check.ps1` Hafta 4 koşusu; RTM aracında KAPSAM DIŞI durumu.
- SRS v0.4, SDD v0.3, RISKS v0.4, TEST_PLAN v0.4, INSTALL v0.4, STANDARDS v0.4; Rapor #4.

### Değişti
- Teslim kapsamı: proje Faz 5'te biter; FR-22..FR-37 ve NFR-13..NFR-15 gelecek çalışma (KRR-18). Panelde bu yetenekler "Kapsam dışı" görünür.
- Bağımlılıklar: Django 5.2.19 (güvenlik), sqlparse 0.6.1 (güvenlik; son sürüm, RSK-31), coverage 7.17.4, ruff 0.17.6, Playwright 1.65.2.
- `CURRENT_WEEK = 4`; rol-izin matrisine yorum, üzerine alma, atama ve öncelik izinleri.

### Düzeltildi
- Alan dışı iş kuralı hatası işlem görünümünde 500 hatasına yol açıyordu (RSK-28).
- Kapanmış talebe yorum reddinin sebebi gösterilmiyordu (RSK-29).

## [0.3.0] - 2026-10-30 (Hafta 3, yayımlanmadı)

### Eklendi
- Category ve Ticket modelleri (migration 0003) ve başlangıç kategorileri (veri migration'ı 0004); talep numarası `INC-000123` birincil anahtardan türetilir.
- Talep oluşturma (`/talepler/yeni/`), listeleme ve filtreleme (durum, öncelik, kategori, atanan; sayfa başına 25), talep ayrıntısı ve süreç şeridi.
- Kayıt bazlı erişim politikası (`services/tickets.py::visible_tickets_for`): talep sahibi yalnız kendi taleplerini görür; başkasının talebine 404.
- Kategori ekleme ve pasifleştirme (`/kategoriler/`, yalnız Yönetici); kategori silinmez.
- Destek kuyruğunda açık talepler; panelde talep durum özeti; menüde Talepler ve Kategoriler bağlantıları.
- Rol-izin matrisine talep ve kategori izinleri; `CURRENT_WEEK = 3`.
- 14 yeni TC kimlikli Django testi (toplam 49): TC-TKT-01..08, TC-CAT-01..03, TC-ARCH-01..02, TC-ROLE-13; 4 yeni tarayıcı senaryosu (`e2e/week3_tickets.py`, TC-E2E-10..13); 4 yeni mutasyon (toplam 8).
- Teslim öncesi güncelleme (26.11.2026): Hafta 3 GitHub Actions kanıtı (koşu #5, 4/4 iş) ve ilk Windows koşusu (49/49 PASS, temiz kurulum BAŞARILI); `tools/install_check.ps1` (Windows temiz kurulum), `tools/record_ci_run.sh` (CI kanıtı), Dependabot ve etiketle Release iş akışı. RTM: 28/28 gereksinim, 67/67 test PASS.
- SDD v0.2 (katmanlı yapı, kayıt düzeyi erişim diyagramı, KRR-11..KRR-15); SRS v0.3, STANDARDS v0.3, RISKS v0.3, TEST_PLAN v0.3, PROCEDURES v0.3; Rapor #3.

### Değişti
- `models.py` → `models/` paketi, `views.py` → `views/` paketi; iş kuralları `services/` paketinde (NFR-16).
- E2E sunucusu `DJANGO_DEBUG=0` ve `--insecure` ile çalışır (RSK-23); E2E giriş yardımcısı gezinmeyi bekler (RSK-22).
- `tools/build_report.py::build` küçük fonksiyonlara bölündü (19 → 4); çıktı bayt bayt aynı (RSK-07).

### Düzeltildi
- Kategori adı tekilliğinin Türkçe büyük harfleri (I/ı, İ/i) kaçırması (RSK-21).
- Teslim öncesi kontrol (30.10.2026): `.gitignore`'daki `reports/` ve `*.log` kalıpları `docs/reports/` altındaki raporları ve `docs/evidence/` altındaki kurulum günlüklerini depo dışında bırakıyordu; kalıp köke bağlandı ve kanıt günlükleri için istisna eklendi (RSK-24). Aynı düzeltme Hafta 1 ve 2 paketlerine de uygulandı.
- Teslim öncesi güncelleme (26.11.2026): RTM üreticisi Windows'ta kanıt yollarını ters bölüyle yazıyordu; yollar `as_posix()` ile yazılıyor, TC-QA-04'e denetim eklendi (RSK-26).
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
