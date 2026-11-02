# PROJECT_STATE: SDS-07 Servis Masası (Hafta 2 paketi)

**Son güncelleme:** 30.10.2026 (Europe/Istanbul). **Hafta 2: TAMAMLANDI**. **Sıradaki: Hafta 3**: talep oluşturma ve listeleme, kayıt bazlı erişim, kategoriler, modüler mimari.

> Hafta 1-3 paketleri geç kayıt nedeniyle 30.10.2026'da birlikte hazırlandı. Kanıt dosyalarındaki tarihler gerçek koşu tarihleridir; geriye tarih atılmadı. Hafta 1 ve Hafta 2 kodu aynı gün yazıldı; bu paket o kodun Hafta 2 sonundaki anlık görüntüsüdür ve buradaki bütün test ve ölçümler bu anlık görüntü üzerinde koşuldu.

## 0. Belgelerin okunma sırası

1. Bu dosyayı, sonra `docs/SRS.md` (§2.6 haftalık plan, §10 açık konular), `docs/SDD.md` ve `docs/RTM.md` dosyalarını okuyun.
2. Kodun güncel kopyası: https://github.com/wordeus/sds07-servis-masasi (Hafta 2: `hafta-2` etiketi).
3. Kurulum: `docs/INSTALL.md`. Testler ve RTM: `docs/TEST_PLAN.md §6`.
4. Yalnız aktif haftanın kapsamını uygulayın (proje talimatı). Gerçek kanıt kuralı geçerlidir: koşulmayan test NOT RUN, yapılmayan ölçüm ÖLÇÜLMEDİ.

## 1. Proje ve kapsam

ISO 9001 ilkelerini destekleyen IT Servis Masası ve Süreç Takip Sistemi. Roller Talep Sahibi, Destek Personeli ve Yönetici. Talep/incident akışı Open → In Progress → Resolved → Closed. Kapsamda değişiklik yönetimi, SLA (7/24, ilk yanıt ve çözüm ayrı), uyarı/eskalasyon, 1-5 memnuniyet puanı, KPI paneli, işlem geçmişi ve uygunsuzluk/DÖF kaydı var. Kapsam dışı: REST API, SPA, JWT, mikroservis, e-posta vb. Ayrıntı: SRS §1.2. Proje tek kişiliktir: Burak Nigiz (2100002062).

## 2. Ortam ve sürümler (30.10.2026)

| Öğe | Değer |
|---|---|
| Django | 5.2.18 (5.2 LTS'nin PyPI'deki son yaması, 06.10.2026; uzatılmış destek Nisan 2028) |
| Python | 3.13.18 ve 3.12.13 ile test edildi (Linux) |
| Bootstrap | 5.3.8 (yerel dosya); yazı tipi IBM Plex Sans 5.3.0 (OFL, yerel) |
| Diğer sabitler | asgiref 3.13.0, sqlparse 0.6.0, tzdata 2026.6 (yalnız Windows), coverage 7.17.0, ruff 0.17.3, playwright 1.63.0, lxml 6.1.3 |
| Standart baskıları | ISO 9001:2026, ISO/IEC/IEEE 12207:2026, ISO/IEC/IEEE 29148:2018, IEEE 1016-2009 (Inactive-Reserved), ISO/IEC 25010:2023, IEEE 1012-2024. Ayrıntı: `docs/STANDARDS.md` |
| Test ortamı | Linux (bulut sunucu), tarayıcı testleri için Playwright/Chromium. Windows'ta elle henüz çalıştırılmadı; Windows doğrulaması GitHub Actions ile yapılıyor. Depo: https://github.com/wordeus/sds07-servis-masasi |

## 3. Hafta 2'de tamamlananlar

