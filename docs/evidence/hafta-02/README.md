# Hafta 2 kanıtları (30.10.2026 koşuları)

Bu klasördeki dosyalar gerçek araç çıktılarıdır ve sonradan değiştirilmez (PRC-05). Zaman damgaları UTC'dir. Hafta 1 kanıtları `../hafta-01/` klasöründe olduğu gibi korunur.

| Dosya | İçerik | İlgili test / kayıt |
|---|---|---|
| `unit-results.json`, `unit-test-output.txt` | Django testleri (35 test, `-v 2`), TC kimlikli sonuçlar | TC-AUTH-*, TC-ROLE-*, TC-SEED-*, TC-SEC-*, TC-CFG-*, TC-QA-03/04 |
| `e2e-results.json`, `e2e-output.txt`, `screenshots/` | Tarayıcı testleri (Chromium, 9 senaryo) ve ekran görüntüleri | TC-E2E-01..09 |
| `coverage.json`, `coverage-report.txt` | Üretim kodu satır+dal kapsamı | TC-QA-01 |
| `ruff.json`, `ruff-format.txt` | Statik analiz ve biçim denetimi | TC-QA-02 |
| `django-check.txt` | `manage.py check` ve `makemigrations --check` | - |
| `check-deploy.txt` | Üretim profilinde `check --deploy --fail-level WARNING` | TC-CFG-03 |
| `install-check-linux-py312.log`, `install-check-linux-py313.log` | `tools/install_check.sh` temiz kurulum günlükleri | TC-INST-01 |
| `mutation-check.md` | `tools/mutation_check.py`: bilinçli 4 hata, 35 testlik takım | Test etkinliği |
| `manual-checks.json` | TC-INST-01 özeti, TC-INS-01 incelemesi, TC-CI-01 (NOT RUN) | TC-INST-01, TC-INS-01, TC-CI-01 |

## `ilk-denemeler/`: Hafta 1-2 geliştirme oturumunun özgün kayıtları

Bu dosyalar Hafta 1 ve Hafta 2 kodu aynı gün yazılırken (30.10.2026, haftalık paketlere ayırmadan önce) üretildi. İçlerinde o zamanki "Sprint" etiketleri ve eski dosya adları (`e2e/sprint1_smoke.py`) görülür; değiştirilmeden saklanmıştır.

| Dosya | İçerik | Kayıt |
|---|---|---|
| `ruff-ilk-kosu-13-bulgu.json` | Statik analizin ilk koşusu: 13 bulgu | RSK-17 |
| `install-check-linux-py312-ilk-deneme-basarisiz.log`, `install-check-linux-py313-ilk-deneme-basarisiz.log` | Temiz kurulumun başarısız ilk denemesi | RSK-18 |
| `e2e-regression-check-without-fix.json` | Mobil tablo düzeltmesi kaldırılınca TC-E2E-07'nin FAIL verdiği koşu | RSK-19 |
| `07-panel-mobil-360-duzeltme-oncesi.png` | Düzeltme öncesi 360 px panel: yetki tablosu kırpılıyor | RSK-19 |
