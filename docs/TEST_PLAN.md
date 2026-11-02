# SDS-07 Test planı (doğrulama ve geçerleme)

| Alan | Değer |
|---|---|
| Doküman kimliği | SDS07-STP |
| Sürüm | 0.2 (Hafta 2) |
| Tarih | 30.10.2026 |
| Hazırlayan | Burak Nigiz (2100002062) |
| İlişkili standart | IEEE 1012-2024 (V&V), ISO/IEC/IEEE 12207:2026 6.4.9 Verification ve 6.4.11 Validation |

Test kataloğu: [traceability/tests.csv](traceability/tests.csv). Gerçek sonuçlar: [TEST_RESULTS.md](TEST_RESULTS.md) ve [RTM.md](RTM.md). Bu iki dosya `tools/build_rtm.py --week 2` ile üretilir; elle sonuç yazılmaz.

## 1. Kapsam

Hafta 1 (MOD-CFG, kullanıcı modeli) ve Hafta 2 (MOD-AUTH, MOD-ROLE, MOD-UI). Gereksinimler: FR-01..FR-11, NFR-01..NFR-12. Hafta 1 testleri her pakette yeniden koşulur (gerileme). Sonraki haftaların testleri kendi haftalarında kataloğa eklenecek.

## 2. Test seviyeleri ve araçları

| Seviye | Amaç | Araç | TC önekleri |
|---|---|---|---|
| Birim | Saf fonksiyonlar (rol çözümleme, ortam ayrıştırma, test koşucusu, RTM üretici) | Django test çatısı (`unittest`) | TC-ROLE-05, TC-CFG-05, TC-QA-03, TC-QA-04, TC-SEC-01 |
| Entegrasyon | Görünüm + middleware + veritabanı + şablon birlikte | Django test istemcisi | TC-AUTH-*, TC-ROLE-*, TC-SEED-*, TC-SEC-02/03, TC-CFG-01/04/06 |
| Sistem (yapılandırma) | Ayarların ayrı süreçte yüklenmesi, üretim profili | `subprocess` + `manage.py check --deploy` | TC-CFG-02, TC-CFG-03 |
| Sistem (E2E, geçerleme) | Gerçek tarayıcıda rol senaryoları, mobil, klavye, kontrast | Playwright (Chromium) | TC-E2E-01..09 |
| Statik analiz | Kod kalitesi ve kapsam ölçümü | ruff, coverage.py | TC-QA-01, TC-QA-02 |
| İnceleme | Kişisel veri asgarisi | Kod/şablon incelemesi | TC-INS-01 |
| Kurulum / CI | Temiz ortam kurulumu, işletim sistemi matrisi | `tools/install_check.sh`, GitHub Actions | TC-INST-01, TC-CI-01 |

Tarayıcı testleri Django testlerinin yerine geçmez; onların tamamlayıcısıdır. Yetki kuralları önce sunucu tarafında entegrasyon testleriyle, sonra gerçek kullanıcı akışında E2E ile doğrulanır.

## 3. IEEE 1012-2024 ile ilişkilendirilen V&V etkinlikleri

