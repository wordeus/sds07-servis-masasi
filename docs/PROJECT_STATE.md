# PROJECT_STATE: SDS-07 Servis Masası (Faz 5 paketi, proje bitişi)

**Son güncelleme:** 26.11.2026 (Europe/Istanbul). **Faz 5: TAMAMLANDI. Proje tamamlandı** (KRR-18: proje Faz 5'te biter; son teslim 11.12.2026).

> Faz 3, 4 ve 5 öğretim elemanına birlikte gönderilecek; her faz ayrı rapor (Rapor #3, #4, #5) ve ayrı etiketle (`hafta-3`, `hafta-4`, `hafta-5`) teslim edilir. Final belgesi ve sunum `docs/final/` klasöründedir.

## 0. Belgelerin okunma sırası

1. Bu dosya; sonra `docs/final/` (final belgesi ve sunum), `docs/SRS.md` (§1.2 teslim kapsamı, §7.1 kabul kriterleri), `docs/SDD.md` ve `docs/RTM.md`.
2. Kod: https://github.com/wordeus/sds07-servis-masasi (`hafta-5` etiketi ve Release).
3. Kurulum: `docs/INSTALL.md`. Testler ve RTM: `docs/TEST_PLAN.md §6`. Kod anlatımı: `docs/KOD_REHBERI.md`.

## 1. Proje ve kapsam

ISO 9001 ilkelerini destekleyen IT Servis Masası ve Süreç Takip Sistemi. Roller Talep Sahibi, Destek Personeli ve Yönetici. Teslim edilen kapsam: kimlik doğrulama ve roller, talep oluşturma ve listeleme, kayıt bazlı erişim, kategoriler, atama ve üzerine alma, yorumlar, öncelik değişikliği, durum makinesi (Açık → İşlemde → Çözüldü → Kapandı) ve değiştirilemez işlem geçmişi. Gelecek çalışma: değişiklik yönetimi, SLA ve eskalasyon, bildirimler, memnuniyet anketi, KPI paneli, uygunsuzluk ve DÖF, performans ve Firefox uyumu (KRR-18, SRS §1.2). Proje tek kişiliktir: Burak Nigiz (2100002062).

## 2. Ortam ve sürümler (26.11.2026)

| Öğe | Değer |
|---|---|
| Django | 5.2.19 (5.2 LTS; uzatılmış destek Nisan 2028) |
| Python | 3.13.17 (Windows 11); CI'da 3.12 ve 3.13 (Ubuntu ve Windows) |
| Bootstrap | 5.3.8 (yerel dosya); yazı tipi IBM Plex Sans 5.3.0 (OFL, yerel) |
| Diğer sabitler | asgiref 3.13.0, sqlparse 0.6.1 (son sürüm, RSK-31), tzdata 2026.6 (yalnız Windows), coverage 7.17.4, ruff 0.17.6, playwright 1.65.2, lxml 6.1.3 |
| Standart baskıları | ISO 9001:2026, ISO/IEC/IEEE 12207:2026, ISO/IEC/IEEE 29148:2018, IEEE 1016-2009, ISO/IEC 25010:2023, IEEE 1012-2024 (`docs/STANDARDS.md`) |
| Otomasyon | CI (her push ve PR), Release (`hafta-N` etiketi; Word, PDF, kanıt zip), Dependabot (Pazartesi 08:00), `tools/record_ci_run.sh` |

## 3. Faz 5'te tamamlananlar

| İş | Çıktı | Kanıt |
|---|---|---|
| Durum makinesi ve geçiş koşulları; çözüm açıklaması zorunlu | `services/workflow.py`, `TicketStatusView`, migration 0007 | TC-WF-01..05, TC-E2E-17, TC-E2E-18 |
| İşlem geçmişi görünümü; durum geçişlerinin geçmişe yazılması | `services/audit.py::history_for`, `ticket_detail.html` | TC-WF-01, TC-WF-06 |
| Rol-izin matrisi Hafta 5 izinleri; `CURRENT_WEEK = 5` | `roles.py` | TC-ROLE-15 |
| AK-01 kararı: yeniden açma yok (KRR-19) | SRS §10, SDD §9 | TC-WF-05 |
| E2E iskeletinin ortaklaştırılması; Hafta 2 senaryolarının bölünmesi (PLN-06) | `e2e/week2_auth_roles.py::run_suite`, `e2e/week5_status.py` | Karmaşıklık 18 → 3 |
| Mutasyon denetiminin genişletilmesi (13 → 18) | `tools/mutation_check.py` | `evidence/hafta-05/mutation-check.md` |
| SRS v0.5, SDD v0.4, RISKS v0.5, TEST_PLAN v0.5, INSTALL v0.5, STANDARDS v0.5, kalite ölçümleri, kod rehberi | `docs/*.md`, `CHANGELOG.md` 1.0.0 | - |
| Rapor #5, final belgesi, HTML sunum ve demo videosu | `docs/reports/Rapor-05_Hafta-5.*`, `docs/final/`, `tools/record_demo.py` | [Video](https://github.com/wordeus/sds07-servis-masasi/releases/download/hafta-5/SDS-07_Sunum_ve_Demo.webm) |

## 4. Gerçek test ve ölçüm sonuçları (26.11.2026)

| Grup | Sonuç | Kaynak |
|---|---|---|
| Django birim/entegrasyon/sistem/mimari | 69/69 PASS (Python 3.13.17, Django 5.2.19, Windows 11) | `evidence/hafta-05/unit-results.json` |
| Tarayıcı E2E (Chromium 159.0.8154.6) | 18/18 PASS (16 gerileme + 2 Faz 5) | `evidence/hafta-05/e2e-*.json` |
| Kapsam (üretim kodu, `-v 2`) | %95,03 (eşik %80) | `evidence/hafta-05/coverage.json` |
| ruff | 0 bulgu | `evidence/hafta-05/ruff.json` |
| `check --deploy` (üretim) | 0 sorun, 1 gerekçeli susturma (W021) | `evidence/hafta-05/check-deploy.txt` |
| Temiz kurulum (TC-INST-01) | Windows 3.13.17 BAŞARILI | `evidence/hafta-05/install-check-windows-py313.log` |
| Mutasyon denetimi | 18/18 yakalandı (69 test) | `evidence/hafta-05/mutation-check.md` |
| Durum rozeti kontrastı (tarayıcıda) | Açık 6,41, İşlemde 5,99, Çözüldü 5,42, Kapandı 5,87 (:1) | TC-E2E-18 |
| GitHub Actions (TC-CI-01) | Koşu #23, commit 8b752e4: Ubuntu/Windows × Python 3.12/3.13, 4/4 iş başarılı | `evidence/hafta-05/ci-github-actions-2026-11-26.json` |
| RTM (`--week 5`) | Kapsam içi 34 gereksinimin 34'ü PASS; 19 KAPSAM DIŞI (gelecek çalışma). Test kataloğu: 92/92 PASS | `docs/RTM.md`, `docs/TEST_RESULTS.md` |
| Faz 5'te bulunan sorunlar | RSK-33 (mutasyonla bulunan test açığı), RSK-34 (E2E test tasarımı); ikisi de kapandı | `docs/RISKS.md` |
| NOT RUN / ÖLÇÜLMEDİ | Hafta 4-5 E2E Linux'ta koşulmadı (CI E2E koşmaz); yorum/işlem/geçmiş öğelerinin kontrastı ayrıca ölçülmedi; efor saatleri; performans (kapsam dışı) | - |

## 5. Açık işler

- [x] TC-INS-01 incelemeleri (Hafta 3, 4 ve Faz 5) Burak Nigiz tarafından 26.11.2026'da onaylandı (`evidence/hafta-05/manual-checks.json`, `tc-ins-01-onay.json`).
- [ ] Faz 3, 4 ve 5'in öğretim elemanına gönderilmesi (Rapor #3-#5 Word ve PDF, final belgesi, sunum, depo bağlantısı).

## 6. Önemli kararlar

KRR-01..KRR-18 ve Faz 5'te eklenen KRR-19 (yeniden açma yok). Ayrıntı: SDD §9.

## 7. Gelecek çalışma

SRS §1.2 ve RTM'de "KAPSAM DIŞI (gelecek çalışma)" olarak işaretli 19 gereksinim: değişiklik yönetimi (FR-22..FR-25), SLA ve eskalasyon (FR-26..FR-30), bildirim kutusu (FR-31), memnuniyet anketi ve KPI paneli (FR-32..FR-34), uygunsuzluk ve DÖF (FR-35..FR-37), performans, yetkisiz erişim günlüğü ve Firefox uyumu (NFR-13..NFR-15). SDD'de bu modüllerin bilgi ve durum tasarımı korunur.

## 8. Bilinen teknik borç ve notlar

- İşlem geçmişinin değiştirilemezliği uygulama düzeyindedir (KRR-16); doğrudan SQL erişimine karşı koruma yoktur.
- `workflow.change_status` döngüsel karmaşıklığı 10 (eşikte); yeni kural eklenirse bölünmeli.
- Kategori adı tekilliği uygulama düzeyinde (Türkçe kurallı) denetlenir (kabul edildi).
- sqlparse bakımı bitti (RSK-31); Django bağımlılığı değiştirirse izlenmeli.
- Windows'ta yönlendirilmiş çıktı için `PYTHONUTF8=1` gerekir (RSK-25); betikler bunu kendisi ayarlar.

## 9. Dosya haritası

```
config/settings.py              profiller, güvenlik, saat dilimi
config/test_runner.py           TC sonuçlarını JSON'a yazan koşucu
servicedesk/models/             user.py (User), ticket.py (Category, Ticket), activity.py (Comment, TicketEvent)
servicedesk/services/           tickets.py (görünürlük, talep, filtre, kategori), assignment.py (üzerine alma, atama,
                                öncelik), comments.py (yorum), workflow.py (durum makinesi), audit.py (geçmiş yazımı ve görünümü)
servicedesk/views/              dashboard.py, tickets.py, ticket_actions.py (yorum, üzerine al, ata, öncelik, durum), categories.py
servicedesk/forms.py            LoginForm, TicketForm, TicketFilterForm, CategoryForm, CommentForm, AssignForm, PriorityForm, StatusForm
servicedesk/roles.py            roller, ROLE_PERMISSIONS, CAPABILITIES, CURRENT_WEEK, sync_role_groups
servicedesk/tests/              test_auth, test_roles, test_security, test_config, test_seed, test_tooling, test_tickets,
                                test_categories, test_architecture, test_assignment, test_comments, test_audit, test_workflow
e2e/                            week2_auth_roles.py (run_suite iskeleti, TC-E2E-01..09), week3_tickets.py (10..13),
                                week4_workflow.py (14..16), week5_status.py (17..18)
tools/                          build_rtm.py, build_report.py, run_e2e.sh/.ps1, install_check.sh/.ps1, mutation_check.py, record_ci_run.sh
docs/traceability/*.csv         gereksinim ve test kataloğu (RTM kaynağı)
docs/evidence/hafta-01..05/     haftalık gerçek koşu kayıtları
docs/reports/                   Rapor #1-#5 (docx; #4-#5 için pdf) ve içerik dosyaları
docs/final/                     final belgesi ve sunum
.github/                        CI ve Release iş akışları, Dependabot
```
