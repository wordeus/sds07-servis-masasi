# Faz 5 kanıtları (26.11.2026 koşuları)

Bu klasördeki dosyalar gerçek araç çıktılarıdır ve sonradan değiştirilmez (PRC-05). Zaman damgaları UTC'dir.

**Ortam:** Windows 11 Pro 10.0.26300, Python 3.13.17, Django 5.2.19, Playwright 1.65.2 (Chromium 159.0.8154.6). Linux ve Python 3.12 doğrulaması GitHub Actions'tadır (TC-CI-01).

| Dosya | İçerik | İlgili test / kayıt |
|---|---|---|
| `unit-results.json`, `unit-test-output.txt` | Django testleri (69 test, `-v 2`) | TC-WF-*, TC-ROLE-15 ve önceki haftaların testleri |
| `e2e-results.json`, `e2e-week3-results.json`, `e2e-week4-results.json`, `e2e-week5-results.json` | Tarayıcı senaryoları: Hafta 2-4 gerileme (16) ve Faz 5 (2) | TC-E2E-01..18 |
| `e2e-output.txt`, `screenshots/` | E2E konsol çıktısı ve ekran görüntüleri (`tools/run_e2e.ps1`) | TC-E2E-01..18 |
| `coverage.json`, `coverage-report.txt` | Üretim kodu kapsamı: %95,03 (967/1.004 satır, 143/164 dal) | TC-QA-01 |
| `ruff.json`, `ruff-format.txt` | Statik analiz ve biçim: 0 bulgu | TC-QA-02 |
| `django-check.txt`, `check-deploy.txt` | `check`, `makemigrations --check`, üretim profilinde `check --deploy` | TC-CFG-03 |
| `install-check-windows-py313.log` | `tools/install_check.ps1` temiz kurulum günlüğü (69 test): BAŞARILI | TC-INST-01 |
| `mutation-check.md` | `tools/mutation_check.py --week 5`: 18 bilinçli hata, 18'i yakalandı | Test etkinliği |
| `manual-checks.json` | TC-INST-01 özeti; Hafta 3-4 TC-INS-01 onayı (Burak Nigiz, 26.11.2026); Faz 5 TC-INS-01 incelemesi (onay bekliyor) | TC-INST-01, TC-INS-01 |
| `ci-github-actions-2026-11-26.json` | Faz 5 commit'inin GitHub Actions koşusu (koşu #23, commit 8b752e4): Ubuntu ve Windows × Python 3.12/3.13, 4/4 iş başarılı | TC-CI-01 |


## Geliştirme sırasında bulunan sorunlar

| Kayıt | İlk koşu | Sonuç |
|---|---|---|
| RSK-33 | Mutasyon denetimi 17/18: M18 (başkasının talebini kapatma) yakalanmadı; test açığı | TC-WF-04'e servis denetimi eklendi; 18/18 |
| RSK-34 | TC-E2E-18 FAIL: rozet kontrastı listede ölçülüyordu, listede yeterli durum yoktu (test tasarımı) | Ölçüm panel özetine taşındı; PASS |

Ayrıca mutasyon M1'in hedef satırı Faz 5'te değiştiği için araç ilk koşuda bu mutasyonu uygulayamadı ("metin bulunamadı"); M1 yeni satıra göre güncellendi. Bu ilk koşuların çıktısı ayrı dosya olarak saklanmadı; ayrıntı `docs/RISKS.md` ve commit geçmişindedir.
