# Kurulum ve çalıştırma kılavuzu

| Alan | Değer |
|---|---|
| Doküman kimliği | SDS07-INS |
| Sürüm | 0.3.1 (Hafta 3, teslim öncesi güncelleme) |
| Tarih | 26.11.2026 |
| Doğrulama | Linux'ta Python 3.12.13 ve 3.13.18 ile temiz kurulum yapıldı (TC-INST-01, `docs/evidence/hafta-03/install-check-*.log`). Windows 11'de Python 3.13.17 ile §2'deki adımlar `tools/install_check.ps1` ile koşuldu: BAŞARILI (26.11.2026, `docs/evidence/hafta-03/windows-2026-11-26/install-check-windows-py313.log`). |

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

Başlangıç kategorileri (Donanım, Yazılım, Ağ ve bağlantı, Hesap ve erişim, Diğer) `migrate` sırasında veri migration'ıyla oluşur (Hafta 3). Talepler `/talepler/`, kategori yönetimi `/kategoriler/` adresindedir.

**Çıktıyı dosyaya kaydedecekseniz** (ör. `> kayit.txt` veya `Tee-Object`), aynı pencerede önce `$env:PYTHONUTF8 = "1"` çalıştırın. Windows, yönlendirilmiş çıktıda varsayılan olarak cp1252 kod sayfasını kullanır; Türkçe "ş" ve "ı" karakterlerinde `UnicodeEncodeError` oluşur (RSK-25). Etkileşimli PowerShell penceresinde bu ayar gerekmez, zararı da yoktur. CI iş akışı bu ayarı kendisi yapar.

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

**Linux/macOS:** `pip install -r requirements-e2e.txt`, `playwright install chromium`, ardından `bash tools/run_e2e.sh`. Betik portun boş olduğunu denetler, geçici veritabanı ve rastgele parola kullanır, sunucuyu DEBUG kapalı başlatır, Hafta 2 ve Hafta 3 senaryolarını koşar ve sunucuyu kapatır.

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
# Sunucu DEBUG kapalı çalışır; özel hata sayfaları üretimdeki gibi görünür (KRR-15)
$env:DJANGO_DEBUG = "0"
python manage.py runserver 127.0.0.1:8765 --noreload --insecure
```

```powershell
# Pencere 2: testler
.\.venv\Scripts\Activate.ps1
$env:E2E_PASSWORD = "E2e-Gecici-Parola-2026"
python e2e\week2_auth_roles.py --base-url http://127.0.0.1:8765 --out-dir reports\screenshots --results-json reports\e2e-results.json
python e2e\week3_tickets.py --base-url http://127.0.0.1:8765 --out-dir reports\screenshots --results-json reports\e2e-week3-results.json
```

Hafta 3 betiği veritabanına talep ve kategori yazar; yalnız bu geçici E2E veritabanıyla koşun.

Bitince Pencere 1'de `Ctrl+C` ile sunucuyu durdurun. `Get-NetTCPConnection -LocalPort 8765 -ErrorAction SilentlyContinue` komutu boş dönmelidir. Açık kalan eski sunucu, testlerin eski kodla koşmasına yol açar (RSK-20).

### Temiz kurulum ve mutasyon denetimi

```bash
bash tools/install_check.sh python3.13 linux-py313 reports/install-check-linux-py313.log   # TC-INST-01
python tools/mutation_check.py --week 3 --out reports/mutation-check.md                    # testlerin hata yakalama yeteneği
```

## 6. RTM ve test sonuç tablosu

```powershell
python tools\build_rtm.py --week 3 --strict `
  --results reports\unit-results.json reports\e2e-results.json reports\e2e-week3-results.json docs\evidence\hafta-03\manual-checks.json `
  --coverage reports\coverage.json --ruff reports\ruff.json