| İş | Çıktı | Kanıt |
|---|---|---|
| Giriş/çıkış (POST), güvenli `next`, genel hata mesajı | `config/urls.py`, `servicedesk/forms.py` | TC-AUTH-01..10 |
| Rol grupları (post_migrate senkronizasyonu), rol-izin matrisi, sunucu tarafı yetki, rol menüsü, admin rol atama, demo komutu | `servicedesk/roles.py`, `views.py`, `admin.py`, `seed_demo_users.py`, migration 0002 | TC-ROLE-01..12, TC-SEED-01..02 |
| CSRF ve oturum çerezi kuralları | `config/settings.py` | TC-SEC-02, TC-SEC-03 |
| Arayüz: Türkçe, Bootstrap teması, giriş sayfası süreç paneli, 403/404/500/CSRF sayfaları, mobil tablo düzeni | `templates/`, `static/css/app.css` | TC-CFG-04, TC-E2E-01..09, ekran görüntüleri |
| E2E betiği (port denetimli), mutasyon denetimi | `e2e/week2_auth_roles.py`, `tools/run_e2e.sh`, `tools/mutation_check.py` | `evidence/hafta-02/` |
| SDD v0.1 (bağlam, bileşen, ER, durum, etkileşim), karar günlüğü KRR-01..KRR-10 | `docs/SDD.md`, `docs/diagrams/` | - |
| SRS v0.2 (rol matrisi koddan), STANDARDS v0.2, RISKS v0.2, TEST_PLAN v0.2, kalite ölçümleri, prosedürler, kod rehberi | `docs/*.md`, `CHANGELOG.md` | - |
| Rapor #2 (özgün şablon, beş başlık korunarak) | `docs/reports/Rapor-02_Hafta-2.docx` (+ `rapor-02.content.json`) | XSD doğrulaması |

## 4. Gerçek test ve ölçüm sonuçları (30.10.2026)

| Grup | Sonuç | Kaynak |
|---|---|---|
| Django birim/entegrasyon/sistem | 35/35 PASS (Python 3.13.18, Django 5.2.18) | `evidence/hafta-02/unit-results.json` |
| Tarayıcı E2E (Chromium 153.0.8010.12) | 9/9 PASS | `evidence/hafta-02/e2e-results.json` |
| Kapsam (üretim kodu, `-v 2`) | %92,08 (eşik %80) | `evidence/hafta-02/coverage.json` |
| ruff | 0 bulgu (Hafta 1-2 kodunun ilk koşusunda 13, RSK-17) | `evidence/hafta-02/ruff.json` |
| `check --deploy` (üretim) | 0 sorun, 1 gerekçeli susturma (W021) | `evidence/hafta-02/check-deploy.txt` |
| Temiz kurulum (TC-INST-01) | Linux 3.12.13 ve 3.13.18 BAŞARILI | `evidence/hafta-02/install-check-linux-py31*.log` |
| Mutasyon denetimi | 4/4 yakalandı (35 test) | `evidence/hafta-02/mutation-check.md` |
| RTM (`--week 2`) | Hafta 1-2'nin 23 gereksiniminin 22'si PASS, 1'i KISMİ (NFR-11); 30 gereksinim PLANLANDI. Test kataloğu: 48 PASS, 1 NOT RUN (TC-CI-01) | `docs/RTM.md`, `docs/TEST_RESULTS.md` |
| NOT RUN / ÖLÇÜLMEDİ | TC-CI-01 (GitHub yok), Windows kurulumu, Firefox E2E, performans (NFR-13), efor saatleri | - |

## 5. Açık işler

- [ ] Hafta 2'nin GitHub Actions sonucunu TC-CI-01 kanıtı olarak eklemek (Hafta 1'in ilk koşusu 02.11.2026'da 4/4 başarılı).
- [ ] Windows'ta kurulum ve testleri bir kez elle çalıştırıp sonucu kaydetmek (NFR-11).
- [ ] TC-INS-01 incelemesini tekrarlayıp onaylamak.
- [ ] Açık konuları netleştirmek: yeniden açma akışı (AK-01), önceliği kimin seçeceği (AK-03). Standart baskıları için karar: en güncel baskılar (AK-05).

## 6. Önemli kararlar

