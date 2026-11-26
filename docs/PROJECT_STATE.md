# PROJECT_STATE: SDS-07 Servis Masası (Hafta 4 paketi)

**Son güncelleme:** 26.11.2026 (Europe/Istanbul). **Hafta 4: TAMAMLANDI**. **Sıradaki: Faz 5 (Hafta 5, bitiş fazı, son teslim 11.12.2026)**: durum geçişleri, işlem geçmişi görünümü, final belgesi, sunum ve demo.

> **Kapsam kararı (26.11.2026, KRR-18):** Proje Faz 5'te biter. FR-22..FR-37 (değişiklik yönetimi, SLA, uyarı/eskalasyon, anket, KPI, DÖF) ve NFR-13..NFR-15 gelecek çalışmadır; RTM'de "KAPSAM DIŞI" görünür. Faz 3, 4 ve 5 öğretim elemanına birlikte gönderilecek; her faz ayrı rapor ve ayrı etiketle (`hafta-N`) teslim edilir.

## 0. Belgelerin okunma sırası

1. Bu dosyayı, sonra `docs/SRS.md` (§1.2 teslim kapsamı, §2.6 plan, §7.1 kabul kriterleri, §10 açık konular), `docs/SDD.md` ve `docs/RTM.md` dosyalarını okuyun.
2. Kodun güncel kopyası: https://github.com/wordeus/sds07-servis-masasi (Hafta 4: `hafta-4` etiketi). İş takibi: GitHub'da "Faz 4" ve "Faz 5" kilometre taşları.
3. Kurulum: `docs/INSTALL.md`. Testler ve RTM: `docs/TEST_PLAN.md §6`. Yeni ekran eklerken: `docs/PROCEDURES.md` PRC-09. Dal ve PR adları: PRC-01 (`hafta-N/<konu>`, "Hafta N: ...").
4. Yalnız aktif fazın kapsamını uygulayın. Gerçek kanıt kuralı geçerlidir: koşulmayan test NOT RUN, yapılmayan ölçüm ÖLÇÜLMEDİ.

## 1. Proje ve kapsam

ISO 9001 ilkelerini destekleyen IT Servis Masası ve Süreç Takip Sistemi. Roller Talep Sahibi, Destek Personeli ve Yönetici. Talep/incident akışı Open → In Progress → Resolved → Closed. Bu teslimin kapsamı: kimlik doğrulama ve roller, talep oluşturma ve listeleme, kayıt bazlı erişim, kategoriler, atama ve üzerine alma, yorumlar, öncelik değişikliği, işlem geçmişi (Faz 4); durum geçişleri ve geçmiş görünümü (Faz 5). Gelecek çalışma: KRR-18. Ayrıntı: SRS §1.2. Proje tek kişiliktir: Burak Nigiz (2100002062).

## 2. Ortam ve sürümler (26.11.2026)

| Öğe | Değer |
|---|---|
| Django | 5.2.19 (5.2 LTS güvenlik yaması, PyPI 03.11.2026; uzatılmış destek Nisan 2028) |
| Python | 3.13.17 (Windows 11, Hafta 4 koşuları); CI'da 3.12 ve 3.13 (Ubuntu ve Windows). Hafta 1-3: 3.12.13 ve 3.13.18 (Linux) |
| Bootstrap | 5.3.8 (yerel dosya); yazı tipi IBM Plex Sans 5.3.0 (OFL, yerel) |
| Diğer sabitler | asgiref 3.13.0, sqlparse 0.6.1 (son sürüm, bakımı bitti, RSK-31), tzdata 2026.6 (yalnız Windows), coverage 7.17.4, ruff 0.17.6, playwright 1.65.2 (Chromium 159), lxml 6.1.3. Hafta 4'te yeni bağımlılık eklenmedi. |
| Standart baskıları | ISO 9001:2026, ISO/IEC/IEEE 12207:2026, ISO/IEC/IEEE 29148:2018, IEEE 1016-2009 (Inactive-Reserved), ISO/IEC 25010:2023, IEEE 1012-2024. Ayrıntı: `docs/STANDARDS.md` |
| Test ortamı | Windows 11 Pro (Django testleri, E2E, temiz kurulum, mutasyon); GitHub Actions (Ubuntu/Windows × Python 3.12/3.13). Depo: https://github.com/wordeus/sds07-servis-masasi |
| Otomasyon | CI (her push ve PR), Release (`hafta-N` etiketi), Dependabot (Pazartesi 08:00), `tools/record_ci_run.sh` (CI kanıtı) |

## 3. Hafta 4'te tamamlananlar

