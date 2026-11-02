# Kod rehberi: Hafta 1 kodu nasıl çalışır?

Bu belge, Hafta 1 kodunun nasıl çalıştığını sunum ve vize hazırlığı için özetler. Her bölümde önce ne olduğu, sonra nerede olduğu, en sonda neden böyle yapıldığı anlatılır.

## 1. Hafta 1'de ne var?

Hafta 1 bir "altyapı haftası"dır: kullanıcıya görünen bir ekran yoktur. Kurulan şeyler sonraki haftaların üzerine oturacağı temeldir.

| Parça | Dosya | Ne işe yarar? |
|---|---|---|
| Django projesi | `config/` | Ayarlar, URL'ler, WSGI/ASGI giriş noktaları |
| Uygulama | `servicedesk/` | Tek uygulama; Hafta 1'de yalnız özel kullanıcı modeli ve yönetim sitesi kaydı |
| Test koşucusu | `config/test_runner.py` | Test sonuçlarını TC kimlikleriyle JSON'a yazar |
| RTM üretici | `tools/build_rtm.py` | Gereksinim → test → gerçek sonuç tablosunu üretir |
| Rapor üretici | `tools/build_report.py` | Ders rapor şablonunu JSON içerikten doldurur |
| Kurulum denetimi | `tools/install_check.sh` | Temiz kopyada temiz kurulum ve CI adımları (TC-INST-01) |
| CI | `.github/workflows/ci.yml` | Ubuntu/Windows × Python 3.12/3.13 matrisi (henüz koşmadı) |

## 2. Neden baştan özel kullanıcı modeli?

`servicedesk/models.py` içindeki `User`, Django'nun hazır `AbstractUser` sınıfını hiçbir alan eklemeden genişletir. `config/settings.py` içinde `AUTH_USER_MODEL = "servicedesk.User"` yazılıdır.

**Neden?** Django belgeleri yeni projelerde baştan özel kullanıcı modeli tanımlanmasını önerir; ilk `migrate`'ten sonra geçiş çok zordur. Bugün alan eklemiyoruz, ama ileride (ör. departman) gerekirse kolayca ekleyebiliriz. Kişisel veri asgarisi (NFR-12) gereği yalnız kullanıcı adı, ad, soyad ve e-posta tutulur. TC-CFG-06, yönetim sitesinin bu modelle açıldığını doğrular.

## 3. Ayarlar ve güvenlik profili

`config/settings.py` iki profil tanır:

- **development** (varsayılan): DEBUG açık, yerel anahtar.
- **production** (`DJANGO_ENV=production`): SECRET_KEY ve ALLOWED_HOSTS yoksa uygulama **başlamaz**. DEBUG açılmaya çalışılırsa yine başlamaz. Güvenli çerezler ve HTTPS yönlendirmesi açılır.

Ortam değişkenleri `env_bool`, `env_int`, `env_list` fonksiyonlarıyla katı okunur: "belki" gibi geçersiz bir değer sessizce yanlış yorumlanmaz, yapılandırma hatası verir (TC-CFG-05).

Üretim profili TC-CFG-02 ve TC-CFG-03'te ayrı bir Python sürecinde denenir. TC-CFG-03, Django'nun güvenlik denetimini (`check --deploy`) uyarı düzeyinde çalıştırır. Tek susturma (security.W021, HSTS preload) gerekçesiyle ayarlarda yazılıdır; susturmasız koşu kanıt olarak saklandı (RSK-04).

**Zaman:** `USE_TZ=True` veritabanına UTC yazar; `TIME_ZONE="Europe/Istanbul"` gösterimi İstanbul saatine çevirir. TC-CFG-01, 09:30 UTC'nin ekranda 12:30 göründüğünü doğrular. SLA hesapları (Hafta 7) bu temel üzerine kurulacak.

**Parolalar:** Django'nun varsayılan PBKDF2-SHA256 özetlemesi ve en az 10 karakterlik parola kuralları (TC-SEC-01).

## 4. Testler ve "gerçek sonuç"

- Her test metodunun belge dizesi bir TC kimliğiyle başlar: `"""TC-CFG-01: ..."""`.
- `config/test_runner.py`, Django'nun test koşucusunu genişletir. `--results-json` verilince her testin sonucunu TC kimliğiyle JSON'a yazar.
- `tools/build_rtm.py` bu JSON'u, gereksinim tablosunu (`docs/traceability/requirements.csv`) ve test kataloğunu birleştirerek `docs/RTM.md` dosyasını üretir. Sonuç sütununu kimse elle yazmaz; koşulmayan test NOT RUN, sonraki haftaya ait olan PLANLANDI görünür (`--week 1`).
- Test araçlarının kendisi de test edilir: TC-QA-03 koşucunun PASS/FAIL/ERROR/SKIP kaydını, TC-QA-04 RTM üreticinin durum hesabını doğrular. TC-QA-04, Hafta 1'de bulunan bir hatadan doğdu: özet tablosu "NOT RUN" durumunu "NOT" diye sayıyordu (RSK-06).

## 5. Vize sorularına malzeme (Hafta 1'den)

| Soru | Kullanılabilecek somut örnek | Kaynak |
|---|---|---|
| S1 (12207, uyarlama) | 6.4.9 Verification süreci; Acquisition/Supply kapsam dışı; tek kişilik ekip nedeniyle 6.3.8'in hafifletilmesi | STANDARDS.md §4 |
| S2 (29148, RTM) | NFR-04 ve NFR-05'in kabul kriterleri ve RTM satırları | SRS §5, §7; RTM.md |
| S4 (25010) | Security / resistance (`check --deploy`), Maintainability / testability (kapsam %87,39) | QUALITY_METRICS.md |
| S5 (IEEE 1012) | RSK-06: test aracındaki sayım hatası; gerileme testi ve hatalı kodla FAIL kanıtı | RISKS.md |

## 6. Sık sorulabilecek sorular

- **"Hafta 1'de neden ekran yok?"** Bu hafta gereksinimler, standartlar ve kurulum altyapısı kuruldu. Giriş/çıkış ve roller Hafta 2'de bu altyapının üstüne eklenir.
- **"Testlerin geçtiğini nasıl kanıtlıyorsunuz?"** RTM'nin sonuç sütunu test çıktısından otomatik üretiliyor; JSON ve günlükler `docs/evidence/hafta-01` altında.
- **"CI'da ne denetleniyor?"** Her push'ta Ubuntu ve Windows üzerinde, Python 3.12 ve 3.13 ile kurulum, biçim ve statik analiz, Django testleri (kapsamla), üretim güvenlik denetimi ve RTM üretimi koşar. İlk koşu (02.11.2026) dört işin dördünde başarılı oldu (TC-CI-01).
