# Kalite ölçümleri (ISO/IEC 25010:2023 ile ilişkili)

| Alan | Değer |
|---|---|
| Doküman kimliği | SDS07-QM |
| Ölçüm tarihi | 30.10.2026 (Hafta 1 paketi) |
| Ortam | Linux, Python 3.13.18, Django 5.2.18 |

Kural: Ölçülmeyen değer "ÖLÇÜLMEDİ" yazılır. Değerler araç çıktılarından alınmıştır; kaynak sütununda belirtilmiştir. Kanıt klasörü: `docs/evidence/hafta-01/`.

## 1. Hafta 1 ölçümleri

| Karakteristik / alt karakteristik | Metrik | Hedef eşik | Ölçülen | Durum | Kaynak |
|---|---|---|---|---|---|
| Maintainability / testability | Üretim kodu satır+dal kapsamı (testler ve migration hariç) | ≥ %80 | %87,39 (173/192 satır, 21/30 dal) | Hedefi karşılıyor | `coverage.json` (`-v 2` koşusu) |
| Maintainability / analysability | ruff bulgu sayısı | 0 | 0 | Hedefi karşılıyor | `ruff.json` |
| Maintainability / modularity (3.7.1) | Uygulama fonksiyonlarının döngüsel karmaşıklığı | Fonksiyon başına ≤ 10 | Ortalama 1,41, medyan 1, en yüksek 4 (22 fonksiyon) | Hedefi karşılıyor | ruff C901 ölçümü |
| Maintainability (araçlar) | `tools/` döngüsel karmaşıklığı | ≤ 10 | Ortalama 3,93, en yüksek 19 (`build_report.build`; 28 fonksiyon) | **Hedefi aşıyor** (RSK-07) | ruff C901 ölçümü |
| Functional suitability / functional correctness (3.1.2) | Hafta 1 otomatik test geçme oranı | %100 | %100 (8/8 Django testi) | Hedefi karşılıyor | `unit-results.json` |
| Security / resistance (3.6.6) | `check --deploy` uyarı sayısı (üretim profili) | 0 (gerekçeli susturma hariç) | 0; 1 gerekçeli susturma (security.W021) | Hedefi karşılıyor | `check-deploy.txt`, `check-deploy-susturmasiz.txt` |
| Security / confidentiality (3.6.1) | Parola özet algoritması | PBKDF2-SHA256 veya daha güçlü | PBKDF2-SHA256 | Hedefi karşılıyor | TC-SEC-01 |
| Flexibility / installability | Temiz ortam kurulumunun başarısı | Linux ve Windows, Python 3.12 ve 3.13 | Linux 3.12.13 ve 3.13.18 BAŞARILI; Windows **NOT RUN** | Kısmi | TC-INST-01, TC-CI-01 |
| Interaction capability (3.4) | Mobil düzen, klavye, kontrast | - | **ÖLÇÜLMEDİ** (arayüz Hafta 2'de) | - | NFR-07, NFR-08 |
| Performance efficiency / time behaviour (3.2.1) | Talep listesi p95 yanıt süresi | < 500 ms | **ÖLÇÜLMEDİ** (özellik Hafta 3'te, ölçüm Hafta 11-12'de) | - | NFR-13 |
| Reliability | Hata/arıza oranı | Tanımlanacak | **ÖLÇÜLMEDİ** | - | - |

Karmaşıklık ölçüm komutu: `ruff check . --select C901 --config "lint.mccabe.max-complexity = 0" --output-format json` (her fonksiyonun değeri iletiden okunur).

## 2. Boyut bilgisi (bağlam için)

| Öğe | Değer |
|---|---|
| Uygulama kodu (`config/`, `servicedesk/`; testler ve migration hariç; boş ve yorum satırı hariç, belge dizeleri dahil) | 325 satır |
| Test kodu | 236 satır |
| Araç kodu (`tools/*.py`) | 549 satır |
| Şablon | 0 (Django yönetim sitesinin hazır şablonları kullanılıyor) |
| Sabitlenmiş çalışma zamanı bağımlılığı | 4 (Django, asgiref, sqlparse, tzdata yalnız Windows) |
| Django test süresi | 1,69 sn (8 test; en uzun TC-CFG-02, 0,59 sn) |
