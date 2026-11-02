# Kurulum ve çalıştırma kılavuzu

| Alan | Değer |
|---|---|
| Doküman kimliği | SDS07-INS |
| Sürüm | 0.2 (Hafta 2) |
| Tarih | 30.10.2026 |
| Doğrulama | Linux'ta Python 3.12.13 ve 3.13.18 ile temiz kurulum yapıldı (TC-INST-01, `docs/evidence/hafta-02/install-check-*.log`). **Windows adımları bu ortamda çalıştırılmadı (NOT RUN)**; ilk Windows kurulumunda sonucu `docs/evidence/hafta-02/` altına yeni dosya olarak ekleyin. |

## 1. Gereksinimler

- Python 3.12 veya 3.13 (Windows'ta python.org yükleyicisiyle kurup `py` başlatıcısını seçin)
- Git
- İnternet bağlantısı yalnız ilk paket kurulumunda gerekir. Bootstrap ve yazı tipi projeyle gelir.

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

# Veritabanını oluşturun (rol grupları bu adımda otomatik oluşur)
python manage.py migrate

# Sistem yöneticisi hesabı (yönetim sitesi ve rol atama için)
python manage.py createsuperuser

# İsteğe bağlı: her rol için demo kullanıcı (parola kurallara uymalı, en az 10 karakter)
$env:SDS07_DEMO_PASSWORD = "Kendi-Guclu-Parolaniz-2026"
python manage.py seed_demo_users

# Sunucuyu başlatın, tarayıcıda http://127.0.0.1:8000/ adresini açın
python manage.py runserver
```

Demo kullanıcıları: `demo.talep` (Talep Sahibi), `demo.destek` (Destek Personeli), `demo.yonetici` (Yönetici). Parola, `SDS07_DEMO_PASSWORD` ile verdiğiniz değerdir.

## 3. Linux / macOS

```bash
cd sds07-servis-masasi
python3.13 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py createsuperuser
SDS07_DEMO_PASSWORD='Kendi-Guclu-Parolaniz-2026' python manage.py seed_demo_users
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

## 5. Tarayıcı (E2E) testleri

Tarayıcı testleri Django testlerinin tamamlayıcısıdır. Ayrı bir veritabanı kullanın.

**Linux/macOS:** `pip install -r requirements-e2e.txt`, `playwright install chromium`, ardından `bash tools/run_e2e.sh`. Betik portun boş olduğunu denetler, geçici veritabanı ve rastgele parola kullanır, koşudan sonra sunucuyu kapatır.

**Windows (iki PowerShell penceresi):**

```powershell
# Pencere 1: hazırlık ve sunucu
.\.venv\Scripts\Activate.ps1
pip install -r requirements-e2e.txt
playwright install chromium
$env:DJANGO_SQLITE_PATH = "$PWD\e2e.sqlite3"
$env:E2E_PASSWORD = "E2e-Gecici-Parola-2026"
python manage.py migrate
python manage.py seed_demo_users --password $env:E2E_PASSWORD
python manage.py runserver 127.0.0.1:8765 --noreload
```

```powershell
# Pencere 2: testler
.\.venv\Scripts\Activate.ps1
$env:E2E_PASSWORD = "E2e-Gecici-Parola-2026"
python e2e\week2_auth_roles.py --base-url http://127.0.0.1:8765 --out-dir reports\screenshots --results-json reports\e2e-results.json
```

Bitince Pencere 1'de `Ctrl+C` ile sunucuyu durdurun. `Get-NetTCPConnection -LocalPort 8765 -ErrorAction SilentlyContinue` komutu boş dönmelidir. Açık kalan eski sunucu, testlerin eski kodla koşmasına yol açar (RSK-20).

### Temiz kurulum ve mutasyon denetimi

```bash
bash tools/install_check.sh python3.13 linux-py313 reports/install-check-linux-py313.log   # TC-INST-01
python tools/mutation_check.py --week 2 --out reports/mutation-check.md                    # testlerin hata yakalama yeteneği
```

## 6. RTM ve test sonuç tablosu

```powershell
python tools\build_rtm.py --week 2 --strict `
  --results reports\unit-results.json reports\e2e-results.json docs\evidence\hafta-02\manual-checks.json `
  --coverage reports\coverage.json --ruff reports\ruff.json
```

Çıktılar: `docs/RTM.md` ve `docs/TEST_RESULTS.md`. `--week 2`, 2. haftadan sonraya planlanan gereksinim ve testleri "PLANLANDI" olarak gösterir.

## 7. İlk commit ve GitHub (kullanıcı tarafından yapılacak)

```powershell
git init -b main
git add .
git commit -m "feat: Hafta 2 - giriş/çıkış, rol grupları, yetkilendirme, arayüz ve E2E"
git tag hafta-2
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
  --content docs\reports\rapor-02.content.json --output docs\reports\Rapor-02_Hafta-2.docx
```

Araç şablonun üst bilgi bandını, bilgi tablosunu ve beş başlığını korur. Yalnız yer tutucuları ve tablo satırlarını doldurur. Köşeli parantezli alanlar sarı vurguludur ve sizin doldurmanız gerekir. Sonraki rapor için `rapor-02.content.json` dosyasını kopyalayıp içeriğini güncelleyin.