```

Çıktılar: `docs/RTM.md` ve `docs/TEST_RESULTS.md`. `--week 3`, 3. haftadan sonraya planlanan gereksinim ve testleri "PLANLANDI" olarak gösterir.

## 7. GitHub'a gönderim (kullanıcı tarafından yapılacak)

Hafta 1, 2 ve 3 paketleri sırayla üç commit olarak gönderilir; her commit kendi haftasının etiketini alır (`hafta-1`, `hafta-2`, `hafta-3`). Commit tarihleri gerçek gönderim tarihidir; geriye tarih atılmaz. GitHub'da depo boş oluşturulmalıdır (README, `.gitignore` veya lisans eklemeden).

```powershell
# Paketleri açın: C:\Projeler\paketler altında sds07-servis-masasi-hafta-1, -hafta-2, -hafta-3 oluşur
Expand-Archive "$HOME\Downloads\SDS07_Hafta-1.zip" -DestinationPath C:\Projeler\paketler
Expand-Archive "$HOME\Downloads\SDS07_Hafta-2.zip" -DestinationPath C:\Projeler\paketler
Expand-Archive "$HOME\Downloads\SDS07_Hafta-3.zip" -DestinationPath C:\Projeler\paketler

# Depo klasörü
New-Item -ItemType Directory C:\Projeler\sds07-servis-masasi | Out-Null
cd C:\Projeler\sds07-servis-masasi
git init -b main
git config user.name "Burak Nigiz"
git config user.email "<GitHub e-posta adresiniz>"
git remote add origin https://github.com/<kullanici-adi>/sds07-servis-masasi.git

# Hafta 1
Copy-Item -Recurse -Force C:\Projeler\paketler\sds07-servis-masasi-hafta-1\* .
git add -A
git commit -m "feat: Hafta 1 - proje iskeleti, ayar profilleri, kullanıcı modeli, testler ve CI"
git tag hafta-1
git push -u origin main --tags
```

Her push'tan sonra GitHub'da **Actions** sekmesindeki "CI" koşusunun dört işi (Ubuntu/Windows × Python 3.12/3.13) bitene kadar bekleyin. İş akışı aynı dalda yeni koşu başlayınca eskisini iptal eder (`cancel-in-progress`); beklemeden yapılan ikinci push önceki haftanın koşusunu iptal eder.

```powershell
# Hafta 2: önce izlenen dosyaları kaldırın (silinen ve taşınan dosyalar böylece commit'e yansır)
git rm -r -q .
Get-ChildItem -Force          # yalnız .git kalmalı
Copy-Item -Recurse -Force C:\Projeler\paketler\sds07-servis-masasi-hafta-2\* .
git add -A
git commit -m "feat: Hafta 2 - giriş/çıkış, rol grupları, yetkilendirme, arayüz ve E2E"
git tag hafta-2
git push origin main --tags

# Hafta 2 koşusu bitince Hafta 3
git rm -r -q .
Get-ChildItem -Force          # yalnız .git kalmalı
Copy-Item -Recurse -Force C:\Projeler\paketler\sds07-servis-masasi-hafta-3\* .
git add -A
git commit -m "feat: Hafta 3 - talepler, kayıt bazlı erişim, kategoriler ve katmanlı yapı"
git tag hafta-3
git push origin main --tags

git log --oneline --decorate   # üç commit ve üç etiket görünmeli
```

Her koşunun sonucu TC-CI-01'in o haftaya ait kanıtıdır. Koşu bağlantılarını ve `git log --oneline --decorate` çıktısını kaydedin; rapora ve `docs/PROJECT_STATE.md` dosyasına eklenir. Bir iş kırmızı biterse sonucu değiştirmeye çalışmayın: o işin günlüğünü kaydedin, sonraki haftayı yine gönderin; hata yeni bir commit ile düzeltilir ve RISKS.md'ye yazılır.

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
  --content docs\reports\rapor-03.content.json --output docs\reports\Rapor-03_Hafta-3.docx
```

Araç şablonun üst bilgi bandını, bilgi tablosunu ve beş başlığını korur. Yalnız yer tutucuları ve tablo satırlarını doldurur. Köşeli parantezli alanlar sarı vurguludur ve sizin doldurmanız gerekir. Sonraki rapor için `rapor-03.content.json` dosyasını kopyalayıp içeriğini güncelleyin.