| İş | Çıktı | Kanıt |
|---|---|---|
| Bağımlılık güncellemesi: Django 5.2.19, sqlparse 0.6.1, coverage, ruff, Playwright 1.65.2 | `requirements*.txt` (PR #21) | `evidence/hafta-04/bagimlilik-guncelleme-2026-11-26/` |
| Talebi üzerine alma ve atama (yalnız Destek Personeline) | `services/assignment.py`, `views/ticket_actions.py`, şablon | TC-ASN-01..03, TC-ASN-05, TC-E2E-14, TC-E2E-15 |
| Yorumlar; kapanmış talebe yorum yok; yorum adresinde başkasının talebi için 404 | `models/activity.py::Comment`, `services/comments.py` | TC-CMT-01..04, TC-E2E-14..16 |
| Öncelik değişikliği (AK-03 kapandı, KRR-17) | `services/assignment.py::change_priority` | TC-ASN-04 |
| İşlem geçmişi: oluşturma, atama, öncelik; değiştirilemez; eski taleplere oluşturma kaydı | `models/activity.py::TicketEvent`, `services/audit.py`, migration 0005-0006 | TC-AUD-01..03, mutasyon M12, M13 |
| Rol-izin matrisi Hafta 4 izinleri; `CURRENT_WEEK = 4`; kapsam dışı yetenekler panelde "Kapsam dışı" | `roles.py`, `dashboard.html` | TC-ROLE-14 |
| Kapsam kararı (Faz 5 bitiş) ve RTM'de KAPSAM DIŞI durumu | SRS v0.4 §1.2/§2.6, `requirements.csv`, `tools/build_rtm.py` | TC-QA-04, `docs/RTM.md` |
| Windows E2E betiği ve Hafta 4 E2E senaryoları | `tools/run_e2e.ps1`, `e2e/week4_workflow.py` | `evidence/hafta-04/e2e-*.json` |
| Mutasyon denetiminin genişletilmesi (8 → 13) | `tools/mutation_check.py` | `evidence/hafta-04/mutation-check.md` |
| SRS v0.4, SDD v0.3, RISKS v0.4, TEST_PLAN v0.4, INSTALL v0.4, STANDARDS v0.4, kalite ölçümleri, kod rehberi | `docs/*.md`, `CHANGELOG.md` | - |
| Rapor #4 (özgün şablon) | `docs/reports/Rapor-04_Hafta-4.docx` (+ `.pdf`, `rapor-04.content.json`) | - |

## 4. Gerçek test ve ölçüm sonuçları (26.11.2026)

| Grup | Sonuç | Kaynak |
|---|---|---|
| Django birim/entegrasyon/sistem/mimari | 62/62 PASS (Python 3.13.17, Django 5.2.19, Windows 11) | `evidence/hafta-04/unit-results.json` |
| Tarayıcı E2E (Chromium 159.0.8154.6) | 16/16 PASS (13 gerileme + 3 Hafta 4) | `evidence/hafta-04/e2e-*.json` |
| Kapsam (üretim kodu, `-v 2`) | %95,04 (eşik %80) | `evidence/hafta-04/coverage.json` |
| ruff | 0 bulgu | `evidence/hafta-04/ruff.json` |
| `check --deploy` (üretim) | 0 sorun, 1 gerekçeli susturma (W021) | `evidence/hafta-04/check-deploy.txt` |
| Temiz kurulum (TC-INST-01) | Windows 3.13.17 BAŞARILI | `evidence/hafta-04/install-check-windows-py313.log` |
| Mutasyon denetimi | 13/13 yakalandı (62 test) | `evidence/hafta-04/mutation-check.md` |
| GitHub Actions (TC-CI-01) | Hafta 4 commit'inin koşusu birleştirmeden sonra kaydedilir | `evidence/hafta-04/ci-github-actions-*.json` |
| RTM (`--week 4`) | Ayrıntı ve sayılar: `docs/RTM.md`, `docs/TEST_RESULTS.md` (otomatik üretilir) | - |
| Bu hafta bulunan sorunlar | RSK-28 (500 hatası), RSK-29 (gösterilmeyen hata), RSK-30 (açık olmayan izin denetimi); üçü de kapandı | `docs/RISKS.md` |
| NOT RUN / ÖLÇÜLMEDİ | Hafta 4 E2E Linux'ta koşulmadı (CI E2E koşmaz); yorum ve işlem paneli öğelerinin kontrastı ayrıca ölçülmedi; efor saatleri | - |

## 5. Açık işler

- [ ] TC-INS-01 incelemesini (Hafta 3 ve Hafta 4) tekrarlayıp onaylamak (Burak Nigiz).
- [ ] AK-01 (yeniden açma akışı) öğretim elemanıyla netleştirmek; Faz 5'in durum geçişlerini etkiler.
- [ ] PLN-06: `e2e/week2_auth_roles.py::main` bölünmesi (RSK-07; karmaşıklık 18) Faz 5'e kaldı.
- [ ] Faz 3, 4 ve 5'i öğretim elemanına birlikte göndermek (Rapor #3, #4, #5; PDF ve Word).

## 6. Önemli kararlar

KRR-01..KRR-15 (Hafta 1-3) ve Hafta 4'te eklenenler: KRR-16 işlem geçmişinin değiştirilemezliği uygulama düzeyinde; KRR-17 öncelik kararı (AK-03, KRR-13'ün yerine); KRR-18 proje Faz 5'te biter. Ayrıntı: SDD §9.

