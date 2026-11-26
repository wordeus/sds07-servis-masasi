# SDS-07 Test planı (doğrulama ve geçerleme)

| Alan | Değer |
|---|---|
| Doküman kimliği | SDS07-STP |
| Sürüm | 0.5 (Faz 5, son sürüm) |
| Tarih | 26.11.2026 |
| Hazırlayan | Burak Nigiz (2100002062) |
| İlişkili standart | IEEE 1012-2024 (V&V), ISO/IEC/IEEE 12207:2026 6.4.9 Verification ve 6.4.11 Validation |

Test kataloğu: [traceability/tests.csv](traceability/tests.csv). Gerçek sonuçlar: [TEST_RESULTS.md](TEST_RESULTS.md) ve [RTM.md](RTM.md). Bu iki dosya `tools/build_rtm.py --week 5` ile üretilir; elle sonuç yazılmaz.

## 1. Kapsam

Hafta 1 (MOD-CFG, kullanıcı modeli), Hafta 2 (MOD-AUTH, MOD-ROLE, MOD-UI), Hafta 3 (MOD-TICKET: talep, kayıt bazlı erişim, kategori; katmanlı yapı) Hafta 4 (üzerine alma ve atama, yorumlar, öncelik değişikliği; MOD-AUDIT: işlem geçmişi) ve Faz 5 (durum makinesi, işlem geçmişi görünümü). Gereksinimler: FR-01..FR-21, NFR-01..NFR-12, NFR-16. Önceki haftaların testleri her pakette yeniden koşulur (gerileme). FR-22..FR-37 ve NFR-13..NFR-15 kapsam dışıdır (SRS §1.2, KRR-18).

## 2. Test seviyeleri ve araçları

