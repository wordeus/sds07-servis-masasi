# Hafta 1 kanıtları (30.10.2026 koşuları)

Bu klasördeki dosyalar gerçek araç çıktılarıdır ve sonradan değiştirilmez (PRC-05). Zaman damgaları UTC'dir.

| Dosya | İçerik | İlgili test / kayıt |
|---|---|---|
| `unit-results.json`, `unit-test-output.txt` | Django testleri (8 test, `-v 2`), TC kimlikli sonuçlar | TC-CFG-*, TC-SEC-01, TC-QA-03, TC-QA-04 |
| `coverage.json`, `coverage-report.txt` | Üretim kodu satır+dal kapsamı | TC-QA-01 |
| `ruff.json`, `ruff-format.txt` | Statik analiz ve biçim denetimi | TC-QA-02 |
| `django-check.txt` | `manage.py check` ve `makemigrations --check` | - |
| `check-deploy.txt` | Üretim profilinde `check --deploy --fail-level WARNING` | TC-CFG-03, NFR-04 |
| `check-deploy-susturmasiz.txt` | Aynı denetim, gerekçeli susturma kaldırılarak (W021 görünür) | RSK-04 |
| `install-check-linux-py312.log`, `install-check-linux-py313.log` | `tools/install_check.sh` temiz kurulum günlükleri | TC-INST-01 |
| `manual-checks.json` | TC-INST-01 özeti, TC-INS-01 incelemesi, TC-CI-01 (NOT RUN) | TC-INST-01, TC-INS-01, TC-CI-01 |
| `rtm-ozet-hatasi-duzeltme-oncesi.txt` | RTM özetinde "NOT RUN"ın "NOT" sayıldığı ilk üretim çıktısı | RSK-06 |
| `tc-qa-04-hatali-kodla.txt` | Hata kopyada geri getirilince TC-QA-04'ün FAIL verdiği koşu | RSK-06, TC-QA-04 |
