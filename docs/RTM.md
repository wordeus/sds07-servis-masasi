# Gereksinim İzlenebilirlik Matrisi (RTM)

> Bu dosya `tools/build_rtm.py` tarafından gerçek test çıktılarından üretilir; elle düzenlemeyin.
> Kaynaklar: `docs/traceability/requirements.csv`, `docs/traceability/tests.csv` ve aşağıdaki sonuç dosyaları.
> Üretim: 26.11.2026 11:06 (Europe/Istanbul) · Aktif hafta: 4

## Çalıştırma kayıtları

| Kaynak | Tür | Başlangıç (İstanbul) | Ortam | Özet |
|---|---|---|---|---|
| `docs/evidence/hafta-04/unit-results.json` | django-unit-integration | 26.11.2026 04:14 | python 3.13.17, django 5.2.19, platform Windows-11-10.0.26300-SP0 | run=62, failures=0, errors=0, skipped=0, successful=True |
| `docs/evidence/hafta-04/e2e-results.json` | e2e-playwright | 26.11.2026 04:16 | browser chromium 159.0.8154.6, python 3.13.17, platform Windows-11-10.0.26300-SP0 | run=9, failures=0, errors=0, successful=True |
| `docs/evidence/hafta-04/e2e-week3-results.json` | e2e-playwright | 26.11.2026 04:16 | browser chromium 159.0.8154.6, python 3.13.17, platform Windows-11-10.0.26300-SP0 | run=4, failures=0, errors=0, successful=True |
| `docs/evidence/hafta-04/e2e-week4-results.json` | e2e-playwright | 26.11.2026 04:16 | browser chromium 159.0.8154.6, python 3.13.17, platform Windows-11-10.0.26300-SP0 | run=3, failures=0, errors=0, successful=True |
| `docs/evidence/hafta-04/manual-checks.json` | manual-and-scripted-checks | 26.11.2026 04:17 | platform Windows 11 Pro 10.0.26300 (Burak Nigiz'in bilgisayarı) | run=2, failures=0, not_run=0 |
| `docs/evidence/hafta-04/ci-github-actions-2026-11-26.json` | github-actions | 26.11.2026 11:04 | platform GitHub Actions: ubuntu-latest ve windows-latest, Python 3.12 ve 3.13 | run=1, failures=0, jobs_passed=4, jobs_total=4 |
| ölçüm | coverage_percent | - | - | 95.04 |
| ölçüm | ruff_findings | - | - | 0 |

## Gereksinim → mimari bileşen → test → gerçek sonuç

| ID | Tip | Gereksinim (kısa) | Öncelik | Kaynak | Mimari bileşen (SDD) | Doğrulama yöntemi | Test ID (STD) | Hafta | Gerçek sonuç |
|---|---|---|---|---|---|---|---|---|---|
| FR-01 | FR | Kullanıcı adı ve parola ile giriş | Çok Yüksek | PT-Ü1; PT-TEK | MOD-AUTH | Test | TC-AUTH-01 (PASS), TC-AUTH-02 (PASS), TC-AUTH-03 (PASS), TC-E2E-01 (PASS), TC-E2E-02 (PASS) | 2 | PASS |
| FR-02 | FR | Başarısız girişte genel hata ve oturum açılmaması | Yüksek | PT-Ü1; DJ-SEC | MOD-AUTH | Test | TC-AUTH-04 (PASS), TC-AUTH-05 (PASS) | 2 | PASS |
| FR-03 | FR | Yalnız POST ile güvenli çıkış | Yüksek | PT-Ü1; DJ-SEC | MOD-AUTH | Test | TC-AUTH-06 (PASS), TC-AUTH-07 (PASS), TC-E2E-06 (PASS) | 2 | PASS |
| FR-04 | FR | Tüm uygulama sayfalarında oturum zorunluluğu | Çok Yüksek | PT-YK | MOD-AUTH | Test | TC-AUTH-08 (PASS), TC-TKT-03 (PASS) | 2 | PASS |
| FR-05 | FR | Girişten sonra yalnız site içi yönlendirme | Yüksek | DJ-SEC | MOD-AUTH | Test | TC-AUTH-09 (PASS), TC-AUTH-10 (PASS) | 2 | PASS |
| FR-06 | FR | Rol gruplarının otomatik ve tekrarlanabilir oluşturulması | Çok Yüksek | PT-Ü1; PT-TEK | MOD-ROLE | Test | TC-ROLE-01 (PASS), TC-ROLE-02 (PASS), TC-ROLE-03 (PASS) | 2 | PASS |
| FR-07 | FR | Sistem yöneticisinin rol ataması | Yüksek | PT-Ü1 | MOD-ROLE | Test | TC-ROLE-04 (PASS) | 2 | PASS |
| FR-08 | FR | Rolün belirlenmesi ve gösterilmesi | Yüksek | PT-Ü1 | MOD-ROLE; MOD-UI | Test | TC-ROLE-05 (PASS), TC-ROLE-06 (PASS), TC-E2E-02 (PASS) | 2 | PASS |
| FR-09 | FR | Sunucu tarafı rol yetkilendirmesi (adres ve form isteklerinde) | Çok Yüksek | PT-YK | MOD-ROLE | Test | TC-ROLE-07 (PASS), TC-ROLE-08 (PASS), TC-ROLE-09 (PASS), TC-ROLE-10 (PASS), TC-ROLE-11 (PASS), TC-E2E-03 (PASS), TC-E2E-04 (PASS), TC-E2E-05 (PASS), TC-TKT-03 (PASS), TC-CAT-03 (PASS), TC-ARCH-02 (PASS), TC-ASN-03 (PASS) | 2 | PASS |
| FR-10 | FR | Role göre gezinme menüsü | Orta | PT-YK | MOD-UI | Test | TC-ROLE-12 (PASS), TC-E2E-02 (PASS), TC-E2E-05 (PASS), TC-ROLE-13 (PASS) | 2 | PASS |
| FR-11 | FR | Geliştirme ortamı için demo kullanıcı komutu | Düşük | PT-ÇB | MOD-ROLE | Test | TC-SEED-01 (PASS), TC-SEED-02 (PASS) | 2 | PASS |
| FR-12 | FR | Talep oluşturma (numara ve Open durumu) | Çok Yüksek | PT-Ü2 | MOD-TICKET | Test | TC-TKT-01 (PASS), TC-TKT-02 (PASS), TC-TKT-03 (PASS), TC-TKT-08 (PASS), TC-E2E-10 (PASS) | 3 | PASS |
| FR-13 | FR | Talep listeleme ve filtreleme | Yüksek | PT-Ü2 | MOD-TICKET | Test | TC-TKT-04 (PASS), TC-TKT-05 (PASS), TC-TKT-06 (PASS), TC-E2E-10 (PASS), TC-E2E-12 (PASS) | 3 | PASS |
| FR-14 | FR | Kayıt bazlı erişim: talep sahibi yalnız kendi kayıtları | Çok Yüksek | PT-YK | MOD-TICKET; MOD-ROLE | Test | TC-TKT-04 (PASS), TC-TKT-05 (PASS), TC-TKT-07 (PASS), TC-TKT-08 (PASS), TC-E2E-11 (PASS), TC-CMT-03 (PASS), TC-E2E-16 (PASS) | 3 | PASS |
| FR-15 | FR | Kategori yönetimi | Orta | PT-Ü2 | MOD-TICKET | Test | TC-TKT-02 (PASS), TC-CAT-01 (PASS), TC-CAT-02 (PASS), TC-CAT-03 (PASS), TC-E2E-13 (PASS) | 3 | PASS |
| FR-16 | FR | Talep atama ve üzerine alma | Yüksek | PT-Ü2 | MOD-TICKET | Test | TC-ASN-01 (PASS), TC-ASN-02 (PASS), TC-ASN-03 (PASS), TC-ASN-05 (PASS), TC-ROLE-14 (PASS), TC-E2E-14 (PASS), TC-E2E-15 (PASS) | 4 | PASS |
| FR-17 | FR | Talebe yorum ekleme | Yüksek | PT-Ü2 | MOD-TICKET | Test | TC-CMT-01 (PASS), TC-CMT-02 (PASS), TC-CMT-03 (PASS), TC-CMT-04 (PASS), TC-ROLE-14 (PASS), TC-E2E-14 (PASS), TC-E2E-15 (PASS) | 4 | PASS |
| FR-18 | FR | Incident durum makinesi (Open → In Progress → Resolved → Closed) | Çok Yüksek | PT-Ü3 | MOD-WF | Test | - | 5 | PLANLANDI (Hafta 5) |
| FR-19 | FR | Durum geçiş yetkileri ve zorunlu çözüm açıklaması | Çok Yüksek | PT-Ü3; PT-YK | MOD-WF | Test | - | 5 | PLANLANDI (Hafta 5) |
| FR-20 | FR | Değiştirilemez işlem geçmişi kaydı | Çok Yüksek | PT-Ü9 | MOD-AUDIT | Test | TC-AUD-01 (PASS), TC-AUD-02 (PASS), TC-AUD-03 (PASS), TC-ASN-04 (PASS) | 4-5 | PASS |
| FR-21 | FR | İşlem geçmişinin görüntülenmesi | Yüksek | PT-Ü9; PT-YK | MOD-AUDIT | Test | - | 5 | PLANLANDI (Hafta 5) |
| FR-22 | FR | Değişiklik kaydı (gerekçe; etki; risk; geri dönüş planı) | Yüksek | PT-Ü4 | MOD-CHANGE | Test | - | kapsam dışı | KAPSAM DIŞI (gelecek çalışma) |
| FR-23 | FR | Yönetici onayı/reddi ve görevler ayrılığı | Çok Yüksek | PT-Ü4 | MOD-CHANGE | Test | - | kapsam dışı | KAPSAM DIŞI (gelecek çalışma) |
| FR-24 | FR | Onaysız değişikliğin uygulanmasının engellenmesi | Çok Yüksek | PT-YK; PT-Ü4 | MOD-CHANGE | Test | - | kapsam dışı | KAPSAM DIŞI (gelecek çalışma) |
| FR-25 | FR | Değişiklik uygulama sonucunun kaydı | Yüksek | PT-Ü4 | MOD-CHANGE | Test | - | kapsam dışı | KAPSAM DIŞI (gelecek çalışma) |
| FR-26 | FR | Önceliğe göre ilk yanıt ve çözüm SLA hedefleri | Yüksek | PT-Ü5; PT-SLA | MOD-SLA | Test | - | kapsam dışı | KAPSAM DIŞI (gelecek çalışma) |
| FR-27 | FR | SLA ölçüm kuralları ve süre sınırları | Çok Yüksek | PT-SLA | MOD-SLA | Test | - | kapsam dışı | KAPSAM DIŞI (gelecek çalışma) |
| FR-28 | FR | Süre dolmadan uygulama içi uyarı | Yüksek | PT-Ü6 | MOD-SLA; MOD-NOTIF | Test | - | kapsam dışı | KAPSAM DIŞI (gelecek çalışma) |
| FR-29 | FR | SLA ihlalinde yöneticiye eskalasyon | Yüksek | PT-Ü6 | MOD-SLA; MOD-NOTIF | Test | - | kapsam dışı | KAPSAM DIŞI (gelecek çalışma) |
| FR-30 | FR | Tekrarlanabilir SLA kontrolü ve mükerrer bildirim engeli | Yüksek | PT-SLA | MOD-SLA | Test | - | kapsam dışı | KAPSAM DIŞI (gelecek çalışma) |
| FR-31 | FR | Uygulama içi bildirim kutusu | Orta | PT-Ü6 | MOD-NOTIF | Test | - | kapsam dışı | KAPSAM DIŞI (gelecek çalışma) |
| FR-32 | FR | Kapanmış talebe bir kez 1–5 memnuniyet puanı | Yüksek | PT-Ü7 | MOD-SURVEY | Test | - | kapsam dışı | KAPSAM DIŞI (gelecek çalışma) |
| FR-33 | FR | KPI paneli | Yüksek | PT-Ü8 | MOD-KPI | Test | - | kapsam dışı | KAPSAM DIŞI (gelecek çalışma) |
| FR-34 | FR | KPI pay/payda ve dönem kuralları | Yüksek | PT-SLA; PT-Ü8 | MOD-KPI | Test | - | kapsam dışı | KAPSAM DIŞI (gelecek çalışma) |
| FR-35 | FR | Uygunsuzluk kaydı | Yüksek | PT-Ü10 | MOD-CAPA | Test | - | kapsam dışı | KAPSAM DIŞI (gelecek çalışma) |
| FR-36 | FR | Kök neden analizi ve düzeltici faaliyet | Yüksek | PT-Ü10 | MOD-CAPA | Test | - | kapsam dışı | KAPSAM DIŞI (gelecek çalışma) |
| FR-37 | FR | Düzeltici faaliyetin etkinlik kontrolü | Yüksek | PT-Ü10 | MOD-CAPA | Test | - | kapsam dışı | KAPSAM DIŞI (gelecek çalışma) |
| NFR-01 | NFR | Parolaların özetlenerek saklanması ve parola kuralları | Çok Yüksek | DJ-SEC | MOD-AUTH; MOD-CFG | Test | TC-SEC-01 (PASS) | 1 | PASS |
| NFR-02 | NFR | Durum değiştiren isteklerde CSRF koruması | Çok Yüksek | DJ-SEC | MOD-CFG | Test | TC-SEC-02 (PASS), TC-CAT-02 (PASS) | 2 | PASS |
| NFR-03 | NFR | Oturum çerezi güvenliği ve 8 saatlik oturum süresi | Yüksek | DJ-SEC | MOD-CFG | Test | TC-SEC-03 (PASS), TC-CFG-03 (PASS) | 2 | PASS |
| NFR-04 | NFR | Üretim yapılandırmasının güvenli başlaması | Çok Yüksek | DJ-SEC | MOD-CFG | Test | TC-CFG-02 (PASS), TC-CFG-03 (PASS), TC-CFG-05 (PASS) | 1 | PASS |
| NFR-05 | NFR | Zamanın UTC saklanması ve Europe/Istanbul gösterimi | Çok Yüksek | PT-SLA | MOD-CFG | Test | TC-CFG-01 (PASS), TC-TKT-08 (PASS) | 1 | PASS |
| NFR-06 | NFR | Türkçe arayüz | Yüksek | EKİP | MOD-UI | Test | TC-CFG-04 (PASS), TC-E2E-01 (PASS) | 2 | PASS |
| NFR-07 | NFR | 360 px genişlikte yatay kaydırmasız kullanım | Orta | EKİP | MOD-UI | Test | TC-E2E-07 (PASS), TC-E2E-12 (PASS), TC-E2E-16 (PASS) | 2 | PASS |
| NFR-08 | NFR | Klavye erişimi; görünür odak ve 4.5:1 kontrast | Orta | EKİP | MOD-UI | Test | TC-E2E-08 (PASS), TC-E2E-09 (PASS), TC-E2E-12 (PASS), TC-CMT-02 (PASS), TC-E2E-15 (PASS) | 2 | PASS |
| NFR-09 | NFR | Otomatik test; ≥ %80 kapsam ve makinece okunur sonuç | Yüksek | PT-KNT; PT-ÇB | MOD-CFG | Analiz; Test | TC-QA-01 (PASS), TC-QA-03 (PASS), TC-QA-04 (PASS) | 1 | PASS |
| NFR-10 | NFR | Statik analizde sıfır bulgu | Orta | PT-ÇB | MOD-CFG | Analiz | TC-QA-02 (PASS) | 1 | PASS |
| NFR-11 | NFR | Sabit bağımlılıklarla Windows ve Ubuntu'da kurulabilirlik | Yüksek | PT-TEK | MOD-CFG | Test | TC-INST-01 (PASS), TC-CFG-06 (PASS), TC-CI-01 (PASS) | 1 | PASS |
| NFR-12 | NFR | Kişisel veri asgarisi | Yüksek | EKİP | MOD-AUTH | İnceleme | TC-INS-01 (PASS) | 1 | PASS |
| NFR-13 | NFR | Talep listesi yanıt süresi (p95 < 500 ms; 1.000 kayıt) | Orta | EKİP | MOD-TICKET | Test | - | kapsam dışı | KAPSAM DIŞI (gelecek çalışma) |
| NFR-14 | NFR | Yetkisiz erişim denemelerinin günlüğe yazılması | Orta | EKİP | MOD-ROLE | Test | - | kapsam dışı | KAPSAM DIŞI (gelecek çalışma) |
| NFR-15 | NFR | Tarayıcı uyumluluğu (Chromium ve Firefox) | Orta | EKİP | MOD-UI | Test | - | kapsam dışı | KAPSAM DIŞI (gelecek çalışma) |
| NFR-16 | NFR | Modüler yapı: iş kuralları servis katmanında | Orta | PT-TEK | MOD-UI; MOD-TICKET | Analiz | TC-ARCH-01 (PASS), TC-ARCH-02 (PASS) | 3 | PASS |

## Özet

| Durum | Gereksinim sayısı |
|---|---|
| KAPSAM DIŞI | 19 |
| PASS | 31 |
| PLANLANDI | 3 |

## Standart eşlemesi (bilgi amaçlı)

| ID | ISO 9001:2026 maddesi | ISO/IEC 25010:2023 karakteristiği / alt karakteristiği |
|---|---|---|
| FR-01 | 7.5.3 | Security / authenticity (3.6.5) |
| FR-02 | 7.5.3 | Security / confidentiality (3.6.1) |
| FR-03 | 7.5.3 | Security / integrity (3.6.2) |
| FR-04 | 7.5.3 | Security / confidentiality (3.6.1) |
| FR-05 | 7.5.3 | Security / resistance (3.6.6) |
| FR-06 | 5.3 | Functional suitability / functional correctness (3.1.2) |
| FR-07 | 5.3 | Functional suitability / functional completeness (3.1.1) |
| FR-08 | 5.3 | Interaction capability / appropriateness recognizability (3.4.1) |
| FR-09 | 5.3; 7.5.3 | Security / confidentiality (3.6.1) |
| FR-10 | 5.3 | Interaction capability / operability (3.4.3) |
| FR-11 | - | Security / confidentiality (3.6.1) |
| FR-12 | 8.2.1; 8.2.2 | Functional suitability / functional completeness (3.1.1) |
| FR-13 | 8.5.1 | Interaction capability / operability (3.4.3) |
| FR-14 | 7.5.3 | Security / confidentiality (3.6.1) |
| FR-15 | 8.5.1 | Functional suitability / functional completeness (3.1.1) |
| FR-16 | 5.3; 8.5.1 | Functional suitability / functional correctness (3.1.2) |
| FR-17 | 8.2.1 | Functional suitability / functional completeness (3.1.1) |
| FR-18 | 8.5.1 | Functional suitability / functional correctness (3.1.2) |
| FR-19 | 8.5.1; 8.6 | Security / integrity (3.6.2) |
| FR-20 | 7.5.3; 8.5.2 | Security / accountability (3.6.4) |
| FR-21 | 8.5.2 | Security / accountability (3.6.4) |
| FR-22 | 8.5.6 | Functional suitability / functional completeness (3.1.1) |
| FR-23 | 8.5.6; 5.3 | Security / integrity (3.6.2) |
| FR-24 | 8.5.6 | Security / integrity (3.6.2) |
| FR-25 | 8.5.6; 7.5.3 | Security / accountability (3.6.4) |
| FR-26 | 6.2; 9.1.1 | Functional suitability / functional completeness (3.1.1) |
| FR-27 | 9.1.1 | Functional suitability / functional correctness (3.1.2) |
| FR-28 | 9.1.1 | Functional suitability / functional appropriateness (3.1.3) |
| FR-29 | 5.1.2; 9.1.1 | Functional suitability / functional appropriateness (3.1.3) |
| FR-30 | 9.1.1 | Reliability / faultlessness (3.5.1) |
| FR-31 | 7.4 | Interaction capability / operability (3.4.3) |
| FR-32 | 9.1.2 | Functional suitability / functional correctness (3.1.2) |
| FR-33 | 9.1.3; 9.3.2 | Functional suitability / functional completeness (3.1.1) |
| FR-34 | 9.1.3 | Functional suitability / functional correctness (3.1.2) |
| FR-35 | 10.2 | Functional suitability / functional completeness (3.1.1) |
| FR-36 | 10.2 | Functional suitability / functional completeness (3.1.1) |
| FR-37 | 10.2; 10.1 | Functional suitability / functional correctness (3.1.2) |
| NFR-01 | 7.5.3 | Security / confidentiality (3.6.1) |
| NFR-02 | 7.5.3 | Security / integrity (3.6.2) |
| NFR-03 | 7.5.3 | Security / confidentiality (3.6.1) |
| NFR-04 | 7.1.3 | Security / resistance (3.6.6) |
| NFR-05 | 7.1.5 | Functional suitability / functional correctness (3.1.2) |
| NFR-06 | - | Interaction capability / learnability (3.4.2) |
| NFR-07 | - | Interaction capability / operability (3.4.3) |
| NFR-08 | - | Interaction capability / inclusivity (3.4.6) |
| NFR-09 | 7.1.5; 9.1.1 | Maintainability / testability |
| NFR-10 | - | Maintainability / analysability |
| NFR-11 | 7.1.3 | Flexibility / installability |
| NFR-12 | 7.5.3 | Security / confidentiality (3.6.1) |
| NFR-13 | - | Performance efficiency / time behaviour (3.2.1) |
| NFR-14 | 9.1.1 | Security / accountability (3.6.4) |
| NFR-15 | - | Flexibility / adaptability |
| NFR-16 | - | Maintainability / modularity (3.7.1) |

Madde numaralarının doğrulama durumu için `docs/STANDARDS.md` dosyasına bakın.

## Tutarlılık denetimi

- Sorun bulunmadı (izlenemeyen test, testsiz aktif gereksinim veya başarısız test yok).