| Seviye | Amaç | Araç | TC önekleri |
|---|---|---|---|
| Birim | Saf fonksiyonlar (rol çözümleme, ortam ayrıştırma, test koşucusu, RTM üretici) | Django test çatısı (`unittest`) | TC-ROLE-05, TC-CFG-05, TC-QA-03, TC-QA-04, TC-SEC-01, TC-AUD-02, TC-AUD-03 |
| Entegrasyon | Görünüm + middleware + veritabanı + şablon birlikte | Django test istemcisi | TC-AUTH-*, TC-ROLE-*, TC-SEED-*, TC-SEC-02/03, TC-CFG-01/04/06, TC-TKT-01..08, TC-CAT-01..03, TC-ASN-01..05, TC-CMT-01..04, TC-AUD-01, TC-WF-01..06 |
| Sistem (yapılandırma) | Ayarların ayrı süreçte yüklenmesi, üretim profili | `subprocess` + `manage.py check --deploy` | TC-CFG-02, TC-CFG-03 |
| Sistem (E2E, geçerleme) | Gerçek tarayıcıda rol ve talep senaryoları, mobil, klavye, kontrast | Playwright (Chromium) | TC-E2E-01..18 |
| Statik analiz | Kod kalitesi, kapsam ölçümü, mimari kurallar (Python AST) | ruff, coverage.py, `ast` | TC-QA-01, TC-QA-02, TC-ARCH-01, TC-ARCH-02 |
| İnceleme | Kişisel veri asgarisi | Kod/şablon incelemesi | TC-INS-01 |
| Kurulum / CI | Temiz ortam kurulumu, işletim sistemi matrisi | `tools/install_check.sh`, `tools/install_check.ps1`, GitHub Actions | TC-INST-01, TC-CI-01 |

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
| İşletim sistemi | Windows 11 Pro 10.0.26300 (Hafta 4 ve Faz 5 koşuları); Ubuntu ve Windows GitHub Actions işleri (TC-CI-01) |
| Python | 3.13.17 (Windows); CI'da 3.12 ve 3.13 |
| Django | 5.2.19 |
| Tarayıcı | Chromium 159.0.8154.6 (Playwright 1.65.2) |
| Veritabanı | SQLite (testlerde bellek içi; E2E'de geçici dosya) |
| E2E sunucusu | `runserver --insecure`, `DJANGO_DEBUG=0` (özel hata sayfaları üretimdeki gibi; KRR-15); Windows'ta `tools/run_e2e.ps1` |

Hafta 1-3 koşuları Linux'ta yapıldı (ortam bilgisi kendi kanıt klasörlerinde). Hafta 4 ve Faz 5'te Linux doğrulaması CI işleriyledir.

## 6. Çalıştırma

```bash
# Birim + entegrasyon (+ kapsam)
coverage run manage.py test -v 2 --results-json reports/unit-results.json
coverage report
coverage json -q -o reports/coverage.json
ruff check . --output-format json --output-file reports/ruff.json

# Tarayıcı (Linux/macOS); Windows: powershell -ExecutionPolicy Bypass -File tools\run_e2e.ps1
bash tools/run_e2e.sh

# Temiz kurulum ve mutasyon denetimi
bash tools/install_check.sh python3.13 linux-py313 reports/install-check-linux-py313.log
# Windows (PowerShell): powershell -ExecutionPolicy Bypass -File tools\install_check.ps1 3.13 windows-py313 reports\install-check-windows-py313.log
python tools/mutation_check.py --week 5 --out reports/mutation-check.md

# RTM ve test sonuç tablosu
python tools/build_rtm.py --week 5 --strict \
  --results reports/unit-results.json reports/e2e-results.json reports/e2e-week3-results.json reports/e2e-week4-results.json \
            reports/e2e-week5-results.json docs/evidence/hafta-05/manual-checks.json docs/evidence/hafta-05/ci-github-actions-*.json \
  --coverage reports/coverage.json --ruff reports/ruff.json
```

## 7. Faz 5 sonuç özeti

| Grup | Planlanan | Koşulan | PASS | FAIL | NOT RUN |
|---|---|---|---|---|---|
| Birim + entegrasyon + sistem + mimari (Django) | 69 | 69 | 69 | 0 | 0 |
| E2E (Chromium, Windows) | 18 | 18 | 18 | 0 | 0 |
| Statik analiz / ölçüm (TC-QA-01/02) | 2 | 2 | 2 | 0 | 0 |
| Kurulum (TC-INST-01, Windows 3.13) | 1 | 1 | 1 | 0 | 0 |
| İnceleme (TC-INS-01) | 1 | 1 | 1 | 0 | 0 |
| CI matrisi (TC-CI-01) | 1 | 1 | 1 | 0 | 0 |

Katalogda 92 test vardır; güncel durum her zaman [TEST_RESULTS.md](TEST_RESULTS.md) dosyasındadır. Mutasyon denetimi: 18 bilinçli hatanın 18'i yakalandı (`evidence/hafta-05/mutation-check.md`). Önceki haftaların özetleri kendi raporlarında ve kanıt klasörlerindedir.

Faz 5'te ilk koşularda bulunanlar: mutasyon M18 yakalanmadı (test açığı, RSK-33) ve TC-E2E-18 test tasarımı nedeniyle FAIL verdi (RSK-34). İkisi düzeltildi; yukarıdaki sonuçlar düzeltmeden sonraki koşudur.

## 8. Bilinen sınırlar

- E2E yalnız Chromium'da koşuldu; Firefox uyumu (NFR-15) kapsam dışı (KRR-18).
- Kontrast ölçümü seçili metin öğelerinde yapıldı; dört durum rozeti Faz 5'te tarayıcıda ölçüldü (TC-E2E-18). Yorum, işlem paneli ve geçmiş öğeleri ayrıca ölçülmedi (renkler mevcut belirteçlerden: metin `--sd-ink`, ikincil metin `--sd-muted`).
- TC-INS-01 incelemesinin Burak Nigiz tarafından tekrarlanıp onaylanması gerekir.
- Proje tek kişilik olduğundan bağımsız V&V yapılamıyor (RSK-03).
- Windows çıktı kodlaması düzeltmesi (`PYTHONUTF8=1`, RSK-25) CI'daki Windows işlerinde ve 26.11.2026'daki elle Windows koşusunda doğrulandı. Tarayıcı (E2E) testleri Windows'ta koşulmadı.
- Performans ölçümü (NFR-13) kapsam dışı (KRR-18).
- Hafta 4 ve Faz 5 koşuları Windows'ta yapıldı; Linux'ta bu fazların E2E'si koşulmadı (CI E2E koşmaz).
