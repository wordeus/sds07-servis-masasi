# SDS-07 Servis Masası

ISO 9001 ilkelerini destekleyen IT Servis Masası ve Süreç Takip Sistemi. İstanbul Kültür Üniversitesi "Software Development with Standards" dersi kapsamında Burak Nigiz (2100002062) tarafından geliştirilmektedir (tek kişilik proje).

**Durum: Hafta 2 paketi (sürüm 0.2.0).** Hafta 1 altyapısının üzerine giriş/çıkış, üç rol grubu, sunucu tarafı yetkilendirme, Türkçe arayüz ve tarayıcı (E2E) testleri eklendi; SDD v0.1 hazırlandı. Talep işlemleri Hafta 3'te eklenir. Güncel durum: [docs/PROJECT_STATE.md](docs/PROJECT_STATE.md).

## Teknoloji

Python 3.12/3.13, Django 5.2.18 (LTS), Django Templates, Bootstrap 5.3.8, SQLite (yerel geliştirme). Ayrı API, SPA, JWT, mikroservis veya ek servis yoktur.

## Hızlı başlangıç (Windows PowerShell)

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Ayrıntılı kurulum, Linux adımları, demo kullanıcılar ve testler: [docs/INSTALL.md](docs/INSTALL.md).

## Klasör yapısı

```
config/                 Django proje ayarları, URL'ler, izlenebilir test koşucusu
servicedesk/            Uygulama (MOD-AUTH, MOD-ROLE, MOD-UI)
  roles.py              Rol tanımları, rol-izin matrisi, grup senkronizasyonu
  tests/                TC kimlikli birim ve entegrasyon testleri
templates/              Ortak şablonlar, giriş ve hata sayfaları
static/                 app.css, Bootstrap 5.3.8 ve IBM Plex Sans (yerel)
e2e/                    Playwright tarayıcı senaryoları
tools/                  RTM üretici, rapor üretici, E2E koşu betiği, kurulum ve mutasyon denetimi
docs/                   SRS, SDD, RTM, test planı ve sonuçları, riskler, standartlar,
                        kalite ölçümleri, prosedürler, kurulum, kod rehberi, raporlar, kanıtlar
.github/workflows/      CI iş akışı
```

## Belgeler

| Belge | İçerik |
|---|---|
| [SRS](docs/SRS.md) | Kapsam, roller, FR/NFR, SLA/KPI kuralları, kabul kriterleri, haftalık plan |
| [SDD](docs/SDD.md) | Bağlam, bileşim/mantık, bilgi (ER), durum görünümleri; karar günlüğü |
| [RTM](docs/RTM.md) | Gereksinim → modül → test → gerçek sonuç (otomatik üretilir, `--week 2`) |
| [Test planı](docs/TEST_PLAN.md) / [Sonuçlar](docs/TEST_RESULTS.md) | V&V yaklaşımı ve gerçek sonuçlar |
| [Riskler](docs/RISKS.md) | Yaşanan sorunlar ve riskler |
| [Standartlar](docs/STANDARDS.md) | Kullanılan baskılar, resmî bağlantılar, madde doğrulama durumu |
| [Kalite ölçümleri](docs/QUALITY_METRICS.md) | ISO/IEC 25010:2023 ile ilişkili ölçümler |
| [Prosedürler](docs/PROCEDURES.md) | Dal, commit, inceleme, belge kontrolü, E2E koşu kuralları |
| [Kod rehberi](docs/KOD_REHBERI.md) | Hafta 1-2 kodunun sunumda anlatılacak özeti, vize malzemesi |
| [Rapor 1](docs/reports/Rapor-01_Hafta-1.docx) / [Rapor 2](docs/reports/Rapor-02_Hafta-2.docx) | Haftalık ilerleme raporları |
| [Kanıtlar](docs/evidence/) | Haftalara göre test JSON'ları, günlükler, ekran görüntüleri, mutasyon denetimi |
| [Değişiklik günlüğü](CHANGELOG.md) | Sürüm geçmişi |

## Üçüncü taraf bileşenler

- Bootstrap 5.3.8: MIT lisansı (`static/vendor/bootstrap-5.3.8/LICENSE`)
- IBM Plex Sans (@fontsource 5.3.0): SIL Open Font License 1.1 (`static/vendor/ibm-plex-sans-5.3.0/LICENSE`)

Bu yazılım ISO 9001 belgelendirmesi sağlamaz; kalite yönetim sistemi uygulamalarını destekleyen bir araçtır.
