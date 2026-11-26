# Kalite ölçümleri (ISO/IEC 25010:2023 ile ilişkili)

| Alan | Değer |
|---|---|
| Doküman kimliği | SDS07-QM |
| Ölçüm tarihi | 30.10.2026 (Hafta 3 paketi) |
| Ortam | Linux, Python 3.13.18, Django 5.2.18, Chromium 153.0.8010.12 |

Kural: Ölçülmeyen değer "ÖLÇÜLMEDİ" yazılır. Değerler araç çıktılarından alınmıştır; kaynak sütununda belirtilmiştir. Kanıt klasörü: `docs/evidence/hafta-03/`. Hafta 1 ve Hafta 2 değerleri kendi kanıt klasörlerindendir.

Kapsam notu: Resmî değer CI ile aynı komutla (`coverage run manage.py test -v 2`) ölçülür.

## 1. Haftalara göre ölçümler

| Karakteristik / alt karakteristik | Metrik | Hedef eşik | Hafta 1 | Hafta 2 | Hafta 3 | Durum | Kaynak |
|---|---|---|---|---|---|---|---|
| Maintainability / testability | Üretim kodu satır+dal kapsamı (testler ve migration hariç) | ≥ %80 | %87,39 | %92,08 | %94,21 (646/675 satır, 86/102 dal) | Hedefi karşılıyor | `coverage.json` (`-v 2`) |
| Maintainability / analysability | ruff bulgu sayısı | 0 | 0 | 0 | 0 | Hedefi karşılıyor | `ruff.json` |
| Maintainability / modularity (3.7.1) | Uygulama fonksiyonlarının döngüsel karmaşıklığı | Fonksiyon başına ≤ 10 | En yüksek 4 | En yüksek 6 | Ortalama 1,70, medyan 1, en yüksek 6 (`seed_demo_users.handle`; 70 fonksiyon) | Hedefi karşılıyor | ruff C901 ölçümü |
| Maintainability / modularity (3.7.1) | Katman kuralı ihlali (görünümde doğrudan model sorgusu, ters yönlü içe aktarma, erişim denetimsiz görünüm) | 0 | - | - | 0 | Hedefi karşılıyor | TC-ARCH-01, TC-ARCH-02 |
| Maintainability (araçlar) | `tools/` ve `e2e/` döngüsel karmaşıklığı | ≤ 10 | En yüksek 19 | En yüksek 19 | Ortalama 2,80; en yüksek 18 (`week2_auth_roles.main`); `build_report.build` 19 → 4; 65 fonksiyon | **Hedefi aşıyor** (RSK-07, kısmen kapandı) | ruff C901 ölçümü |
| Functional suitability / functional correctness (3.1.2) | Otomatik test geçme oranı | %100 | %100 (8/8) | %100 (35/35, E2E 9/9) | %100 (49/49 Django, 13/13 E2E) | Hedefi karşılıyor | `unit-results.json`, `e2e-*.json` |
| Test etkinliği (destekleyici) | Mutasyon denetiminde yakalanan hata oranı | %100 | - | 4/4 | 8/8 | Hedefi karşılıyor | `mutation-check.md` |
| Security / resistance (3.6.6) | `check --deploy` uyarı sayısı (üretim profili) | 0 (gerekçeli susturma hariç) | 0 | 0 | 0; 1 gerekçeli susturma (security.W021) | Hedefi karşılıyor | `check-deploy.txt` |
| Security / confidentiality (3.6.1) | Başkasına ait talebe doğrudan erişimde sızıntı | 0 (404, içerik var olmayan kayıtla aynı) | - | - | 0 | Hedefi karşılıyor | TC-TKT-07, TC-E2E-11 |
| Interaction capability / inclusivity (3.4.6) | Metin, düğme ve durum rozeti kontrastı | ≥ 4.5:1 | - | En düşük 6,28:1 | Giriş/panel öğeleri Hafta 2 ile aynı (en düşük 6,28:1); Açık rozeti 6,41:1 (tarayıcıda ölçüldü) | Hedefi karşılıyor | TC-E2E-09, TC-E2E-12 |
| Interaction capability / operability (3.4.3) | 360 px'te yatay taşma (sayfa + iç kapsayıcı) | 0 | - | 0 (giriş, panel) | 0 (giriş, panel, talep listesi, talep ayrıntısı) | Hedefi karşılıyor | TC-E2E-07, TC-E2E-12 |
| Flexibility / installability | Temiz ortam kurulumunun başarısı | Linux ve Windows, Python 3.12 ve 3.13 | Linux BAŞARILI | Linux BAŞARILI | Linux 3.12.13 ve 3.13.18 BAŞARILI; Windows 3.13.17 BAŞARILI (elle, 26.11.2026); CI Ubuntu/Windows × 3.12/3.13 başarılı (koşu #5) | Hedefi karşılıyor | TC-INST-01, TC-CI-01 |
| Performance efficiency / time behaviour (3.2.1) | Talep listesi p95 yanıt süresi (1.000 talep) | < 500 ms | - | - | **ÖLÇÜLMEDİ** (özellik var; ölçüm Hafta 11-12'de) | - | NFR-13 |
| Reliability | Hata/arıza oranı | Tanımlanacak | - | - | **ÖLÇÜLMEDİ** | - | - |

Durum rozetlerinin tasarım kontrastı CSS belirteçlerinden hesaplandı: Açık 6,41:1, İşlemde 5,99:1, Çözüldü 5,42:1, Kapandı 5,87:1. Tarayıcıda yalnız Açık rozeti ölçüldü; diğer durumlar Hafta 5'te oluşacak ve o zaman ölçülecek.

Karmaşıklık ölçüm komutu: `ruff check . --select C901 --config "lint.mccabe.max-complexity = 0" --output-format json`.

## 2. Boyut bilgisi (bağlam için)

| Öğe | Hafta 1 | Hafta 2 | Hafta 3 |
|---|---|---|---|
| Uygulama kodu (`config/`, `servicedesk/`; testler ve migration hariç; boş ve yorum satırı hariç, belge dizeleri dahil) | 325 satır | 649 satır | 1.117 satır |
| Test kodu | 236 satır | 601 satır | 942 satır |
| Araç kodu (`tools/*.py`, `e2e/*.py`) | 549 satır | 981 satır | 1.239 satır |
| Şablonlar (boş olmayan satır) | 0 | 329 satır (13 dosya) | 613 satır (19 dosya) |
| `app.css` (boş olmayan satır) | - | 283 satır | 355 satır |
| Sabitlenmiş çalışma zamanı bağımlılığı | 4 | 4 | 4 (yeni bağımlılık eklenmedi) |
| Django test süresi (test başına sürelerin toplamı) | 1,69 sn (8 test) | 10,94 sn (35 test) | 12,66 sn (49 test; en uzun TC-SEED-01, 4,39 sn) |
