# Hafta 4 kanıtları (26.11.2026 koşuları)

Bu klasördeki dosyalar gerçek araç çıktılarıdır ve sonradan değiştirilmez (PRC-05). Zaman damgaları UTC'dir. Önceki haftaların kanıtları kendi klasörlerinde olduğu gibi korunur.

**Ortam:** Windows 11 Pro 10.0.26300, Python 3.13.17, Django 5.2.19, Playwright 1.65.2 (Chromium 159.0.8154.6). Linux ve Python 3.12 doğrulaması GitHub Actions'tadır (TC-CI-01).

| Dosya | İçerik | İlgili test / kayıt |
|---|---|---|
| `unit-results.json`, `unit-test-output.txt` | Django testleri (62 test, `-v 2`), TC kimlikli sonuçlar | TC-ASN-*, TC-CMT-*, TC-AUD-*, TC-ROLE-14 ve önceki haftaların testleri |
| `e2e-results.json`, `e2e-week3-results.json`, `e2e-week4-results.json` | Tarayıcı senaryoları: Hafta 2-3 gerileme (13) ve Hafta 4 (3) | TC-E2E-01..16 |
| `e2e-output.txt`, `screenshots/` | E2E konsol çıktısı ve ekran görüntüleri (`tools/run_e2e.ps1`) | TC-E2E-01..16 |
| `coverage.json`, `coverage-report.txt` | Üretim kodu satır+dal kapsamı: %95,04 (882/916 satır, 114/132 dal) | TC-QA-01 |
| `ruff.json`, `ruff-format.txt` | Statik analiz ve biçim denetimi: 0 bulgu | TC-QA-02 |
| `django-check.txt`, `check-deploy.txt` | `check`, `makemigrations --check`, üretim profilinde `check --deploy` | TC-CFG-03 |
| `install-check-windows-py313.log` | `tools/install_check.ps1` temiz kurulum günlüğü (62 test): BAŞARILI | TC-INST-01 |
| `mutation-check.md` | `tools/mutation_check.py --week 4`: 13 bilinçli hata, 13'ü yakalandı | Test etkinliği |
| `manual-checks.json` | TC-INST-01 özeti, TC-INS-01 incelemesi (onay bekliyor) | TC-INST-01, TC-INS-01 |
| `ci-github-actions-2026-11-26.json` | Hafta 4 commit'inin GitHub Actions koşusu (koşu #19, commit 816a611): Ubuntu ve Windows × Python 3.12/3.13, 4/4 iş başarılı; `tools/record_ci_run.sh 4` ile kaydedildi | TC-CI-01 |
| `bagimlilik-guncelleme-2026-11-26/` | Hafta 4 başındaki bağımlılık güncellemesinin doğrulaması (Django 5.2.19, sqlparse 0.6.1, araçlar; Windows'ta ilk E2E) | RSK-15, RSK-31 |

## Geliştirme sırasında bulunan sorunlar

İlk koşularda testler üç sorun yakaladı; düzeltmeden sonra aynı testler geçti. Ayrıntı: `docs/RISKS.md` RSK-28..RSK-30.

| Kayıt | İlk koşu | Sonuç |
|---|---|---|
| RSK-28 | TC-ASN-05 ERROR: kapanmış talepte işlem isteği sunucu hatası (500) | Düzeltildi, PASS |
| RSK-29 | TC-CMT-04 FAIL (3 alt test): kapanmış talebe yorum reddinin sebebi gösterilmiyordu | Düzeltildi, PASS |
| RSK-30 | TC-ARCH-02 FAIL: işlem görünümlerinde izin denetimi açıkça yazılmamıştı | Düzeltildi, PASS |

Bu ilk koşuların çıktısı ayrı dosya olarak saklanmadı; sorunlar ve düzeltmeler commit geçmişinde ve RISKS.md'de kayıtlıdır.
