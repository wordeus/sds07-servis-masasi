# SDS-07 Servis Masası

ISO 9001 ilkelerini destekleyen IT Servis Masası ve Süreç Takip Sistemi. İstanbul Kültür Üniversitesi "Software Development with Standards" dersi kapsamında Burak Nigiz (2100002062) tarafından geliştirilmektedir (tek kişilik proje).

**Durum: Hafta 1 paketi (sürüm 0.1.0).** Kapsam, gereksinimler (SRS v0.1), standart araştırması, Django kurulumu, ayar profilleri, özel kullanıcı modeli ve doğrulama altyapısı. Kullanıcı arayüzü yoktur; giriş/çıkış ve roller Hafta 2'de eklenir. Güncel durum: [docs/PROJECT_STATE.md](docs/PROJECT_STATE.md).

## Teknoloji

Python 3.12/3.13, Django 5.2.18 (LTS), SQLite (yerel geliştirme). Arayüz Hafta 2'den itibaren Django Templates ve Bootstrap 5.3.8 ile yapılacaktır. Ayrı API, SPA, JWT, mikroservis veya ek servis yoktur.

## Hızlı başlangıç (Windows PowerShell)

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Tarayıcıda `http://127.0.0.1:8000/` adresi yönetim sitesine (`/admin/`) yönlenir. Ayrıntılı kurulum, Linux adımları ve testler: [docs/INSTALL.md](docs/INSTALL.md).

## Klasör yapısı

```
config/                 Django proje ayarları, URL'ler, izlenebilir test koşucusu
servicedesk/            Uygulama; Hafta 1'de özel kullanıcı modeli (MOD-AUTH veri modeli)
  tests/                TC kimlikli birim, entegrasyon ve yapılandırma testleri
tools/                  RTM üretici, rapor üretici, temiz kurulum denetimi
docs/                   SRS, RTM, test planı ve sonuçları, riskler, standartlar,
                        kalite ölçümleri, prosedürler, kurulum, kod rehberi, rapor, kanıtlar
.github/workflows/      CI iş akışı
```

## Belgeler

| Belge | İçerik |
|---|---|
| [SRS](docs/SRS.md) | Kapsam, roller, FR/NFR, SLA/KPI kuralları, kabul kriterleri, haftalık plan |
| [RTM](docs/RTM.md) | Gereksinim → modül → test → gerçek sonuç (otomatik üretilir, `--week 1`) |
| [Test planı](docs/TEST_PLAN.md) / [Sonuçlar](docs/TEST_RESULTS.md) | V&V yaklaşımı ve gerçek sonuçlar |
| [Riskler](docs/RISKS.md) | Yaşanan sorunlar ve riskler |
| [Standartlar](docs/STANDARDS.md) | Kullanılan baskılar, resmî bağlantılar, madde doğrulama durumu |
| [Kalite ölçümleri](docs/QUALITY_METRICS.md) | ISO/IEC 25010:2023 ile ilişkili ölçümler |
| [Prosedürler](docs/PROCEDURES.md) | Dal, commit, inceleme, belge kontrolü kuralları |
| [Kod rehberi](docs/KOD_REHBERI.md) | Hafta 1 kodunun sunumda anlatılacak özeti, vize malzemesi |
| [Rapor 1](docs/reports/Rapor-01_Hafta-1.docx) | İlerleme raporu #1 (Hafta 1) |
| [Kanıtlar](docs/evidence/hafta-01/) | Test JSON'ları, günlükler, kurulum denetimleri |
| [Değişiklik günlüğü](CHANGELOG.md) | Sürüm geçmişi |

Bu yazılım ISO 9001 belgelendirmesi sağlamaz; kalite yönetim sistemi uygulamalarını destekleyen bir araçtır.
