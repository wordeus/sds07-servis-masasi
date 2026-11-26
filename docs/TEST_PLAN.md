# SDS-07 Test planı (doğrulama ve geçerleme)

| Alan | Değer |
|---|---|
| Doküman kimliği | SDS07-STP |
| Sürüm | 0.3.1 (Hafta 3, teslim öncesi güncelleme) |
| Tarih | 26.11.2026 |
| Hazırlayan | Burak Nigiz (2100002062) |
| İlişkili standart | IEEE 1012-2024 (V&V), ISO/IEC/IEEE 12207:2026 6.4.9 Verification ve 6.4.11 Validation |

Test kataloğu: [traceability/tests.csv](traceability/tests.csv). Gerçek sonuçlar: [TEST_RESULTS.md](TEST_RESULTS.md) ve [RTM.md](RTM.md). Bu iki dosya `tools/build_rtm.py --week 3` ile üretilir; elle sonuç yazılmaz.

## 1. Kapsam

Hafta 1 (MOD-CFG, kullanıcı modeli), Hafta 2 (MOD-AUTH, MOD-ROLE, MOD-UI) ve Hafta 3 (MOD-TICKET: talep, kayıt bazlı erişim, kategori; katmanlı yapı). Gereksinimler: FR-01..FR-15, NFR-01..NFR-12, NFR-16. Önceki haftaların testleri her pakette yeniden koşulur (gerileme). Sonraki haftaların testleri kendi haftalarında kataloğa eklenecek.

## 2. Test seviyeleri ve araçları

| Seviye | Amaç | Araç | TC önekleri |
|---|---|---|---|
| Birim | Saf fonksiyonlar (rol çözümleme, ortam ayrıştırma, test koşucusu, RTM üretici) | Django test çatısı (`unittest`) | TC-ROLE-05, TC-CFG-05, TC-QA-03, TC-QA-04, TC-SEC-01 |
| Entegrasyon | Görünüm + middleware + veritabanı + şablon birlikte | Django test istemcisi | TC-AUTH-*, TC-ROLE-*, TC-SEED-*, TC-SEC-02/03, TC-CFG-01/04/06, TC-TKT-01..08, TC-CAT-01..03 |
| Sistem (yapılandırma) | Ayarların ayrı süreçte yüklenmesi, üretim profili | `subprocess` + `manage.py check --deploy` | TC-CFG-02, TC-CFG-03 |
| Sistem (E2E, geçerleme) | Gerçek tarayıcıda rol ve talep senaryoları, mobil, klavye, kontrast | Playwright (Chromium) | TC-E2E-01..13 |
| Statik analiz | Kod kalitesi, kapsam ölçümü, mimari kurallar (Python AST) | ruff, coverage.py, `ast` | TC-QA-01, TC-QA-02, TC-ARCH-01, TC-ARCH-02 |
| İnceleme | Kişisel veri asgarisi | Kod/şablon incelemesi | TC-INS-01 |
| Kurulum / CI | Temiz ortam kurulumu, işletim sistemi matrisi | `tools/install_check.sh`, GitHub Actions | TC-INST-01, TC-CI-01 |

Tarayıcı testleri Django testlerinin yerine geçmez; onların tamamlayıcısıdır. Yetki kuralları önce sunucu tarafında entegrasyon testleriyle, sonra gerçek kullanıcı akışında E2E ile doğrulanır.

## 3. IEEE 1012-2024 ile ilişkilendirilen V&V etkinlikleri

