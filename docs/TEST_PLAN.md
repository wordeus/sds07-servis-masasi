# SDS-07 Test planı (doğrulama ve geçerleme)

| Alan | Değer |
|---|---|
| Doküman kimliği | SDS07-STP |
| Sürüm | 0.1 (Hafta 1) |
| Tarih | 30.10.2026 |
| Hazırlayan | Burak Nigiz (2100002062) |
| İlişkili standart | IEEE 1012-2024 (V&V), ISO/IEC/IEEE 12207:2026 6.4.9 Verification ve 6.4.11 Validation |

Test kataloğu: [traceability/tests.csv](traceability/tests.csv). Gerçek sonuçlar: [TEST_RESULTS.md](TEST_RESULTS.md) ve [RTM.md](RTM.md). Bu iki dosya `tools/build_rtm.py --week 1` ile üretilir; elle sonuç yazılmaz.

## 1. Kapsam

Hafta 1: MOD-CFG (ayar profilleri, güvenli üretim yapılandırması, saat dilimi, test altyapısı) ve MOD-AUTH veri modeli (özel kullanıcı modeli). Gereksinimler: NFR-01, NFR-04, NFR-05, NFR-09, NFR-10, NFR-11, NFR-12.

Hafta 2'nin 36 testi (TC-AUTH, TC-ROLE, TC-SEED, TC-SEC-02/03, TC-CFG-04, TC-E2E) katalogda tanımlıdır ve RTM'de "PLANLANDI" görünür. Kabul kriterleri SRS §7.1'dedir.

## 2. Test seviyeleri ve araçları

| Seviye | Amaç | Araç | Hafta 1 TC'leri |
|---|---|---|---|
| Birim | Saf fonksiyonlar: ortam değişkeni ayrıştırma, parola kuralları, test koşucusu, RTM üretici | Django test çatısı (`unittest`) | TC-CFG-05, TC-SEC-01, TC-QA-03, TC-QA-04 |
| Entegrasyon | Ayar + veritabanı + şablon + yönetim sitesi birlikte | Django test istemcisi | TC-CFG-01, TC-CFG-06 |
| Sistem (yapılandırma) | Ayarların ayrı süreçte yüklenmesi, üretim profili | `subprocess` + `manage.py check --deploy` | TC-CFG-02, TC-CFG-03 |
| Statik analiz | Kod kalitesi ve kapsam ölçümü | ruff, coverage.py | TC-QA-01, TC-QA-02 |
| İnceleme | Kişisel veri asgarisi | Kod incelemesi | TC-INS-01 |
| Kurulum / CI | Temiz ortam kurulumu, işletim sistemi matrisi | `tools/install_check.sh`, GitHub Actions | TC-INST-01, TC-CI-01 |
| Sistem (E2E, geçerleme) | Gerçek tarayıcıda rol senaryoları | Playwright (Chromium) | Hafta 2 |

## 3. IEEE 1012-2024 ile ilişkilendirilen V&V etkinlikleri

| Etkinlik | Hafta 1 uygulaması | Kanıt |
|---|---|---|
| Gereksinim izlenebilirlik analizi | Her aktif gereksinim ≥ 1 TC'ye bağlı. İzlenemeyen test veya testsiz aktif gereksinim varsa RTM üretici `--strict` modunda başarısız olur. | RTM "Tutarlılık denetimi" bölümü |
| Kod analizi | ruff kuralları (güvenlik kuralları dahil), döngüsel karmaşıklık ölçümü | [QUALITY_METRICS.md](QUALITY_METRICS.md) |
| Yapılandırma denetimi | `check --deploy --fail-level WARNING` (üretim profili); gerekçeli susturma ayrıca susturmasız koşuyla belgelendi | TC-CFG-03, `evidence/hafta-01/check-deploy*.txt` |
| Birim/entegrasyon testi | 8 otomatik test | `evidence/hafta-01/unit-results.json` |
| Test araçlarının doğrulanması | Koşucunun her sonuç türünü doğru kaydettiği (TC-QA-03) ve RTM üreticinin durumları doğru saydığı (TC-QA-04) | `evidence/hafta-01/tc-qa-04-hatali-kodla.txt` |
| Kurulum doğrulaması | Temiz kopya, temiz sanal ortam, CI adımlarının yerel eşdeğeri | `evidence/hafta-01/install-check-*.log` |

Sistem testi (E2E) ve mutasyon denetimi Hafta 2'de eklenir.

## 4. Giriş ve çıkış ölçütleri

**Giriş:** Gereksinim SRS'de kimlikli ve kabul kriterli; TC katalogda tanımlı; geliştirme ortamı `requirements-dev.txt` ile kurulmuş.

**Çıkış (haftalık tamamlanma tanımı):**

1. Aktif haftanın tüm otomatik testleri PASS.
2. Üretim kodu kapsamı ≥ %80 (NFR-09).
3. ruff 0 bulgu (NFR-10), `check --deploy` geçer (NFR-04).
4. RTM `--week N --strict` modda sorunsuz üretilir.
5. NOT RUN kalan testler gerekçesiyle PROJECT_STATE ve rapora yazılır.

## 5. Test ortamı (Hafta 1 gerçek koşu, 30.10.2026)

| Öğe | Değer |
|---|---|
| İşletim sistemi | Linux (bulut çalışma alanı) |
| Python | 3.13.18 (ana koşu); 3.12.13 ve 3.13.18 (temiz kurulum denetimi) |
| Django | 5.2.18 |
| Veritabanı | SQLite (testlerde bellek içi) |
| Windows | **NOT RUN** (CI matrisinde tanımlı, depo yok) |

## 6. Çalıştırma

```bash
# Birim + entegrasyon (+ kapsam)
coverage run manage.py test -v 2 --results-json reports/unit-results.json
coverage report
coverage json -q -o reports/coverage.json
ruff check . --output-format json --output-file reports/ruff.json

# Temiz kurulum (TC-INST-01)
bash tools/install_check.sh python3.13 linux-py313 reports/install-check-linux-py313.log

# RTM ve test sonuç tablosu
python tools/build_rtm.py --week 1 --strict \
  --results reports/unit-results.json docs/evidence/hafta-01/manual-checks.json \
  --coverage reports/coverage.json --ruff reports/ruff.json
```

## 7. Hafta 1 sonuç özeti

| Grup | Planlanan | Koşulan | PASS | FAIL | NOT RUN |
|---|---|---|---|---|---|
| Birim + entegrasyon + sistem (Django) | 8 | 8 | 8 | 0 | 0 |
| Statik analiz / ölçüm (TC-QA-01/02) | 2 | 2 | 2 | 0 | 0 |
| Kurulum (TC-INST-01, Linux 3.12 ve 3.13) | 1 | 1 | 1 | 0 | 0 |
| İnceleme (TC-INS-01) | 1 | 1 | 1 | 0 | 0 |
| CI matrisi (TC-CI-01) | 1 | 0 | 0 | 0 | 1 |

Katalogdaki 49 testin 36'sı Hafta 2'ye planlıdır. Sayılar 30.10.2026 koşusuna aittir; güncel durum her zaman [TEST_RESULTS.md](TEST_RESULTS.md) dosyasındadır.

## 8. Bilinen sınırlar

- Tarayıcı testleri yoktur; arayüz Hafta 2'de eklenir.
- TC-INS-01 incelemesinin Burak Nigiz tarafından tekrarlanıp onaylanması gerekir.
- Proje tek kişilik olduğundan bağımsız V&V yapılamıyor (RSK-03).
- Performans ölçümü (NFR-13) yapılmadı: ÖLÇÜLMEDİ (Hafta 11-12).
