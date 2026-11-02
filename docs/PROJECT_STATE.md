# PROJECT_STATE: SDS-07 Servis Masası (Hafta 1 paketi)

**Son güncelleme:** 30.10.2026 (Europe/Istanbul). **Hafta 1: TAMAMLANDI**. **Sıradaki: Hafta 2**: giriş/çıkış, roller, sunucu tarafı yetkilendirme, arayüz ve tarayıcı testleri.

> Hafta 1-3 paketleri geç kayıt nedeniyle 30.10.2026'da birlikte hazırlandı. Kanıt dosyalarındaki tarihler gerçek koşu tarihleridir; geriye tarih atılmadı. Bu paket, aynı gün geliştirilen kodun Hafta 1 kapsamına indirgenmiş anlık görüntüsüdür; buradaki bütün test ve ölçümler bu anlık görüntü üzerinde koşuldu.

## 0. Belgelerin okunma sırası

1. Bu dosyayı, sonra `docs/SRS.md` (§2.6 haftalık plan, §10 açık konular) ve `docs/RTM.md` dosyalarını okuyun.
2. Kodun güncel kopyası: https://github.com/wordeus/sds07-servis-masasi (Hafta 1: `hafta-1` etiketi).
3. Kurulum: `docs/INSTALL.md`. Testler ve RTM: `docs/TEST_PLAN.md §6`.
4. Yalnız aktif haftanın kapsamını uygulayın (proje talimatı). Gerçek kanıt kuralı geçerlidir: koşulmayan test NOT RUN, yapılmayan ölçüm ÖLÇÜLMEDİ.

## 1. Proje ve kapsam

ISO 9001 ilkelerini destekleyen IT Servis Masası ve Süreç Takip Sistemi. Roller Talep Sahibi, Destek Personeli ve Yönetici. Talep/incident akışı Open → In Progress → Resolved → Closed. Kapsamda değişiklik yönetimi, SLA (7/24, ilk yanıt ve çözüm ayrı), uyarı/eskalasyon, 1-5 memnuniyet puanı, KPI paneli, işlem geçmişi ve uygunsuzluk/DÖF kaydı var. Kapsam dışı: REST API, SPA, JWT, mikroservis, e-posta vb. Ayrıntı: SRS §1.2. Proje tek kişiliktir: Burak Nigiz (2100002062).

## 2. Ortam ve sürümler (30.10.2026)

| Öğe | Değer |
|---|---|
| Django | 5.2.18 (5.2 LTS'nin PyPI'deki son yaması, 06.10.2026; uzatılmış destek Nisan 2028) |
| Python | 3.13.18 ve 3.12.13 ile test edildi (Linux) |
| Diğer sabitler | asgiref 3.13.0, sqlparse 0.6.0, tzdata 2026.6 (yalnız Windows), coverage 7.17.0, ruff 0.17.3, lxml 6.1.3 (yalnız rapor üretimi) |
| Standart baskıları | ISO 9001:2026, ISO/IEC/IEEE 12207:2026, ISO/IEC/IEEE 29148:2018, IEEE 1016-2009 (Inactive-Reserved), ISO/IEC 25010:2023, IEEE 1012-2024. Ayrıntı: `docs/STANDARDS.md` |
| Test ortamı | Linux (bulut sunucu). Windows'ta elle henüz çalıştırılmadı; Windows doğrulaması GitHub Actions ile yapılacak. Depo: https://github.com/wordeus/sds07-servis-masasi |

## 3. Hafta 1'de tamamlananlar