| Etkinlik | Hafta 3 uygulaması | Kanıt |
|---|---|---|
| Gereksinim izlenebilirlik analizi | Her aktif gereksinim ≥ 1 TC'ye bağlı. İzlenemeyen test veya testsiz gereksinim varsa RTM üretici `--strict` modunda başarısız olur. | RTM "Tutarlılık denetimi" bölümü |
| Arayüz ve tasarım değerlendirmesi | Rol matrisinin koddan üretilmesi ve SRS ile karşılaştırılması | SRS §4, `roles.py` |
| Kod analizi | ruff kuralları (güvenlik kuralları dahil), döngüsel karmaşıklık ölçümü | QUALITY_METRICS.md |
| Mimari değerlendirme | Katman kuralı ve erişim denetimi kaynak kod üzerinde otomatik denetlenir | TC-ARCH-01, TC-ARCH-02 |
| Yapılandırma denetimi | `check --deploy --fail-level WARNING` (üretim profili) | TC-CFG-03 |
| Konfigürasyon ve ortam denetimi (teslim öncesi) | Paketin boş bir git deposunda `git status --ignored` ile incelenmesi; CI komutlarının Windows'un yönlendirilmiş çıktı kodlaması taklit edilerek (`PYTHONIOENCODING=cp1252`) koşulması. İki hata bulundu (RSK-24, RSK-25). | `evidence/hafta-03/teslim-oncesi/` |
| Birim/entegrasyon testi | 49 otomatik test (Hafta 1-2'nin 35 testi dahil) | `evidence/hafta-03/unit-results.json` |
| Sistem testi (geçerleme) | 13 tarayıcı senaryosu (9'u Hafta 2 gerilemesi) | `evidence/hafta-03/e2e-results.json`, `e2e-week3-results.json`, `screenshots/` |
| Test araçlarının doğrulanması | Koşucunun her sonuç türünü doğru kaydettiği (TC-QA-03) ve RTM üreticinin durumları doğru saydığı (TC-QA-04) | TC-QA-03, TC-QA-04 |
| Testlerin etkinliği | Mutasyon denetimi (`tools/mutation_check.py`): bilinçli 8 hatanın 8'i 49 testlik takımla yakalandı (4'ü Hafta 3 için yeni) | `evidence/hafta-03/mutation-check.md` |

## 4. Giriş ve çıkış ölçütleri

**Giriş:** Gereksinim SRS'de kimlikli ve kabul kriterli; TC katalogda tanımlı; geliştirme ortamı `requirements-dev.txt` ile kurulmuş.

**Çıkış (haftalık tamamlanma tanımı):**

1. Aktif haftanın ve önceki haftaların tüm otomatik testleri PASS.
2. Üretim kodu kapsamı ≥ %80 (NFR-09).
3. ruff 0 bulgu (NFR-10), `check --deploy` geçer (NFR-04).
4. RTM `--week N --strict` modda sorunsuz üretilir.
5. NOT RUN kalan testler gerekçesiyle PROJECT_STATE ve rapora yazılır.

## 5. Test ortamı (Hafta 3 gerçek koşu, 30.10.2026)

| Öğe | Değer |
|---|---|
| İşletim sistemi | Linux (bulut çalışma alanı); Windows 11 Pro 10.0.26300 (26.11.2026, Django testleri ve temiz kurulum) |
| Python | 3.13.18 (ana koşu); 3.12.13 ve 3.13.18 (temiz kurulum denetimi, Linux); 3.13.17 (Windows) |
| Django | 5.2.18 |
| Tarayıcı | Chromium 153.0.8010.12 (Playwright 1.63.0) |
| Veritabanı | SQLite (testlerde bellek içi; E2E'de geçici dosya) |
| E2E sunucusu | `runserver --insecure`, `DJANGO_DEBUG=0` (özel hata sayfaları üretimdeki gibi; KRR-15) |
| Windows | Elle: Windows 11, Python 3.13.17, 49/49 PASS ve temiz kurulum BAŞARILI (26.11.2026, `evidence/hafta-03/windows-2026-11-26/`). CI: koşu #5'te windows-latest × 3.12/3.13 başarılı. Tarayıcı testleri Windows'ta koşulmadı. |

## 6. Çalıştırma

```bash
# Birim + entegrasyon (+ kapsam)
coverage run manage.py test -v 2 --results-json reports/unit-results.json
coverage report
coverage json -q -o reports/coverage.json
ruff check . --output-format json --output-file reports/ruff.json

# Tarayıcı (Linux/macOS); Windows için docs/INSTALL.md §5
bash tools/run_e2e.sh

# Temiz kurulum ve mutasyon denetimi
bash tools/install_check.sh python3.13 linux-py313 reports/install-check-linux-py313.log
# Windows (PowerShell): powershell -ExecutionPolicy Bypass -File tools\install_check.ps1 3.13 windows-py313 reports\install-check-windows-py313.log
python tools/mutation_check.py --week 3 --out reports/mutation-check.md

# RTM ve test sonuç tablosu
python tools/build_rtm.py --week 3 --strict \
  --results reports/unit-results.json reports/e2e-results.json reports/e2e-week3-results.json \
            docs/evidence/hafta-03/manual-checks.json docs/evidence/hafta-03/ci-github-actions-2026-11-21.json \
            docs/evidence/hafta-03/windows-2026-11-26/unit-results.json docs/evidence/hafta-03/windows-2026-11-26/manual-checks.json \
  --coverage reports/coverage.json --ruff reports/ruff.json
```

## 7. Hafta 3 sonuç özeti

| Grup | Planlanan | Koşulan | PASS | FAIL | NOT RUN |
|---|---|---|---|---|---|
| Birim + entegrasyon + sistem + mimari (Django) | 49 | 49 | 49 | 0 | 0 |
| E2E (Chromium) | 13 | 13 | 13 | 0 | 0 |
| Statik analiz / ölçüm (TC-QA-01/02) | 2 | 2 | 2 | 0 | 0 |
| Kurulum (TC-INST-01: Linux 3.12 ve 3.13, Windows 3.13) | 1 | 1 | 1 | 0 | 0 |
| İnceleme (TC-INS-01) | 1 | 1 | 1 | 0 | 0 |
| CI matrisi (TC-CI-01, koşu #5) | 1 | 1 | 1 | 0 | 0 |

Katalogda 67 test vardır: 67 PASS. Django ve E2E sayıları 30.10.2026 koşusuna, TC-CI-01 21.11.2026 GitHub Actions koşusuna, Windows sonuçları 26.11.2026 koşusuna aittir; güncel durum her zaman [TEST_RESULTS.md](TEST_RESULTS.md) dosyasındadır.

## 8. Bilinen sınırlar

- E2E yalnız Chromium'da koşuldu; Firefox Hafta 11-12'de (NFR-15).
- Kontrast ölçümü seçili metin öğelerinde yapıldı; tüm ekranların taraması Hafta 11-12'de.
- TC-INS-01 incelemesinin Burak Nigiz tarafından tekrarlanıp onaylanması gerekir.
- Proje tek kişilik olduğundan bağımsız V&V yapılamıyor (RSK-03).
- Windows çıktı kodlaması düzeltmesi (`PYTHONUTF8=1`, RSK-25) CI'daki Windows işlerinde ve 26.11.2026'daki elle Windows koşusunda doğrulandı. Tarayıcı (E2E) testleri Windows'ta koşulmadı.
- Performans ölçümü (NFR-13) yapılmadı: ÖLÇÜLMEDİ (Hafta 11-12).
