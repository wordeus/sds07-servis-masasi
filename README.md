# SDS-07 Servis Masası

ISO 9001 ilkelerini destekleyen IT Servis Masası ve Süreç Takip Sistemi. İstanbul Kültür Üniversitesi "Software Development with Standards" dersi kapsamında Burak Nigiz (2100002062) tarafından geliştirilmektedir (tek kişilik proje).

Roller: **Talep Sahibi**, **Destek Personeli**, **Yönetici**. Talep akışı: Open → In Progress → Resolved → Closed. Proje beş fazda tamamlandı; **Faz 5 bitiş fazıdır**. Final belgesi ve sunum: [docs/final/](docs/final/). Her faz bir paket, bir ilerleme raporu ve bir GitHub etiketiyle (`hafta-N`) teslim edilir.

## 1. Durum özeti

| Faz | Kapsam | Son teslim | Durum | Etiket ve Release | Rapor |
|---|---|---|---|---|---|
| 1 | Kapsam, gereksinimler, standartlar, kurulum ve doğrulama altyapısı | 16.10.2026 | Tamamlandı | [`hafta-1`](https://github.com/wordeus/sds07-servis-masasi/tree/hafta-1) | [Rapor #1](docs/reports/Rapor-01_Hafta-1.docx) |
| 2 | Giriş/çıkış, roller, yetkilendirme, arayüz, tarayıcı testleri | 30.10.2026 | Tamamlandı | [`hafta-2`](https://github.com/wordeus/sds07-servis-masasi/tree/hafta-2) | [Rapor #2](docs/reports/Rapor-02_Hafta-2.docx) |
| 3 | Talep oluşturma ve listeleme, kayıt bazlı erişim, kategoriler, modüler mimari | 13.11.2026 | Tamamlandı | [`hafta-3`](https://github.com/wordeus/sds07-servis-masasi/releases/tag/hafta-3) | [Rapor #3](docs/reports/Rapor-03_Hafta-3.docx) |
| 4 | Atama ve üzerine alma, yorumlar, öncelik değişikliği, işlem geçmişi | 27.11.2026 | Tamamlandı | [`hafta-4`](https://github.com/wordeus/sds07-servis-masasi/releases/tag/hafta-4) | [Rapor #4](docs/reports/Rapor-04_Hafta-4.docx) |
| 5 (bitiş) | Durum geçişleri ve işlem geçmişi görünümü; final belgesi, sunum ve demo | 11.12.2026 | Tamamlandı | [`hafta-5`](https://github.com/wordeus/sds07-servis-masasi/releases/tag/hafta-5) | [Rapor #5](docs/reports/Rapor-05_Hafta-5.docx) |

Güncel ayrıntı ve açık işler: [docs/PROJECT_STATE.md](docs/PROJECT_STATE.md).

## 2. Fazlar

### Faz 1 (Hafta 1): Temel ve doğrulama altyapısı

- **Yapılanlar:** Django 5.2 LTS proje iskeleti, geliştirme ve üretim ayar profilleri, özel kullanıcı modeli, TC kimlikli sonuç kaydeden test koşucusu, RTM üreticisi, GitHub Actions CI (Ubuntu ve Windows × Python 3.12/3.13).
- **Belgeler:** SRS v0.1, STANDARDS, RISKS, TEST_PLAN, PROCEDURES ilk sürümleri.
- **Sonuçlar:** 8/8 Django testi PASS, kapsam %87,39; CI koşusu #1 (commit `29f962c`) 4/4 iş başarılı.
- **Kanıt:** [docs/evidence/hafta-01/](docs/evidence/hafta-01/)

### Faz 2 (Hafta 2): Giriş, roller ve yetkilendirme

- **Yapılanlar:** Giriş ve yalnız POST ile çıkış, üç rol grubu ve rol-izin matrisi, sunucu tarafı yetki denetimi, Türkçe hata sayfaları, Bootstrap arayüzü, Playwright tarayıcı testleri, mutasyon denetimi. SDD v0.1.
- **Sonuçlar:** 35/35 Django testi ve 9/9 tarayıcı senaryosu PASS, kapsam %92,08; CI koşusu #3 (commit `6dd3dc9`) 4/4 iş başarılı.
- **Kanıt:** [docs/evidence/hafta-02/](docs/evidence/hafta-02/)

### Faz 3 (Hafta 3): Talepler, kayıt bazlı erişim, kategoriler

- **Yapılanlar:** Talep oluşturma (`INC-000123` numarası), filtreli ve sayfalı liste, talep ayrıntısı; talep sahibi yalnız kendi taleplerini görür, başkasının talebine 404; kategori ekleme ve pasifleştirme. Kod `models/`, `services/`, `views/` katmanlarına ayrıldı ve katman kuralı testle denetleniyor. SDD v0.2.
- **Sonuçlar:** 49/49 Django testi ve 13/13 tarayıcı senaryosu PASS, kapsam %94,21, mutasyon denetimi 8/8. RTM: 28/28 gereksinim, 67/67 test PASS. CI koşusu #5 4/4 iş başarılı; Windows 11'de temiz kurulum BAŞARILI.
- **Kanıt:** [docs/evidence/hafta-03/](docs/evidence/hafta-03/)

### Faz 4 (Hafta 4): Atama, yorumlar, işlem geçmişi

- **Yapılanlar:** Destek Personeli atanmamış talebi üzerine alır; Yönetici talebi yalnız Destek Personeline atar; personel ve yönetici önceliği değiştirir (AK-03 kapandı). Yorumlar: talep sahibi kendi talebine, personel ve yönetici tüm taleplere; kapanmış talebe yorum yok; başkasının talebinin yorum adresinde 404. İşlem geçmişi: her işlem aktör, UTC zaman, eski ve yeni değerle; kayıtlar değiştirilemez. Bağımlılıklar güncellendi (Django 5.2.19). Kapsam kararı: proje Faz 5'te biter (KRR-18).
- **Sonuçlar:** 62/62 Django testi ve 16/16 tarayıcı senaryosu PASS (Windows 11), kapsam %95,04, mutasyon denetimi 13/13; Windows'ta temiz kurulum BAŞARILI. Testler geliştirme sırasında üç hata yakaladı (RSK-28..RSK-30).
- **Kanıt:** [docs/evidence/hafta-04/](docs/evidence/hafta-04/)

### Faz 5 (Hafta 5): Durum geçişleri ve proje bitişi

- **Yapılanlar:** Durum makinesi (Açık → İşlemde → Çözüldü → Kapandı); atanmış personel veya yönetici ilerletir, çözüm açıklaması zorunlu, talep sahibi veya yönetici kapatır; tanımsız geçişler doğrudan POST ile de reddedilir. Talep sayfasında işlem geçmişi (İstanbul saatiyle). Yeniden açma yok (AK-01, KRR-19). E2E kodu sadeleştirildi (karmaşıklık 18 → 3). Final belgesi ve sunum.
- **Sonuçlar:** 69/69 Django testi ve 18/18 tarayıcı senaryosu PASS, kapsam %95,03, mutasyon denetimi 18/18 (ilk koşuda bulunan test açığı kapatıldı, RSK-33); dört durum rozetinin kontrastı tarayıcıda ölçüldü (en düşük 5,42:1).
- **Kanıt:** [docs/evidence/hafta-05/](docs/evidence/hafta-05/)

### Gelecek çalışma (kapsam dışı)

Proje Faz 5'te bittiği için 14 haftalık ilk plandaki şu modüller bu teslimde yapılmaz; SRS'te "gelecek çalışma" olarak işaretlenir (karar Hafta 4 paketinde kayıtlıdır): değişiklik yönetimi (FR-22..FR-25), SLA ve eskalasyon (FR-26..FR-30), bildirim kutusu (FR-31), memnuniyet anketi ve KPI paneli (FR-32..FR-34), uygunsuzluk ve DÖF (FR-35..FR-37), performans ve tarayıcı uyumu ölçümleri (NFR-13..NFR-15).

## 3. Kurulum (Windows PowerShell)

1. Python 3.13'ü python.org yükleyicisiyle kurun (`py` başlatıcısıyla birlikte).
2. Sanal ortamı oluşturun ve etkinleştirin:
   ```powershell
   py -3.13 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. Sabitlenmiş bağımlılıkları kurun:
   ```powershell
   pip install -r requirements-dev.txt
   ```
4. Veritabanını oluşturun ve yönetici hesabı açın:
   ```powershell
   python manage.py migrate
   python manage.py createsuperuser
   ```
5. Sunucuyu başlatın ve http://127.0.0.1:8000/ adresini açın:
   ```powershell
   python manage.py runserver
   ```

Linux adımları, demo kullanıcılar ve tarayıcı testleri: [docs/INSTALL.md](docs/INSTALL.md).

## 4. Testler ve kalite kontrolleri

1. Testler ve kapsam: `coverage run manage.py test -v 2`, ardından `coverage report`
2. Statik analiz: `ruff format --check .` ve `ruff check .`
3. Windows'ta tarayıcı testleri: `powershell -ExecutionPolicy Bypass -File toolsun_e2e.ps1`; temiz kurulum denetimi: `powershell -ExecutionPolicy Bypass -File tools\install_check.ps1 3.13 windows-py313 reports\install-check-windows-py313.log`
4. RTM ve test sonuç tablosu: `python tools/build_rtm.py --week N --strict ...` (tam komut: [TEST_PLAN §6](docs/TEST_PLAN.md))

Çıktıyı dosyaya yönlendirirken Windows'ta önce `$env:PYTHONUTF8 = "1"` çalıştırın (RSK-25).

## 5. GitHub iş akışı (her faz için)

1. **Dal aç:** `hafta-N/<konu>` (ör. `hafta-4/atama`).
2. **Commit:** Conventional Commits biçiminde, özetin başında hafta: `feat: Hafta 4 - atama ve üzerine alma` (PRC-02).
3. **PR aç:** başlık `Hafta N: <özet>`. CI dört işi koşar (Ubuntu ve Windows × Python 3.12/3.13); Actions listesinde "PR #N · başlık" olarak görünür.
4. **Birleştir:** CI yeşil olmadan `main`'e birleştirilmez.
5. **CI kanıtını kaydet:** `bash tools/record_ci_run.sh N` komutu `main`'deki koşunun sonucunu `docs/evidence/hafta-0N/` altına yazar (TC-CI-01).
6. **Etiketle:** `hafta-N` etiketi gönderilir. Release iş akışı raporu ve kanıt zip'ini GitHub Release'e ekler.

Otomatik işler:

| İş akışı | Ne zaman | Ne yapar |
|---|---|---|
| [CI](.github/workflows/ci.yml) | `main`'e push, her PR, elle | ruff, Django kontrolleri, testler ve kapsam, `check --deploy`, RTM; raporları artifact olarak saklar |
| [Release](.github/workflows/release.yml) | `hafta-N` etiketi | Haftanın raporu ve kanıt zip'iyle GitHub Release |
| [Dependabot](.github/dependabot.yml) | Her Pazartesi 08:00 | pip ve Actions güncellemeleri için PR (Django yalnız 5.2.x yamaları) |

## 6. Klasör yapısı

```
config/                 Django proje ayarları, URL'ler, izlenebilir test koşucusu
servicedesk/            Uygulama (MOD-AUTH, MOD-ROLE, MOD-UI, MOD-TICKET)
  models/               Veri: User, Category, Ticket
  services/             İş kuralları: görünürlük politikası, talep, filtre, kategori
  views/                Görünümler: panel, talepler, kategoriler
  roles.py              Rol tanımları, rol-izin matrisi, grup senkronizasyonu
  tests/                TC kimlikli birim, entegrasyon ve mimari testler
templates/              Ortak şablonlar, giriş ve hata sayfaları
static/                 app.css, Bootstrap 5.3.8 ve IBM Plex Sans (yerel)
e2e/                    Playwright tarayıcı senaryoları
tools/                  RTM ve rapor üreticileri, E2E koşu betiği, kurulum denetimi (Linux ve Windows),
                        mutasyon denetimi, CI kanıtı kaydı
docs/                   SRS, SDD, RTM, test planı ve sonuçları, riskler, standartlar,
                        kalite ölçümleri, prosedürler, kurulum, kod rehberi, raporlar, kanıtlar
.github/                CI ve Release iş akışları, Dependabot
```

## 7. Belgeler

| Belge | İçerik |
|---|---|
| [SRS](docs/SRS.md) | Kapsam, roller, FR/NFR, SLA/KPI kuralları, kabul kriterleri, haftalık plan |
| [SDD](docs/SDD.md) | Bağlam, bileşim/mantık, bilgi (ER), durum görünümleri; karar günlüğü |
| [RTM](docs/RTM.md) | Gereksinim → modül → test → gerçek sonuç (otomatik üretilir) |
| [Test planı](docs/TEST_PLAN.md) / [Sonuçlar](docs/TEST_RESULTS.md) | V&V yaklaşımı ve gerçek sonuçlar |
| [Riskler](docs/RISKS.md) | Yaşanan sorunlar ve riskler |
| [Standartlar](docs/STANDARDS.md) | Kullanılan baskılar, resmî bağlantılar, madde doğrulama durumu |
| [Kalite ölçümleri](docs/QUALITY_METRICS.md) | ISO/IEC 25010:2023 ile ilişkili ölçümler |
| [Prosedürler](docs/PROCEDURES.md) | Dal, commit, inceleme, belge kontrolü, E2E koşu kuralları |
| [Kod rehberi](docs/KOD_REHBERI.md) | Hafta 1-5 kodunun sunumda anlatılacak özeti, vize malzemesi |
| [Final belgesi ve sunum](docs/final/) | Dönem sonu proje teslim dokümanı ve sunum |
| [Kanıtlar](docs/evidence/) | Haftalara göre test JSON'ları, günlükler, ekran görüntüleri, mutasyon denetimi |
| [Değişiklik günlüğü](CHANGELOG.md) | Sürüm geçmişi |

## 8. Teknoloji ve üçüncü taraf bileşenler

Python 3.12/3.13, Django 5.2.18 (LTS), Django Templates, Bootstrap 5.3.8, SQLite. Ayrı API, SPA, JWT, mikroservis veya ek servis yoktur.

- Bootstrap 5.3.8: MIT lisansı (`static/vendor/bootstrap-5.3.8/LICENSE`)
- IBM Plex Sans (@fontsource 5.3.0): SIL Open Font License 1.1 (`static/vendor/ibm-plex-sans-5.3.0/LICENSE`)

Bu yazılım ISO 9001 belgelendirmesi sağlamaz; kalite yönetim sistemi uygulamalarını destekleyen bir araçtır.
