# Kod rehberi: Hafta 1-2 kodu nasıl çalışır?

Bu belge, Hafta 1 ve Hafta 2 kodunun nasıl çalıştığını sunum ve vize hazırlığı için özetler. Her bölümde önce ne olduğu, sonra nerede olduğu, en sonda neden böyle yapıldığı anlatılır.

## 1. Bir isteğin yolculuğu

Talep Sahibi tarayıcıya `/yonetim/` yazdığında şunlar olur:

1. **Middleware zinciri** (`config/settings.py` → `MIDDLEWARE`): `SessionMiddleware` çerezden oturumu bulur. `AuthenticationMiddleware` `request.user` nesnesini hazırlar. `CsrfViewMiddleware` POST isteklerinde belirteci denetler.
2. **URL eşleme** (`config/urls.py` → `servicedesk/urls.py`): `/yonetim/` adresi `ManagerPanelView` görünümüne gider.
3. **Yetki denetimi** (`servicedesk/views.py`): `ManagerPanelView`, Django'nun hazır `PermissionRequiredMixin` sınıfını kullanır. `dispatch()` görünüm kodu çalışmadan önce `user.has_perm("servicedesk.access_manager_panel")` sorar.
   - Oturum yoksa kullanıcı giriş sayfasına yönlendirilir (`?next=/yonetim/`).
   - Oturum var ama izin yoksa `PermissionDenied` fırlatılır ve Django `templates/403.html` sayfasını 403 koduyla döndürür.
4. **Şablon**: İzin varsa `manager_panel.html`, `base.html` iskeletine yerleşir. `role_context` bağlam işlemcisi rol adını her sayfaya ekler.

**Anlatırken vurgulayın:** Menüdeki bağlantıyı gizlemek güvenlik değildir. Denetim 3. adımda sunucuda yapılır, GET ve POST için aynıdır. Kanıt: TC-ROLE-07..10 ve TC-E2E-03.

## 2. Roller nasıl tanımlandı?

`servicedesk/roles.py` dosyası üç şey içerir:

- **Rol tanımları:** `REQUESTER`, `AGENT`, `MANAGER`. Her rolün bir Django grubu (`group_name`) ve önceliği vardır.
- **Rol-izin matrisi:** `ROLE_PERMISSIONS`. Hangi grubun hangi izni taşıdığını kod içinde tek yerde tanımlar.
- **Senkronizasyon:** `sync_role_groups()`. Grupları oluşturur ve izinlerini matrisle birebir eşitler.

`servicedesk/apps.py` içindeki `ready()` metodu bu fonksiyonu Django'nun `post_migrate` sinyaline bağlar. Böylece her `python manage.py migrate` sonunda gruplar otomatik kurulur.

**Neden sinyal?** Django, uygulama izinlerini (`access_manager_panel` gibi) `migrate`'in sonunda oluşturur. Normal bir veri migration'ı bu izinler henüz yokken çalışabilir. `post_migrate` ise izinler oluştuktan sonra tetiklenir. Ayrıca işlem tekrarlanabilir: ikinci çalıştırmada hiçbir şey değişmez. Biri yönetim sitesinden gruba fazladan izin eklerse bir sonraki `migrate` bunu geri alır. Kanıt: TC-ROLE-01..03.

**Neden rol = grup, yetki = izin?** Görünümler grup adına değil izne bakar. Grubun adı değişse bile yetki kırılmaz. Yeni rol eklemek için yalnız matrise satır eklenir. Superuser bütün izinlere sahip olduğu için ayrıca kod gerekmez.

## 3. Giriş ve çıkış

- Giriş, Django'nun `LoginView` sınıfıdır (`config/urls.py`). Kendi yazdığımız tek parça `LoginForm`'dur (`servicedesk/forms.py`). Bu form yalnız Bootstrap sınıfı ve erişilebilirlik özniteliği ekler; parola kontrolünü Django yapar.
- Hatalı parola, olmayan kullanıcı ve pasif hesap için aynı mesaj gösterilir. Böylece saldırgan hangi kullanıcı adlarının var olduğunu öğrenemez (FR-02, TC-AUTH-04/05).
- `next` parametresi dış siteye işaret ediyorsa yok sayılır (açık yönlendirme koruması, TC-AUTH-09).
- Çıkış yalnız POST ile yapılır; menüdeki "Çıkış yap" düğmesi CSRF belirteçli bir formdur. GET ile çıkış 405 döner (TC-AUTH-07). Böylece başka bir site, kullanıcıyı gizli bir bağlantıyla oturumundan çıkaramaz.

## 4. Ayarlar ve güvenlik profili

`config/settings.py` iki profil tanır:

- **development** (varsayılan): DEBUG açık, yerel anahtar.
- **production** (`DJANGO_ENV=production`): SECRET_KEY ve ALLOWED_HOSTS yoksa uygulama **başlamaz**. DEBUG açılmaya çalışılırsa yine başlamaz. Güvenli çerezler ve HTTPS yönlendirmesi açılır.

