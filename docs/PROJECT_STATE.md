# PROJECT_STATE: SDS-07 Servis Masası (Hafta 3 paketi)

**Son güncelleme:** 30.10.2026 (Europe/Istanbul). **Hafta 3: TAMAMLANDI**. **Sıradaki: Hafta 4**: atama ve üzerine alma, yorumlar, işlem geçmişinin ilk sürümü.

> Hafta 1-3 paketleri geç kayıt nedeniyle 30.10.2026'da birlikte hazırlandı. Kanıt dosyalarındaki tarihler gerçek koşu tarihleridir; geriye tarih atılmadı. Hafta 3 kodu 30.10.2026 sabahı (İstanbul saatiyle yaklaşık 09:15-09:40) Hafta 2 paketinin üzerine yazıldı; bu paketteki bütün test ve ölçümler bu kod üzerinde koşuldu.

## 0. Belgelerin okunma sırası

1. Bu dosyayı, sonra `docs/SRS.md` (§2.6 haftalık plan, §7.2 sonraki haftalar, §10 açık konular), `docs/SDD.md` ve `docs/RTM.md` dosyalarını okuyun.
2. Kodun güncel kopyası: https://github.com/wordeus/sds07-servis-masasi (Hafta 3: `hafta-3` etiketi).
3. Kurulum: `docs/INSTALL.md`. Testler ve RTM: `docs/TEST_PLAN.md §6`. Yeni ekran eklerken: `docs/PROCEDURES.md` PRC-09.
4. Yalnız aktif haftanın kapsamını uygulayın (proje talimatı). Gerçek kanıt kuralı geçerlidir: koşulmayan test NOT RUN, yapılmayan ölçüm ÖLÇÜLMEDİ.

## 1. Proje ve kapsam

ISO 9001 ilkelerini destekleyen IT Servis Masası ve Süreç Takip Sistemi. Roller Talep Sahibi, Destek Personeli ve Yönetici. Talep/incident akışı Open → In Progress → Resolved → Closed. Kapsamda değişiklik yönetimi, SLA (7/24, ilk yanıt ve çözüm ayrı), uyarı/eskalasyon, 1-5 memnuniyet puanı, KPI paneli, işlem geçmişi ve uygunsuzluk/DÖF kaydı var. Kapsam dışı: REST API, SPA, JWT, mikroservis, e-posta vb. Ayrıntı: SRS §1.2. Proje tek kişiliktir: Burak Nigiz (2100002062).

## 2. Ortam ve sürümler (30.10.2026)

| Öğe | Değer |
|---|---|
| Django | 5.2.18 (5.2 LTS'nin PyPI'deki son yaması, 06.10.2026; uzatılmış destek Nisan 2028) |
| Python | 3.13.18 ve 3.12.13 ile test edildi (Linux) |
| Bootstrap | 5.3.8 (yerel dosya); yazı tipi IBM Plex Sans 5.3.0 (OFL, yerel) |
| Diğer sabitler | asgiref 3.13.0, sqlparse 0.6.0, tzdata 2026.6 (yalnız Windows), coverage 7.17.0, ruff 0.17.3, playwright 1.63.0, lxml 6.1.3. Hafta 3'te yeni bağımlılık eklenmedi. |
| Standart baskıları | ISO 9001:2026, ISO/IEC/IEEE 12207:2026, ISO/IEC/IEEE 29148:2018, IEEE 1016-2009 (Inactive-Reserved), ISO/IEC 25010:2023, IEEE 1012-2024. Ayrıntı: `docs/STANDARDS.md` |
| Test ortamı | Linux (bulut sunucu), tarayıcı testleri için Playwright/Chromium. Windows 11'de (Python 3.13.17) Django testleri ve temiz kurulum 26.11.2026'da elle çalıştırıldı; ayrıca GitHub Actions'ta windows-latest. Depo: https://github.com/wordeus/sds07-servis-masasi |

## 3. Hafta 3'te tamamlananlar

