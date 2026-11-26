# Hafta 4 kanıtları: bağımlılık güncellemesi (26.11.2026)

Bu klasördeki dosyalar gerçek araç çıktılarıdır ve sonradan değiştirilmez (PRC-05). Zaman damgaları UTC'dir.

**Ortam:** Windows 11 Pro 10.0.26300, Python 3.13.17. **Kod:** `main` (hafta-3 sonrası README ve iş akışı değişiklikleri) + bağımlılık güncellemesi. Uygulama kodu değişmedi.

| Paket | Önceki | Yeni | PyPI yayımlanma (UTC) | Not |
|---|---|---|---|---|
| Django | 5.2.18 | 5.2.19 | 2026-11-03 | 5.2 LTS güvenlik yaması (5 CVE) |
| sqlparse | 0.6.0 | 0.6.1 | 2026-11-01 | 2 güvenlik düzeltmesi; projenin son sürümü, bakımı sona erdi |
| coverage | 7.17.0 | 7.17.4 | 2026-11-20 | Yama |
| ruff | 0.17.3 | 0.17.6 | 2026-11-19 | Yama; yeni bulgu yok |
| playwright | 1.63.0 | 1.65.2 | 2026-11-14 | Chromium 159.0.8154.6; işlemler artık `inert` öğeyi bekliyor |

| Dosya | İçerik | Sonuç |
|---|---|---|
| `unit-results.json`, `unit-test-output.txt` | Django testleri (`-v 2`) | 49/49 PASS |
| `coverage.json`, `coverage-report.txt` | Üretim kodu kapsamı | %94,08 (önceki %94,21; fark yalnız `config/test_runner.py` 126-128 satırının coverage 7.17.4'te dal yerine satır olarak sayılmasından) |
| `ruff.json`, `ruff-format.txt` | Statik analiz ve biçim | 0 bulgu |
| `django-check.txt`, `check-deploy.txt` | `check`, `makemigrations --check`, üretim profilinde `check --deploy` | Sorun yok (1 gerekçeli susturma, W021) |
| `e2e-results.json`, `e2e-week3-results.json`, `e2e-output.txt`, `screenshots/` | Tarayıcı senaryoları, Windows'ta ilk koşu (INSTALL §5 adımları; geçici veritabanı, rastgele parola, DEBUG kapalı sunucu) | 13/13 PASS (TC-E2E-01..13) |
| `pip-freeze.txt` | Koşu ortamındaki paket sürümleri | - |

`e2e-output.txt` PowerShell 5.1 `Tee-Object` ile UTF-16 yazıldı; diğer dosyalarla aynı biçimde olması için içerik değiştirilmeden UTF-8'e çevrildi.