Bu davranış TC-CFG-02 ve TC-CFG-03'te ayrı bir Python sürecinde denenir. TC-CFG-03, Django'nun güvenlik denetimini (`check --deploy`) uyarı düzeyinde çalıştırır.

**Zaman:** `USE_TZ=True` veritabanına UTC yazar; `TIME_ZONE="Europe/Istanbul"` gösterimi İstanbul saatine çevirir. TC-CFG-01, 09:30 UTC'nin ekranda 12:30 göründüğünü doğrular. SLA hesapları (Hafta 7) bu temel üzerine kurulacak.

## 5. Testler ve "gerçek sonuç"

- Her test metodunun belge dizesi bir TC kimliğiyle başlar: `"""TC-ROLE-08: ..."""`.
- `config/test_runner.py`, Django'nun test koşucusunu genişletir. `--results-json` verilince her testin sonucunu TC kimliğiyle JSON'a yazar.
- `tools/build_rtm.py` bu JSON'u, gereksinim tablosunu (`docs/traceability/requirements.csv`) ve test kataloğunu birleştirerek `docs/RTM.md` dosyasını üretir. Sonuç sütununu kimse elle yazmaz; koşulmayan test NOT RUN görünür.
- Test araçlarının kendisi de test edilir: TC-QA-03 koşucuyu, TC-QA-04 RTM üreticinin durum hesabını ve sayımını doğrular (Hafta 1'de bulunan "NOT RUN" sayım hatası, RSK-06).
- Testlerin işe yaradığı **mutasyon denetimiyle** gösterildi: `tools/mutation_check.py` kodun kopyasına bilinçli 4 hata ekledi, 35 testlik takım 4'ünü de yakaladı (`docs/evidence/hafta-02/mutation-check.md`).
- Tarayıcı testleri (`e2e/week2_auth_roles.py`) Django testlerinin tamamlayıcısıdır: gerçek Chromium'da giriş yapar, adres çubuğuna kısıtlı sayfayı yazar, mobil genişliği ve klavye kullanımını dener.

## 6. Arayüz

- Django Templates + Bootstrap 5.3.8 (yerel dosya, internetsiz demo çalışır).
- `static/css/app.css` yalnız Bootstrap değişkenlerini ve birkaç bileşeni özelleştirir. Durum renkleri (Açık, İşlemde, Çözüldü, Kapandı) yalnız talep durumunu anlatmak için kullanılır.
- Giriş sayfasındaki "Bir talep nasıl ilerler?" paneli, Hafta 5'te kurulacak durum makinesini kullanıcıya baştan gösterir.
- Panelin yetki tablosundaki "Hafta N" etiketleri `roles.py` içindeki `Capability.week` değerinden gelir; `CURRENT_WEEK = 2`.

## 7. Vize sorularına malzeme (Hafta 1-2'den)

| Soru | Kullanılabilecek somut örnek | Kaynak |
|---|---|---|
| S1 (12207, uyarlama) | 6.4.9 Verification ve 6.4.11 Validation süreçleri; Acquisition/Supply kapsam dışı | STANDARDS.md §4 |
| S2 (29148, RTM) | MOD-ROLE için FR-06, FR-09 ve NFR-03, NFR-04; RTM satırları | SRS §5, RTM.md |
| S3 (IEEE 1016) | Bağlam ve bileşim görünümleri; paydaş kaygıları tablosu | SDD §1, §3, §4 |
| S4 (25010) | Security (3.6.1, 3.6.6), Maintainability (kapsam %92,08), Interaction capability (kontrast ≥ 4.5:1) | QUALITY_METRICS.md |
| S5 (IEEE 1012) | RSK-19 (görsel inceleme ile bulunan mobil kusur), RSK-20 (eski sunucuyla koşan test), RSK-06 (test aracındaki sayım hatası) | RISKS.md |

## 8. Sık sorulabilecek sorular

- **"Rol kontrolünü neden şablonda yapmadınız?"** Şablondaki koşul yalnız görünümü değiştirir. Adresi bilen kullanıcı şablonu atlar. Denetim sunucudaki görünümdedir.
- **"Neden 403, bazen de 404?"** Sayfa role kapalıysa 403 ile açıklarız. Hafta 3'te başkasının talebine erişimde 404 döneceğiz; böylece kaydın var olup olmadığı sızmaz.
- **"Testlerin geçtiğini nasıl kanıtlıyorsunuz?"** RTM'nin sonuç sütunu test çıktısından otomatik üretiliyor; JSON ve günlükler her haftanın `docs/evidence/hafta-NN` klasöründe.
- **"Neden özel kullanıcı modeli?"** Django belgeleri yeni projede baştan önerir; ileride alan eklemek (ör. departman) kolay olur, sonradan geçiş zordur.
