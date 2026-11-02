# Kalite ölçümleri (ISO/IEC 25010:2023 ile ilişkili)

| Alan | Değer |
|---|---|
| Doküman kimliği | SDS07-QM |
| Ölçüm tarihi | 30.10.2026 (Hafta 2 paketi) |
| Ortam | Linux, Python 3.13.18, Django 5.2.18, Chromium 153.0.8010.12 |

Kural: Ölçülmeyen değer "ÖLÇÜLMEDİ" yazılır. Değerler araç çıktılarından alınmıştır; kaynak sütununda belirtilmiştir. Kanıt klasörü: `docs/evidence/hafta-02/`. Hafta 1 değerleri `docs/evidence/hafta-01/` klasöründe ve Hafta 1 paketindeki bu belgededir.

Kapsam notu: Resmî değer CI ile aynı komutla (`coverage run manage.py test -v 2`) ölçülür. Varsayılan ayrıntı düzeyinde ölçüm daha düşük çıkar (347/374 satır); fark, `roles.py` içindeki ve yalnız ayrıntılı `migrate` çıktısında çalışan yazdırma dalından gelir.

## 1. Hafta 2 ölçümleri

| Karakteristik / alt karakteristik | Metrik | Hedef eşik | Hafta 1 | Hafta 2 | Durum | Kaynak |
|---|---|---|---|---|---|---|
| Maintainability / testability | Üretim kodu satır+dal kapsamı (testler ve migration hariç) | ≥ %80 | %87,39 | %92,08 (351/374 satır, 56/68 dal) | Hedefi karşılıyor | `coverage.json` (`-v 2` koşusu) |
| Maintainability / analysability | ruff bulgu sayısı | 0 | 0 | 0 (Hafta 1-2 kodunun ilk koşusunda 13, RSK-17) | Hedefi karşılıyor | `ruff.json` |
| Maintainability / modularity (3.7.1) | Uygulama fonksiyonlarının döngüsel karmaşıklığı | Fonksiyon başına ≤ 10 | En yüksek 4 | Ortalama 1,83, medyan 1, en yüksek 6 (`seed_demo_users.handle`; 36 fonksiyon) | Hedefi karşılıyor | ruff C901 ölçümü |
| Maintainability (araçlar) | `tools/` ve `e2e/` döngüsel karmaşıklığı | ≤ 10 | En yüksek 19 | Ortalama 3,15; en yüksek 19 (`build_report.build`) ve 18 (`week2_auth_roles.main`); 52 fonksiyon | **Hedefi aşıyor** (RSK-07) | ruff C901 ölçümü |
| Functional suitability / functional correctness (3.1.2) | Otomatik test geçme oranı | %100 | %100 (8/8) | %100 (35/35 Django, 9/9 E2E) | Hedefi karşılıyor | `unit-results.json`, `e2e-results.json` |
| Test etkinliği (destekleyici) | Mutasyon denetiminde yakalanan hata oranı | %100 | - | 4/4 | Hedefi karşılıyor | `mutation-check.md` |
| Security / resistance (3.6.6) | `check --deploy` uyarı sayısı (üretim profili) | 0 (gerekçeli susturma hariç) | 0 | 0; 1 gerekçeli susturma (security.W021) | Hedefi karşılıyor | `check-deploy.txt` |
| Security / confidentiality (3.6.1) | Parola özet algoritması | PBKDF2-SHA256 veya daha güçlü | PBKDF2-SHA256 | PBKDF2-SHA256 | Hedefi karşılıyor | TC-SEC-01 |
| Interaction capability / inclusivity (3.4.6) | Metin/düğme kontrast oranı (ölçülen 7 öğe) | ≥ 4.5:1 | - | En düşük 6,28:1 (ikincil metin); birincil düğme 15,95:1 | Hedefi karşılıyor | TC-E2E-09 |
| Interaction capability / operability (3.4.3) | 360 px'te yatay taşma (sayfa + iç kapsayıcı) | 0 | - | 0 (giriş ve panel) | Hedefi karşılıyor | TC-E2E-07 |
| Flexibility / installability | Temiz ortam kurulumunun başarısı | Linux ve Windows, Python 3.12 ve 3.13 | Linux BAŞARILI; CI 4/4 (02.11.2026) | Linux 3.12.13 ve 3.13.18 BAŞARILI; GitHub Actions'ta Ubuntu ve Windows × 3.12/3.13 BAŞARILI (02.11.2026); Windows'ta elle kurulum NOT RUN | Hedefi karşılıyor | TC-INST-01, TC-CI-01 |
| Performance efficiency / time behaviour (3.2.1) | Talep listesi p95 yanıt süresi | < 500 ms | - | **ÖLÇÜLMEDİ** (özellik Hafta 3'te, ölçüm Hafta 11-12'de) | - | NFR-13 |
| Reliability | Hata/arıza oranı | Tanımlanacak | - | **ÖLÇÜLMEDİ** | - | - |

Karmaşıklık ölçüm komutu: `ruff check . --select C901 --config "lint.mccabe.max-complexity = 0" --output-format json`.

## 2. Boyut bilgisi (bağlam için)

| Öğe | Hafta 1 | Hafta 2 |
|---|---|---|
| Uygulama kodu (`config/`, `servicedesk/`; testler ve migration hariç; boş ve yorum satırı hariç, belge dizeleri dahil) | 325 satır | 649 satır |
| Test kodu | 236 satır | 601 satır |
| Araç kodu (`tools/*.py`, `e2e/*.py`) | 549 satır | 981 satır |
| Şablonlar (boş olmayan satır) | 0 | 329 satır (13 dosya) |
| `app.css` (boş olmayan satır) | - | 283 satır |
| Sabitlenmiş çalışma zamanı bağımlılığı | 4 | 4 (Django, asgiref, sqlparse, tzdata yalnız Windows) |
| Django test süresi (test başına sürelerin toplamı) | 1,69 sn (8 test) | 10,94 sn (35 test; en uzun TC-SEED-01, 4,59 sn) |