| İş | Çıktı | Kanıt |
|---|---|---|
| Kapsam, aktörler, rol-yetki matrisi (plan), FR-01..FR-37, NFR-01..NFR-16, SLA/KPI kuralları, kabul kriterleri, haftalık plan | `docs/SRS.md` v0.1 | SRS §1-§7 |
| Standart baskıları, resmî bağlantılar, ISO 9001:2026 eşlemesi, 12207 uyarlaması, 25010 2011↔2023 eşlemesi | `docs/STANDARDS.md` v0.1 | §1-§9 |
| Django projesi, sabit bağımlılıklar, development/production profilleri, katı ortam değişkeni ayrıştırma, UTC/İstanbul | `config/`, `requirements*.txt` | TC-CFG-01, 02, 03, 05 |
| Özel kullanıcı modeli ve yönetim sitesi kaydı; parola kuralları | `servicedesk/models.py`, `admin.py`, `config/settings.py` | TC-CFG-06, TC-SEC-01 |
| TC kimlikli test koşucusu, RTM/test sonuç üretici (`--week`), rapor üretici, temiz kurulum denetimi | `config/test_runner.py`, `tools/` | TC-QA-03, TC-QA-04, TC-INST-01 |
| CI iş akışı (Ubuntu/Windows × 3.12/3.13), actionlint 0 bulgu | `.github/workflows/ci.yml` | TC-CI-01 PASS (02.11.2026, koşu #1, commit 29f962c; 4/4 iş) |
| Risk listesi, test planı, kalite ölçümleri, prosedürler, kurulum, kod rehberi, değişiklik günlüğü | `docs/*.md`, `CHANGELOG.md` | - |
| Rapor #1 (özgün şablon, beş başlık korunarak) | `docs/reports/Rapor-01_Hafta-1.docx` (+ `rapor-01.content.json`) | XSD doğrulaması |

## 4. Gerçek test ve ölçüm sonuçları (30.10.2026)

| Grup | Sonuç | Kaynak |
|---|---|---|
| Django birim/entegrasyon/sistem | 8/8 PASS (Python 3.13.18, Django 5.2.18) | `evidence/hafta-01/unit-results.json` |
| Kapsam (üretim kodu, `-v 2`) | %87,39 (eşik %80) | `evidence/hafta-01/coverage.json` |
| ruff | 0 bulgu | `evidence/hafta-01/ruff.json` |
| `check --deploy` (üretim) | 0 sorun, 1 gerekçeli susturma (W021); susturmasız koşuda W021 görülür | `evidence/hafta-01/check-deploy*.txt` |
| Temiz kurulum (TC-INST-01) | Linux 3.12.13 ve 3.13.18 BAŞARILI | `evidence/hafta-01/install-check-linux-py31*.log` |
| RTM (`--week 1`) | Hafta 1'in 7 gereksiniminin 7'si PASS; 46 gereksinim PLANLANDI. Test kataloğu: 13 PASS, 36 PLANLANDI | `docs/RTM.md`, `docs/TEST_RESULTS.md` |
| Bulunan ve düzeltilen hata | RTM özet tablosu "NOT RUN"ı "NOT" sayıyordu (RSK-06); TC-QA-04 eklendi, hatalı kodla FAIL verdiği doğrulandı | `evidence/hafta-01/rtm-ozet-hatasi-duzeltme-oncesi.txt`, `tc-qa-04-hatali-kodla.txt` |
| GitHub Actions (TC-CI-01) | Ubuntu ve Windows × Python 3.12 ve 3.13: 4/4 iş başarılı (02.11.2026, koşu #1, commit 29f962c) | `evidence/hafta-01/ci-github-actions-2026-11-02.json`, `ci-kosu-1-ozet.png` |
| NOT RUN / ÖLÇÜLMEDİ | Windows'ta elle kurulum, efor saatleri | - |

## 5. Kararlar (Hafta 1)

Hafta 1 kararları burada tutulur; Hafta 2'den itibaren karar günlüğü SDD §9'dadır. Kimlikler kalıcıdır.

| Kimlik | Karar | Gerekçe |
|---|---|---|
| KRR-01 | Tek Django projesi, tek uygulama, modüler iç yapı | Proje talimatı; tek kişilik ekip için basit dağıtım ve migration yönetimi |
| KRR-02 | Baştan özel `User` modeli (`AbstractUser`) | Django belgeleri yeni projelerde önerir; sonradan geçiş zordur |
| KRR-03 | development/production profilleri; üretimde güvensiz ayarla başlamama | Hatalı dağıtımı erken yakalama (NFR-04) |
| KRR-04 | Test sonuçlarını TC kimliğiyle JSON'a yazan koşucu ve RTM üretici | RTM'de gerçek sonuç; elle sonuç yazımını önleme |
| KRR-05 | Haftalık paketler: `week` sütunu, RTM'de `--week N`, kanıtlar `docs/evidence/hafta-NN/` | Her hafta ayrı teslim ve ayrı rapor; planlanan ile doğrulananın ayrı görünmesi |

## 6. Açık işler

- [x] Hafta 1'in GitHub Actions sonucu TC-CI-01 kanıtı olarak eklendi (PASS, 02.11.2026, koşu #1, commit 29f962c).
- [ ] Windows'ta kurulum ve testleri bir kez çalıştırıp sonucu kaydetmek (NFR-11).
- [ ] TC-INS-01 incelemesini tekrarlayıp onaylamak.
- [ ] Ayrıntılı SDS-07 proje dokümanı elde edilirse SRS ile karşılaştırmak (AK-07).

## 7. Hafta 2 planı

| ID | İş | Gereksinim |
|---|---|---|
| PLN-01 | Giriş/çıkış (yalnız POST çıkış), güvenli `next`, genel hata mesajı | FR-01..FR-05 |
| PLN-02 | Rol grupları, koddaki rol-izin matrisi, `post_migrate` eşitleme, sunucu tarafı yetki, rol menüsü, demo komutu | FR-06..FR-11 |
| PLN-03 | Türkçe arayüz (Django Templates + Bootstrap 5.3.8), 403/404/500/CSRF sayfaları, mobil, klavye ve kontrast | NFR-06..NFR-08 |
| PLN-04 | CSRF ve oturum çerezi kuralları | NFR-02, NFR-03 |
| PLN-05 | Tarayıcı (E2E) testleri ve mutasyon denetimi; SDD v0.1 | TC-E2E-01..09 |
| PLN-06 | RTM `--week 2`; Rapor #2 | - |

## 8. Bilinen teknik borç ve notlar

- `tools/build_report.py::build` döngüsel karmaşıklığı 19 (RSK-07); bölünecek.
- Kök adres şimdilik yönetim sitesine yönlenir; Hafta 2'de kullanıcı paneline yönlenecek.
- Rapor şablonundaki "ŞABLONU" ifadesi, üst bilgiyi koruma kuralı nedeniyle olduğu gibi bırakıldı.

## 9. Dosya haritası

```
config/settings.py           profiller, güvenlik, saat dilimi, parola kuralları
config/test_runner.py        TC sonuçlarını JSON'a yazan koşucu
config/urls.py               yönetim sitesi; kök adres yönetim sitesine yönlenir
servicedesk/models.py        özel kullanıcı modeli (User)
servicedesk/tests/           test_config, test_security, test_tooling
tools/build_rtm.py           RTM + TEST_RESULTS üretici (--week)
tools/build_report.py        Word rapor üretici (şablon + JSON içerik)
tools/install_check.sh       temiz kurulum denetimi (TC-INST-01)
docs/traceability/*.csv      gereksinim ve test kataloğu (RTM kaynağı)
docs/evidence/hafta-01/      gerçek koşu kayıtları
docs/reports/                Rapor #1 (docx) ve içerik dosyası
```
