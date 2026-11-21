# Hafta 3 kanıtları (30.10.2026 koşuları)

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
| `tc-cat-01-turkce-harf-duzeltme-oncesi.txt` | Türkçe büyük harfli kopya adlar eklenince TC-CAT-01'in düzeltme öncesi koşusu (4 FAIL) | RSK-21 |
| `build-report-esdegerlik.txt` | Bölünen rapor aracının eski araçla bayt bayt aynı çıktı ürettiğinin karşılaştırması | RSK-07 |

## `teslim-oncesi/`

GitHub'a gönderimden önce yapılan depo dışlama (`.gitignore`) denetimi ve Windows çıktı kodlaması simülasyonu: bulunan hatalar, düzeltmeleri ve yeniden denetim (RSK-24, RSK-25). Ayrıntı: `teslim-oncesi/README.md`.

## `ilk-denemeler/`

| Dosya | İçerik | Kayıt |
|---|---|---|
| `e2e-week3-ilk-kosu-debug-404.json` | Hafta 3 E2E'nin ilk koşusu: sunucu DEBUG açıkken TC-E2E-11 FAIL | RSK-23 |
| `e2e-kesif-giris-iptali.txt`, `e2e-kesif-giris-iptali.png` | Tarayıcı keşif koşusunda girişin iptal olması (konsol çıktısından aktarılan satırlar ve o anki ekran) | RSK-22 |
