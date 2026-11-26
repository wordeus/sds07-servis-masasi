# Hafta 3 kanıtları (30.10.2026 koşuları; CI 21.11.2026; Windows 26.11.2026)

Bu klasördeki dosyalar gerçek araç çıktılarıdır ve sonradan değiştirilmez (PRC-05). Zaman damgaları UTC'dir. Hafta 1 ve Hafta 2 kanıtları `../hafta-01/` ve `../hafta-02/` klasörlerinde olduğu gibi korunur.

| Dosya | İçerik | İlgili test / kayıt |
|---|---|---|
| `unit-results.json`, `unit-test-output.txt` | Django testleri (49 test, `-v 2`), TC kimlikli sonuçlar | TC-TKT-*, TC-CAT-*, TC-ARCH-*, TC-ROLE-13 ve önceki haftaların testleri |
| `e2e-results.json` | Hafta 2 tarayıcı senaryolarının Hafta 3 kodu üzerinde gerileme koşusu (9 senaryo) | TC-E2E-01..09 |
| `e2e-week3-results.json` | Hafta 3 tarayıcı senaryoları (4 senaryo) | TC-E2E-10..13 |
| `e2e-output.txt`, `screenshots/` | E2E konsol çıktısı ve ekran görüntüleri (01-09 Hafta 2, 10-13 Hafta 3) | TC-E2E-01..13 |
| `coverage.json`, `coverage-report.txt` | Üretim kodu satır+dal kapsamı | TC-QA-01 |
| `ruff.json`, `ruff-format.txt` | Statik analiz ve biçim denetimi | TC-QA-02 |
| `django-check.txt` | `manage.py check` ve `makemigrations --check` | - |
| `check-deploy.txt` | Üretim profilinde `check --deploy --fail-level WARNING` | TC-CFG-03 |
| `install-check-linux-py312.log`, `install-check-linux-py313.log` | `tools/install_check.sh` temiz kurulum günlükleri (49 test) | TC-INST-01 |
| `mutation-check.md` | `tools/mutation_check.py`: bilinçli 8 hata, 49 testlik takım | Test etkinliği |
| `manual-checks.json` | TC-INST-01 özeti, TC-INS-01 incelemesi, TC-CI-01 (NOT RUN) | TC-INST-01, TC-INS-01, TC-CI-01 |
| `ci-github-actions-2026-11-21.json` | Hafta 3 commit'inin GitHub Actions koşusu (koşu #5, commit aa17057): Ubuntu ve Windows × Python 3.12/3.13, 4/4 iş başarılı; GitHub API'den 26.11.2026'da okundu | TC-CI-01, RSK-05 |
| `tc-cat-01-turkce-harf-duzeltme-oncesi.txt` | Türkçe büyük harfli kopya adlar eklenince TC-CAT-01'in düzeltme öncesi koşusu (4 FAIL) | RSK-21 |
| `build-report-esdegerlik.txt` | Bölünen rapor aracının eski araçla bayt bayt aynı çıktı ürettiğinin karşılaştırması | RSK-07 |

## `windows-2026-11-26/`

İlk Windows koşusu (26.11.2026, Windows 11 Pro, Python 3.13.17). Kod: `hafta-3` etiketi ve bu koşuda bulunan RSK-26 düzeltmesi (`tools/build_rtm.py`, TC-QA-04'e yol denetimi). Ürün kodu (`servicedesk/` uygulama dosyaları, şablonlar, ayarlar) değişmedi. Tarayıcı (E2E) testleri Windows'ta koşulmadı; E2E sonuçları yukarıdaki Linux koşusundandır.

| Dosya | İçerik | İlgili test / kayıt |
|---|---|---|
| `unit-results.json`, `unit-test-output.txt` | Django testleri (49 test, `-v 2`), Windows | Tüm Django TC'leri |
| `coverage.json`, `coverage-report.txt` | Üretim kodu kapsamı (%94,21; Linux ile aynı) | TC-QA-01 |
| `ruff.json`, `ruff-format.txt` | Statik analiz ve biçim denetimi (0 bulgu) | TC-QA-02 |
| `django-check.txt`, `check-deploy.txt` | `check`, `makemigrations --check`, üretim profilinde `check --deploy` | TC-CFG-03 |
| `install-check-windows-py313.log`, `manual-checks.json` | `tools/install_check.ps1` temiz kurulum günlüğü ve özeti: BAŞARILI | TC-INST-01, NFR-11 |
| `tc-qa-04-yol-duzeltme-oncesi.txt` | RTM üreticisinin düzeltme öncesi koduyla TC-QA-04: FAIL (ters bölülü yol) | RSK-26 |

## `teslim-oncesi/`

GitHub'a gönderimden önce yapılan depo dışlama (`.gitignore`) denetimi ve Windows çıktı kodlaması simülasyonu: bulunan hatalar, düzeltmeleri ve yeniden denetim (RSK-24, RSK-25). Ayrıntı: `teslim-oncesi/README.md`.

## `ilk-denemeler/`

| Dosya | İçerik | Kayıt |
|---|---|---|
| `e2e-week3-ilk-kosu-debug-404.json` | Hafta 3 E2E'nin ilk koşusu: sunucu DEBUG açıkken TC-E2E-11 FAIL | RSK-23 |
| `e2e-kesif-giris-iptali.txt`, `e2e-kesif-giris-iptali.png` | Tarayıcı keşif koşusunda girişin iptal olması (konsol çıktısından aktarılan satırlar ve o anki ekran) | RSK-22 |