## 7. Faz 5 planı (bitiş, son teslim 11.12.2026)

| ID | İş | Gereksinim |
|---|---|---|
| PLN-08 | Durum geçişleri: Open → In Progress → Resolved → Closed; tanımsız geçişin (doğrudan POST dahil) reddi | FR-18 |
| PLN-09 | Geçiş koşulları: atanmış personel veya yönetici ilerletir; talep sahibi veya yönetici kapatır; çözüm açıklaması zorunlu | FR-19 |
| PLN-10 | Durum geçişlerinin işlem geçmişine yazılması; talep ayrıntısında geçmiş görünümü (İstanbul saati, kayıt bazlı erişim) | FR-20, FR-21 |
| PLN-06 | `e2e/week2_auth_roles.py::main` bölünmesi | RSK-07 |
| PLN-11 | Final belgesi (dönem sonu proje teslim dokümanı şablonu), sunum ve demo senaryosu; gelecek çalışma bölümü | KRR-18 |
| PLN-12 | RTM `--week 5`; Rapor #5; `hafta-5` etiketi | - |

Faz 5 başında: Dependabot PR'larını değerlendirin; `CURRENT_WEEK` değerini 5 yapın; durum geçişi izinlerini `ROLE_PERMISSIONS`'a ekleyin (PRC-07, PRC-09).

## 8. Bilinen teknik borç ve notlar

- `e2e/week2_auth_roles.py::main` döngüsel karmaşıklığı 18 (RSK-07, kısmen kapandı; PLN-06).
- İşlem geçmişinin değiştirilemezliği uygulama düzeyindedir (KRR-16); veritabanına doğrudan SQL erişimine karşı koruma yoktur. Kod içinde `QuerySet.update/delete` ile olay kaydı değiştirilmez.
- Atama kaydındaki eski/yeni değer kişinin görünen adıdır (metin); kullanıcının adı sonradan değişirse geçmiş eski adı gösterir. Bu bilinçli bir tercihtir: geçmiş, işlem anındaki durumu yansıtır.
- Kategori adı tekilliği uygulama düzeyinde (Türkçe kurallı) denetlenir; veritabanındaki `unique` kısıtı yalnız birebir aynı adı engeller (kabul edildi).
- E2E çalıştırmadan önce açık sunucu olmadığını doğrulayın (RSK-20); `tools/run_e2e.sh` ve `tools/run_e2e.ps1` bunu denetler.
- RSK-25: Windows'ta yönlendirilmiş çıktı için `PYTHONUTF8=1` gerekir; betikler bunu kendisi ayarlar.
- Rapor şablonundaki "ŞABLONU" ifadesi, üst bilgiyi koruma kuralı nedeniyle olduğu gibi bırakıldı.

## 9. Dosya haritası

```
config/settings.py              profiller, güvenlik, saat dilimi
config/test_runner.py           TC sonuçlarını JSON'a yazan koşucu
servicedesk/models/             user.py (User), ticket.py (Category, Ticket), activity.py (Comment, TicketEvent)
servicedesk/services/           tickets.py (görünürlük politikası, talep, filtre, kategori), assignment.py (üzerine alma,
                                atama, öncelik), comments.py (yorum), audit.py (işlem geçmişine yazım)
servicedesk/views/              dashboard.py, tickets.py, ticket_actions.py (yorum, üzerine al, ata, öncelik), categories.py
servicedesk/forms.py            LoginForm, TicketForm, TicketFilterForm, CategoryForm, CommentForm, AssignForm, PriorityForm
servicedesk/roles.py            roller, ROLE_PERMISSIONS, CAPABILITIES, CURRENT_WEEK, sync_role_groups
servicedesk/text.py             Türkçe kurallı karşılaştırma anahtarı
servicedesk/tests/              test_auth, test_roles, test_security, test_config, test_seed, test_tooling, test_tickets,
                                test_categories, test_architecture, test_assignment, test_comments, test_audit
templates/, servicedesk/templates/  ortak şablonlar; tickets/, categories/
e2e/week2_auth_roles.py         Playwright senaryoları TC-E2E-01..09 (ortak yardımcılar)
e2e/week3_tickets.py            Playwright senaryoları TC-E2E-10..13
e2e/week4_workflow.py           Playwright senaryoları TC-E2E-14..16
tools/                          build_rtm.py, build_report.py, run_e2e.sh, run_e2e.ps1, install_check.sh, install_check.ps1,
                                mutation_check.py, record_ci_run.sh (CI kanıtı)
docs/traceability/*.csv         gereksinim ve test kataloğu (RTM kaynağı)
docs/evidence/hafta-01..04/     haftalık gerçek koşu kayıtları
docs/reports/                   Rapor #1-#4 (docx; Rapor #4 için pdf) ve içerik dosyaları
.github/                        CI ve Release iş akışları, Dependabot
```
