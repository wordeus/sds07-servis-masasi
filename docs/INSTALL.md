# Kurulum ve çalıştırma kılavuzu

| Alan | Değer |
|---|---|
| Doküman kimliği | SDS07-INS |
| Sürüm | 0.1 (Hafta 1) |
| Tarih | 30.10.2026 |
| Doğrulama | Linux'ta Python 3.12.13 ve 3.13.18 ile temiz kurulum yapıldı (TC-INST-01, `docs/evidence/hafta-01/install-check-*.log`). **Windows adımları bu ortamda çalıştırılmadı (NOT RUN)**; ilk Windows kurulumunda sonucu `docs/evidence/hafta-01/` altına yeni dosya olarak ekleyin. |

## 1. Gereksinimler

- Python 3.12 veya 3.13 (Windows'ta python.org yükleyicisiyle kurup `py` başlatıcısını seçin)
- Git
- İnternet bağlantısı yalnız ilk paket kurulumunda gerekir.

Sürümler `requirements.txt` dosyasında sabitlenmiştir: Django 5.2.18, asgiref 3.13.0, sqlparse 0.6.0. Windows'ta saat dilimi verisi için `tzdata` 2026.6 otomatik kurulur.

## 2. Windows (PowerShell)

```powershell
# Proje klasörüne geçin (zip'i açtığınız veya depoyu klonladığınız yer)
cd C:\Projeler\sds07-servis-masasi

# Python sürümünü doğrulayın
py -3.13 --version

# Sanal ortamı oluşturup etkinleştirin
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
# "running scripts is disabled" hatası alırsanız yalnız bu pencere için izin verin:
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Bağımlılıkları kurun
python -m pip install --upgrade pip
pip install -r requirements-dev.txt

# Veritabanını oluşturun
python manage.py migrate

# Sistem yöneticisi hesabı (yönetim sitesi için)
python manage.py createsuperuser

# Sunucuyu başlatın, tarayıcıda http://127.0.0.1:8000/ adresini açın
python manage.py runserver
```

Hafta 1'de kullanıcı arayüzü yoktur: kök adres Django yönetim sitesine (`/admin/`) yönlenir ve özel kullanıcı modeli orada görülür. Giriş/çıkış sayfaları, rol grupları ve demo kullanıcı komutu Hafta 2'de eklenir.

## 3. Linux / macOS

```bash
cd sds07-servis-masasi
python3.13 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## 4. Testler ve kalite kontrolleri

PowerShell (Linux'ta `\` yerine `/` kullanın):

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
ruff format --check .
ruff check . --output-format json --output-file reports\ruff.json
coverage run manage.py test -v 2 --results-json reports\unit-results.json
coverage report
coverage json -q -o reports\coverage.json
```

Üretim profili denetimi (PowerShell):

```powershell
$env:DJANGO_ENV = "production"
$env:DJANGO_ALLOWED_HOSTS = "sds07.example"
$env:DJANGO_SECRET_KEY = python -c "import secrets; print(secrets.token_urlsafe(50))"
python manage.py check --deploy --fail-level WARNING
Remove-Item Env:DJANGO_ENV, Env:DJANGO_ALLOWED_HOSTS, Env:DJANGO_SECRET_KEY
```

## 5. Temiz kurulum denetimi (TC-INST-01)

Linux/macOS'ta projenin temiz kopyasını temiz sanal ortamda kurup CI adımlarını koşar; sonuç günlüğün son satırındadır:

```bash
bash tools/install_check.sh python3.13 linux-py313 reports/install-check-linux-py313.log
```

Tarayıcı (E2E) testleri Hafta 2'de eklenir.

## 6. RTM ve test sonuç tablosu

```powershell
python tools\build_rtm.py --week 1 --strict `
  --results reports\unit-results.json docs\evidence\hafta-01\manual-checks.json `
  --coverage reports\coverage.json --ruff reports\ruff.json
```

Çıktılar: `docs/RTM.md` ve `docs/TEST_RESULTS.md`. `--week 1`, 1. haftadan sonraya planlanan gereksinim ve testleri "PLANLANDI" olarak gösterir.

## 7. İlk commit ve GitHub (kullanıcı tarafından yapılacak)

```powershell
git init -b main
git add .
git commit -m "feat: Hafta 1 - proje iskeleti, ayar profilleri, kullanıcı modeli, testler ve CI"
git tag hafta-1
git remote add origin https://github.com/wordeus/sds07-servis-masasi.git
git push -u origin main --tags
```

Push sonrası GitHub'da **Actions** sekmesinde "CI" iş akışının dört işi (Ubuntu/Windows × Python 3.12/3.13) koşmalıdır. Sonuç TC-CI-01'in kanıtıdır; bağlantısını rapora ve `docs/PROJECT_STATE.md` dosyasına ekleyin.

## 8. Üretim profili ortam değişkenleri

| Değişken | Zorunlu | Açıklama |
|---|---|---|
| `DJANGO_ENV=production` | Evet | Üretim profilini açar; DEBUG kapalı olur |
| `DJANGO_SECRET_KEY` | Evet | En az 50 karakterlik rastgele anahtar |
| `DJANGO_ALLOWED_HOSTS` | Evet | Virgülle ayrılmış alan adları |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Gerekirse | Ör. `https://sds07.example` |
| `DJANGO_SECURE_SSL_REDIRECT` | Hayır | Varsayılan 1 |
| `DJANGO_SECURE_HSTS_SECONDS` | Hayır | Varsayılan 3600; HTTPS doğrulandıktan sonra 31536000 önerilir |
| `DJANGO_BEHIND_TLS_PROXY` | Hayır | Ters vekil TLS sonlandırıyorsa 1 |
| `DJANGO_SQLITE_PATH` | Hayır | SQLite dosya yolu |

Üretimde statik dosyaların sunulması (ör. `collectstatic` + web sunucusu) Hafta 1-3 kapsamında değildir.

## 9. İlerleme raporunun Word şablonundan üretilmesi

Dersin rapor şablonu depoda tutulmaz (öğretim elemanının belgesi). Şablonun yolunu verin:

```powershell
pip install -r requirements-docs.txt
python tools\build_report.py --template "C:\Ders\IKU_Iki_Haftalik_Ilerleme_Raporu_Sablonu.docx" `
  --content docs\reports\rapor-01.content.json --output docs\reports\Rapor-01_Hafta-1.docx
```

Araç şablonun üst bilgi bandını, bilgi tablosunu ve beş başlığını korur. Yalnız yer tutucuları ve tablo satırlarını doldurur. Köşeli parantezli alanlar sarı vurguludur ve sizin doldurmanız gerekir. Sonraki rapor için `rapor-01.content.json` dosyasını kopyalayıp içeriğini güncelleyin.