| İş | Çıktı | Kanıt |
|---|---|---|
| Category ve Ticket modelleri, başlangıç kategorileri, talep numarası (`INC-000123`) | `servicedesk/models/ticket.py`, migration 0003 ve 0004 | TC-TKT-01, TC-CAT-01 |
| Talep oluşturma, liste (filtre, 25'li sayfa), ayrıntı ve süreç şeridi | `services/tickets.py`, `views/tickets.py`, `forms.py`, şablonlar | TC-TKT-01..08, TC-E2E-10, TC-E2E-12 |
| Kayıt bazlı erişim politikası (başkasının talebine 404) | `services/tickets.py::visible_tickets_for` | TC-TKT-04, 05, 07, TC-E2E-11, mutasyon M5/M6 |
| Kategori ekleme ve pasifleştirme (Yönetici); Türkçe kurallı tekil ad | `views/categories.py`, `models/ticket.py::Category.clean`, `text.py` | TC-CAT-01..03, TC-E2E-13 |
| `models/`, `services/`, `views/` katmanları ve mimari testleri | `servicedesk/tests/test_architecture.py` | TC-ARCH-01, TC-ARCH-02 |
| Rol-izin matrisi Hafta 3 izinleri; menüde Talepler/Kategoriler; panelde durum özeti; destek kuyruğunda açık talepler | `roles.py`, şablonlar | TC-ROLE-13, TC-E2E-12 |
| E2E iyileştirmeleri (DEBUG kapalı sunucu, gezinme bekleme) ve Hafta 3 senaryoları | `tools/run_e2e.sh`, `e2e/week3_tickets.py` | `evidence/hafta-03/e2e-*.json` |
| Rapor aracının bölünmesi (19 → 4) | `tools/build_report.py` | `evidence/hafta-03/build-report-esdegerlik.txt` |
| SRS v0.3, SDD v0.2, STANDARDS v0.3, RISKS v0.3, TEST_PLAN v0.3, PROCEDURES v0.3, kalite ölçümleri, kod rehberi | `docs/*.md`, `CHANGELOG.md` | - |
| Rapor #3 (özgün şablon, beş başlık korunarak) | `docs/reports/Rapor-03_Hafta-3.docx` (+ `rapor-03.content.json`) | XSD doğrulaması |
| Teslim öncesi kontrol: depo dışlama denetimi ve Windows çıktı kodlaması simülasyonu; iki hata bulundu ve düzeltildi (üç pakette `.gitignore` ve `ci.yml`) | `.gitignore`, `.github/workflows/ci.yml`, INSTALL §2 ve §7 | `evidence/hafta-03/teslim-oncesi/` (RSK-24, RSK-25) |

## 4. Gerçek test ve ölçüm sonuçları (30.10.2026)

| Grup | Sonuç | Kaynak |
|---|---|---|
| Django birim/entegrasyon/sistem/mimari | 49/49 PASS (Python 3.13.18, Django 5.2.18) | `evidence/hafta-03/unit-results.json` |
| Tarayıcı E2E (Chromium 153.0.8010.12) | 13/13 PASS (9 Hafta 2 gerilemesi + 4 Hafta 3) | `evidence/hafta-03/e2e-results.json`, `e2e-week3-results.json` |
| Kapsam (üretim kodu, `-v 2`) | %94,21 (eşik %80) | `evidence/hafta-03/coverage.json` |
| ruff | 0 bulgu | `evidence/hafta-03/ruff.json` |
| `check --deploy` (üretim) | 0 sorun, 1 gerekçeli susturma (W021) | `evidence/hafta-03/check-deploy.txt` |
| Temiz kurulum (TC-INST-01) | Linux 3.12.13 ve 3.13.18 BAŞARILI | `evidence/hafta-03/install-check-linux-py31*.log` |
| Mutasyon denetimi | 8/8 yakalandı (49 test) | `evidence/hafta-03/mutation-check.md` |
| RTM (`--week 3`) | Hafta 1-3'ün 28 gereksiniminin 28'i PASS; 25 gereksinim PLANLANDI. Test kataloğu: 67 PASS | `docs/RTM.md`, `docs/TEST_RESULTS.md` |
| GitHub Actions (TC-CI-01) | Koşu #5, commit aa17057: Ubuntu/Windows × Python 3.12/3.13, 4/4 iş başarılı (21.11.2026) | `evidence/hafta-03/ci-github-actions-2026-11-21.json` |
| Windows (26.11.2026) | Windows 11, Python 3.13.17: 49/49 PASS, kapsam %94,21, ruff 0, `check --deploy` 0; temiz kurulum BAŞARILI | `evidence/hafta-03/windows-2026-11-26/` |
| Bu hafta bulunan sorunlar | RSK-21 (Türkçe büyük harf), RSK-22 (E2E giriş beklemesi), RSK-23 (E2E'de DEBUG 404 sayfası); üçü de kapandı | `docs/RISKS.md`, `evidence/hafta-03/` |
| Teslim öncesi kontrolde bulunanlar | RSK-24: `.gitignore` raporları ve kanıt günlüklerini depo dışında bırakıyordu (kapandı). RSK-25: Windows'ta yönlendirilmiş çıktıda Türkçe karakter `UnicodeEncodeError` veriyordu; CI'a UTF-8 kipi eklendi; Hafta 1-2 CI koşularında Windows işleri geçti (kapandı) | `evidence/hafta-03/teslim-oncesi/` |
| Teslim öncesi güncellemede bulunanlar (26.11.2026) | RSK-26: RTM üreticisi Windows'ta yolları ters bölüyle yazıyordu (düzeltildi, TC-QA-04'e denetim eklendi). RSK-27: Windows kurulum betiği BOM'suz kaydedilince günlükte Türkçe karakterler bozuluyordu (düzeltildi) | `docs/RISKS.md`, `evidence/hafta-03/windows-2026-11-26/` |
| NOT RUN / ÖLÇÜLMEDİ | Windows'ta tarayıcı (E2E) testleri, Firefox E2E, performans (NFR-13), efor saatleri | - |

## 5. Açık işler

- [x] Hafta 3'ün GitHub Actions sonucu TC-CI-01 kanıtı olarak eklendi: koşu #5, commit aa17057, 4/4 iş başarılı (`evidence/hafta-03/ci-github-actions-2026-11-21.json`). Hafta 1: koşu #1, commit 29f962c; Hafta 2: koşu #3, commit 6dd3dc9.
- [x] `RTM.md` ve `TEST_RESULTS.md` CI ve Windows kanıtlarıyla yeniden üretildi (26.11.2026): 28/28 gereksinim, 67/67 test PASS.

## 5.1 Otomasyon (26.11.2026)

- `.github/dependabot.yml`: pip ve Actions bağımlılıkları için haftalık PR (Pazartesi 08:00); Django için yalnız 5.2.x yamaları.
- `.github/workflows/release.yml`: `hafta-N` etiketi gönderilince Release oluşturur; `Rapor-0N_Hafta-N.docx` ve `kanit-hafta-0N.zip` eklenir, notlar CHANGELOG'dan alınır.
- `tools/record_ci_run.sh <hafta> [commit]`: CI koşusunun sonucunu GitHub API'den okuyup `evidence/hafta-0N/ci-github-actions-*.json` yazar. Koşu bitmemişse ya da dosya zaten varsa yazmaz.
- Haftalık akış: `hafta-N` dalında çalışılır, PR açılır, CI geçince main'e birleştirilir, `record_ci_run.sh` çalıştırılır, ardından `hafta-N` etiketi gönderilir.
- [x] Windows'ta kurulum ve testler elle çalıştırıldı (26.11.2026, Windows 11, Python 3.13.17): BAŞARILI (NFR-11, TC-INST-01). Betik: `tools/install_check.ps1`.
- [ ] TC-INS-01 incelemesini tekrarlayıp onaylamak.
- [ ] Açık konuları netleştirmek: yeniden açma akışı (AK-01), önceliği kimin seçeceği (AK-03; geçici karar KRR-13). Standart baskıları için karar: en güncel baskılar (AK-05).

## 6. Önemli kararlar

KRR-01..KRR-10 (Hafta 1-2) ve Hafta 3'te eklenenler: KRR-11 katmanlı yapı ve mimari testleri; KRR-12 talep numarası birincil anahtardan; KRR-13 önceliği talep sahibi seçer (geçici); KRR-14 kategori silinmez, pasifleştirilir; KRR-15 E2E sunucusu DEBUG kapalı. Ayrıntı: SDD §9.

## 7. Hafta 4 planı

| ID | İş | Gereksinim |
|---|---|---|
| PLN-01 | Talebi üzerine alma (Destek Personeli) ve atama (Yönetici yalnız Destek Personeli rolüne) | FR-16 |
| PLN-02 | Yorumlar: talep sahibi kendi talebine, personel ve yönetici tüm taleplere; Closed talebe yorum yok; yorum adresinde başkasının talebi için 404 | FR-17, FR-14, RSK-08 |
| PLN-03 | İşlem geçmişinin ilk sürümü: oluşturma, atama, öncelik değişikliği; yalnız ekleme | FR-20 |
| PLN-04 | Öncelik değişikliğini destek personeline açma (AK-03 / KRR-13) | FR-12, FR-20 |
| PLN-05 | Windows'ta tarayıcı (E2E) testlerini bir kez koşmak (temiz kurulum ve Django testleri 26.11.2026'da Windows'ta yapıldı) | NFR-11 |
| PLN-06 | `e2e/week2_auth_roles.py::main` bölünmesi (RSK-07) | - |
| PLN-07 | RTM `--week 4`; Rapor #4 | - |

Hafta 4 başında yapılacaklar: Django 5.2.19 yayımlandıysa sürüm notlarını okuyup sabitlemeyi güncelleyin. `CURRENT_WEEK` değerini 4 yapın; yorum ve atama izinlerini `ROLE_PERMISSIONS`'a ekleyin (PRC-07, PRC-09).

## 8. Bilinen teknik borç ve notlar

- `e2e/week2_auth_roles.py::main` döngüsel karmaşıklığı 18 (RSK-07, kısmen kapandı).
- Kategori adı tekilliği uygulama düzeyinde (Türkçe kurallı) denetlenir; veritabanındaki `unique` kısıtı yalnız birebir aynı adı engeller. Aynı anda iki yöneticinin aynı adı farklı yazımla eklemesi teorik olarak mümkündür; kategori sayısı az ve işlem yalnız Yönetici rolünde olduğu için kabul edildi.
- Talep ayrıntısındaki `form_valid` içindeki doğrulama hatası dalı (pasif kategori servis kontrolü) normal akışta formdan önce yakalandığı için kapsam dışında kaldı (`views/tickets.py` 67-69); savunma katmanıdır.
- E2E çalıştırmadan önce açık sunucu olmadığını doğrulayın (RSK-20); `tools/run_e2e.sh` bunu denetler.
- RSK-25'in kalıcı çözümü (komut çıktısının kod sayfasından bağımsız olması: `roles.py` eşitleme çıktısı, `tools/build_rtm.py` çıktısı) Hafta 4'te değerlendirilecek. O zamana kadar Windows'ta yönlendirilmiş çıktı için `PYTHONUTF8=1` gerekir.
- Rapor şablonundaki "ŞABLONU" ifadesi, üst bilgiyi koruma kuralı nedeniyle olduğu gibi bırakıldı.

## 9. Dosya haritası

```
config/settings.py              profiller, güvenlik, saat dilimi
config/test_runner.py           TC sonuçlarını JSON'a yazan koşucu
servicedesk/models/             user.py (User), ticket.py (Category, Ticket)
servicedesk/services/tickets.py görünürlük politikası, talep, filtre, kategori, süreç şeridi
servicedesk/views/              dashboard.py, tickets.py, categories.py
servicedesk/forms.py            LoginForm, TicketForm, TicketFilterForm, CategoryForm
servicedesk/roles.py            roller, ROLE_PERMISSIONS, CAPABILITIES, CURRENT_WEEK, sync_role_groups
servicedesk/text.py             Türkçe kurallı karşılaştırma anahtarı
servicedesk/tests/              test_auth, test_roles, test_security, test_config, test_seed, test_tooling,
                                test_tickets, test_categories, test_architecture
templates/, servicedesk/templates/  ortak şablonlar; tickets/, categories/
e2e/week2_auth_roles.py         Playwright senaryoları TC-E2E-01..09 (ortak yardımcılar)
e2e/week3_tickets.py            Playwright senaryoları TC-E2E-10..13
tools/                          build_rtm.py, build_report.py, run_e2e.sh, install_check.sh, install_check.ps1 (Windows),
                                mutation_check.py, record_ci_run.sh (CI kanıtı)
docs/traceability/*.csv         gereksinim ve test kataloğu (RTM kaynağı)
docs/evidence/hafta-01..03/     haftalık gerçek koşu kayıtları
docs/reports/                   Rapor #1, #2, #3 (docx) ve içerik dosyaları
```