| Etkinlik | Hafta 2 uygulaması | Kanıt |
|---|---|---|
| Gereksinim izlenebilirlik analizi | Her aktif gereksinim ≥ 1 TC'ye bağlı. İzlenemeyen test veya testsiz gereksinim varsa RTM üretici `--strict` modunda başarısız olur. | RTM "Tutarlılık denetimi" bölümü |
| Arayüz ve tasarım değerlendirmesi | Rol matrisinin koddan üretilmesi ve SRS ile karşılaştırılması | SRS §4, `roles.py` |
| Kod analizi | ruff kuralları (güvenlik kuralları dahil), döngüsel karmaşıklık ölçümü | QUALITY_METRICS.md |
| Yapılandırma denetimi | `check --deploy --fail-level WARNING` (üretim profili) | TC-CFG-03 |
| Birim/entegrasyon testi | 35 otomatik test (Hafta 1'in 8 testi dahil) | `evidence/hafta-02/unit-results.json` |
| Sistem testi (geçerleme) | 9 tarayıcı senaryosu | `evidence/hafta-02/e2e-results.json`, `screenshots/` |
| Test araçlarının doğrulanması | Koşucunun her sonuç türünü doğru kaydettiği (TC-QA-03) ve RTM üreticinin durumları doğru saydığı (TC-QA-04) | TC-QA-03, TC-QA-04 |
| Testlerin etkinliği | Mutasyon denetimi (`tools/mutation_check.py`): bilinçli 4 hatanın 4'ü 35 testlik takımla yakalandı | `evidence/hafta-02/mutation-check.md` |

## 4. Giriş ve çıkış ölçütleri

**Giriş:** Gereksinim SRS'de kimlikli ve kabul kriterli; TC katalogda tanımlı; geliştirme ortamı `requirements-dev.txt` ile kurulmuş.

**Çıkış (haftalık tamamlanma tanımı):**

1. Aktif haftanın ve önceki haftaların tüm otomatik testleri PASS.
2. Üretim kodu kapsamı ≥ %80 (NFR-09).
3. ruff 0 bulgu (NFR-10), `check --deploy` geçer (NFR-04).
4. RTM `--week N --strict` modda sorunsuz üretilir.
5. NOT RUN kalan testler gerekçesiyle PROJECT_STATE ve rapora yazılır.

## 5. Test ortamı (Hafta 2 gerçek koşu, 30.10.2026)

| Öğe | Değer |
|---|---|
| İşletim sistemi | Linux (bulut çalışma alanı) |
| Python | 3.13.18 (ana koşu); 3.12.13 ve 3.13.18 (temiz kurulum denetimi) |
| Django | 5.2.18 |
| Tarayıcı | Chromium 153.0.8010.12 (Playwright 1.63.0) |
| Veritabanı | SQLite (testlerde bellek içi; E2E'de geçici dosya) |
| Windows | **NOT RUN** (CI matrisinde tanımlı, depo yok) |

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
python tools/mutation_check.py --week 2 --out reports/mutation-check.md

# RTM ve test sonuç tablosu
python tools/build_rtm.py --week 2 --strict \
  --results reports/unit-results.json reports/e2e-results.json docs/evidence/hafta-02/manual-checks.json \
  --coverage reports/coverage.json --ruff reports/ruff.json
```

## 7. Hafta 2 sonuç özeti

| Grup | Planlanan | Koşulan | PASS | FAIL | NOT RUN |
|---|---|---|---|---|---|
| Birim + entegrasyon + sistem (Django) | 35 | 35 | 35 | 0 | 0 |
| E2E (Chromium) | 9 | 9 | 9 | 0 | 0 |
| Statik analiz / ölçüm (TC-QA-01/02) | 2 | 2 | 2 | 0 | 0 |
| Kurulum (TC-INST-01, Linux 3.12 ve 3.13) | 1 | 1 | 1 | 0 | 0 |
| İnceleme (TC-INS-01) | 1 | 1 | 1 | 0 | 0 |
| CI matrisi (TC-CI-01) | 1 | 0 | 0 | 0 | 1 |

Katalogda 49 test vardır: 48 PASS, 1 NOT RUN. Sayılar 30.10.2026 koşusuna aittir; güncel durum her zaman [TEST_RESULTS.md](TEST_RESULTS.md) dosyasındadır.

## 8. Bilinen sınırlar

- E2E yalnız Chromium'da koşuldu; Firefox Hafta 11-12'de (NFR-15).
- Kontrast ölçümü seçili metin öğelerinde yapıldı; tüm ekranların taraması Hafta 11-12'de.
- TC-INS-01 incelemesinin Burak Nigiz tarafından tekrarlanıp onaylanması gerekir.
- Proje tek kişilik olduğundan bağımsız V&V yapılamıyor (RSK-03).
- Performans ölçümü (NFR-13) yapılmadı: ÖLÇÜLMEDİ (Hafta 11-12).