KRR-01 tek proje + tek uygulama; KRR-02 özel User; KRR-03 iki ayar profili; KRR-04 JSON test sonucu + otomatik RTM; KRR-05 haftalık paketler ve `--week`; KRR-06 rol = grup, yetki = izin, matris kodda, `post_migrate` eşitleme; KRR-07 rol düzeyinde 403, kayıt düzeyinde 404; KRR-08 yerel Bootstrap/yazı tipi; KRR-09 çıkış yalnız POST; KRR-10 SLA için yönetim komutu + işletim sistemi zamanlayıcısı. Ayrıntı: SDD §9.

## 7. Hafta 3 planı

| ID | İş | Gereksinim |
|---|---|---|
| PLN-01 | Ticket ve Category modelleri; talep oluşturma, listeleme, filtre (durum, öncelik, kategori, atanan), sayfalama (25) | FR-12, FR-13 |
| PLN-02 | Kayıt bazlı erişim politikası (tek politika fonksiyonu), başkasının talebine doğrudan adresle 404 testleri | FR-14, RSK-08 |
| PLN-03 | Kategori ekleme ve pasifleştirme (Yönetici) | FR-15 |
| PLN-04 | `models/`, `services/`, `views/` paketleri; görünümlerin model sorgusunu doğrudan yapmadığını denetleyen mimari testi; SDD v0.2 | NFR-16 |
| PLN-05 | GitHub + ilk CI koşusu + Windows doğrulaması | NFR-11, TC-CI-01 |
| PLN-06 | RTM `--week 3`; Rapor #3 | - |

Hafta 3 başında yapılacaklar: Django 5.2.19 yayımlandıysa sürüm notlarını okuyup sabitlemeyi güncelleyin. `ROLE_PERMISSIONS`'a `add_ticket`, `view_ticket` ve benzeri izinleri ekleyin (PRC-07). `CURRENT_WEEK` değerini 3 yapın.

## 8. Bilinen teknik borç ve notlar

- `tools/build_report.py::build` (19) ve `e2e/week2_auth_roles.py::main` (18) döngüsel karmaşıklık eşiğini aşıyor (RSK-07).
- Destek kuyruğu ve yönetim paneli şimdilik yalnız erişim kontrollü iskelet sayfalardır.
- E2E çalıştırmadan önce açık sunucu olmadığını doğrulayın (RSK-20); `tools/run_e2e.sh` bunu denetler.
- Kapsam değeri ayrıntı düzeyine göre değişir; resmî ölçüm `-v 2` iledir.
- Rapor şablonundaki "ŞABLONU" ifadesi, üst bilgiyi koruma kuralı nedeniyle olduğu gibi bırakıldı.

## 9. Dosya haritası

```
config/settings.py           profiller, güvenlik, saat dilimi
config/test_runner.py        TC sonuçlarını JSON'a yazan koşucu
servicedesk/roles.py         roller, ROLE_PERMISSIONS, CAPABILITIES, CURRENT_WEEK, sync_role_groups
servicedesk/views.py         panel, destek kuyruğu, yönetim paneli
servicedesk/tests/           test_auth, test_roles, test_security, test_config, test_seed, test_tooling
templates/                   base, partials, registration/login, 403/404/500/403_csrf
e2e/week2_auth_roles.py      Playwright senaryoları (TC-E2E-01..09)
tools/build_rtm.py           RTM + TEST_RESULTS üretici (--week)
tools/run_e2e.sh             E2E koşu betiği (port denetimli)
tools/install_check.sh       temiz kurulum denetimi (TC-INST-01)
tools/mutation_check.py      mutasyon denetimi
tools/build_report.py        Word rapor üretici (şablon + JSON içerik)
docs/traceability/*.csv      gereksinim ve test kataloğu (RTM kaynağı)
docs/evidence/hafta-01/      Hafta 1 koşu kayıtları
docs/evidence/hafta-02/      Hafta 2 koşu kayıtları, ekran görüntüleri, ilk denemeler
docs/reports/                Rapor #1 ve #2 (docx) ve içerik dosyaları
```
