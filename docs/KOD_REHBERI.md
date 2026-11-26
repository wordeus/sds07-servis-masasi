# Kod rehberi: Hafta 1-4 kodu nasıl çalışır?

Bu belge, Hafta 1-4 kodunun nasıl çalıştığını sunum ve vize hazırlığı için özetler. Her bölümde önce ne olduğu, sonra nerede olduğu, en sonda neden böyle yapıldığı anlatılır.

## 1. Bir isteğin yolculuğu

Talep Sahibi tarayıcıya `/yonetim/` yazdığında şunlar olur:

1. **Middleware zinciri** (`config/settings.py` → `MIDDLEWARE`): `SessionMiddleware` çerezden oturumu bulur. `AuthenticationMiddleware` `request.user` nesnesini hazırlar. `CsrfViewMiddleware` POST isteklerinde belirteci denetler.
2. **URL eşleme** (`config/urls.py` → `servicedesk/urls.py`): `/yonetim/` adresi `ManagerPanelView` görünümüne gider.
3. **Yetki denetimi** (`servicedesk/views/dashboard.py`): `ManagerPanelView`, Django'nun hazır `PermissionRequiredMixin` sınıfını kullanır. `dispatch()` görünüm kodu çalışmadan önce `user.has_perm("servicedesk.access_manager_panel")` sorar.
   - Oturum yoksa kullanıcı giriş sayfasına yönlendirilir (`?next=/yonetim/`).
   - Oturum var ama izin yoksa `PermissionDenied` fırlatılır ve Django `templates/403.html` sayfasını 403 koduyla döndürür.
4. **Şablon**: İzin varsa `manager_panel.html`, `base.html` iskeletine yerleşir. `role_context` bağlam işlemcisi rol adını her sayfaya ekler.

**Anlatırken vurgulayın:** Menüdeki bağlantıyı gizlemek güvenlik değildir. Denetim 3. adımda sunucuda yapılır, GET ve POST için aynıdır. Kanıt: TC-ROLE-07..10 ve TC-E2E-03.

## 1a. Hafta 3: başkasının talebini açmaya çalışınca ne olur?

Talep Sahibi Ayşe, adres çubuğuna başkasına ait `/talepler/42/` adresini yazar:

1. **Rol düzeyi (403 kapısı):** `TicketDetailView`, `PermissionRequiredMixin` ile `servicedesk.view_ticket` iznini sorar. Ayşe'nin rolünde bu izin var; kapıdan geçer.
2. **Kayıt düzeyi (404 kapısı):** Görünüm kaydı doğrudan `Ticket.objects.get(...)` ile aramaz. `get_queryset()` yalnız `visible_tickets_for(ayse)` döndürür (`servicedesk/services/tickets.py`). Bu fonksiyon, `view_all_tickets` izni olmayan kullanıcı için sorguya `requester=ayse` koşulunu ekler.
3. Talep 42 bu kümede olmadığı için Django `DetailView` 404 döndürür. Yanıt, hiç var olmayan bir numarayla aynıdır; Ayşe kaydın var olup olmadığını öğrenemez.

**Anlatırken vurgulayın:** Kural tek fonksiyonda olduğu için liste, ayrıntı, destek kuyruğu ve panel özeti aynı kuralı kullanır. Kanıt: TC-TKT-04, TC-TKT-07, TC-E2E-11; kuralı kaldıran mutasyon (M5) ve görünümde politikayı atlayan mutasyon (M6) testlerce yakalandı. Diyagram: SDD §8.2.

## 1b. Hafta 3: katmanlar ve mimari testi

```
views/     HTTP isteği, yetki kapısı, form, mesaj      (dashboard.py, tickets.py, categories.py)
   ↓
services/  iş kuralları: görünürlük, oluşturma, filtre, kategoriler   (tickets.py)
   ↓
models/    veri: User, Category, Ticket               (user.py, ticket.py)
```

- Görünümler `.objects` ile modele doğrudan sorgu yazmaz; servis fonksiyonunu çağırır.
- Servisler görünüme, şablona veya HTTP katmanına bağlı değildir; bu yüzden testte tek başına çağrılabilir.
- Bu kural yalnız belgede değildir: `servicedesk/tests/test_architecture.py` kaynak kodu Python'un `ast` modülüyle okur ve ihlal varsa testi düşürür (TC-ARCH-01). TC-ARCH-02 her görünüm sınıfında oturum veya izin denetimi olduğunu denetler.
- Talep numarası (`INC-000123`) veritabanının birincil anahtarından türetilir; ayrı sayaç olmadığı için iki kullanıcı aynı anda talep açsa da numara çakışmaz (KRR-12).
- Durum alanı formda yoktur (`editable=False`); kötü niyetli biri POST isteğine `status=CLOSED` eklese bile talep Açık başlar (TC-TKT-02).

## 1c. Hafta 3'te bulunan bir hata: Türkçe büyük harf

Kategori adlarının tekilliği önce veritabanının `iexact` karşılaştırmasıyla denetleniyordu. SQLite bu karşılaştırmayı yalnız İngilizce harflerde yapar: "donanım" kopya sayılıyordu ama "DONANIM" sayılmıyordu. Çözüm `servicedesk/text.py::turkish_key`: önce "I"yı "ı"ya, "İ"yi "i"ye çevirir, sonra küçük harfe dönüştürür. Kural `Category.clean()` içinde olduğu için yönetim sitesi de aynı kuralı uygular (RSK-21, TC-CAT-01).

## 1d. Teslim öncesi bulunan iki yapılandırma hatası

**Depoya girmeyecek dosyalar (RSK-24).** `.gitignore` dosyasındaki `reports/` satırı yalnız kökteki test çıktısı klasörünü değil, her düzeydeki `reports` klasörünü kapsıyordu. Bu yüzden `docs/reports/` altındaki raporlar depoya girmeyecekti. Satır `/reports/` yapıldı; baştaki `/` kalıbı depo köküne bağlar. Benzer şekilde `*.log` kanıt günlüklerini de dışlıyordu; `!docs/evidence/**/*.log` istisnası eklendi. Denetim yöntemi: paketi boş bir depoya kopyalayıp `git status --ignored` çıktısına bakmak.

**Windows'ta Türkçe karakter hatası (RSK-25).** Python, çıktı bir konsola değil dosyaya veya başka bir programa gidiyorsa (CI günlüğü gibi) Windows'ta varsayılan olarak cp1252 kod sayfasını kullanır. Bu kod sayfasında "ş" ve "ı" yoktur; `print("RTM yazıldı")` gibi bir satır `UnicodeEncodeError` ile programı durdurur. Linux'ta `PYTHONIOENCODING=cp1252` ile bu durum taklit edildi ve hata gerçekten görüldü. Çözüm, Python'un UTF-8 kipidir (`PYTHONUTF8=1`); CI iş akışında tanımlıdır. Etkileşimli PowerShell penceresinde sorun yoktur, çünkü Python konsola her zaman UTF-8 yazar.

## 1e. Hafta 4: yorum, üzerine alma, atama ve işlem geçmişi

**Ne?** Talep sayfasında yorum yazılır; Destek Personeli atanmamış talebi "Üzerime al" düğmesiyle alır; Yönetici talebi bir Destek Personeline atar; personel ve yönetici önceliği değiştirebilir. Bu işlemlerin her biri işlem geçmişine kaydedilir: kim, ne zaman (UTC), eski değer, yeni değer.

**Nerede?**
- Kurallar: `services/assignment.py` (üzerine alma, atama, öncelik), `services/comments.py` (yorum), `services/audit.py` (işlem geçmişine yazan tek fonksiyon `record_event`).
- Adresler: `views/ticket_actions.py`. Dört görünüm de yalnız POST kabul eder. Talep her zaman `visible_tickets_for` kümesinden alınır; bu yüzden talep sahibi başkasının talebinin yorum adresine istek gönderirse ayrıntı sayfasındaki gibi 404 alır (FR-14).
- Veri: `models/activity.py` (`Comment`, `TicketEvent`), migration 0005 ve 0006.

**Neden böyle?**
- İzin iki yerde denetlenir: görünümde `PermissionRequiredMixin` (403) ve servis fonksiyonunun içinde (`PermissionDenied`). Böylece ileride servisi başka bir yerden çağıran kod kuralı atlayamaz (TC-ASN-03).
- İşlem ve geçmiş kaydı aynı veritabanı işleminde (`transaction.atomic`) yazılır: biri olmazsa öteki de olmaz.
- Geçmiş kaydı yalnız eklenir: `TicketEvent.save()` ikinci kez çağrılırsa ve `delete()` her zaman hata verir; yönetim sitesinde kayıtlar salt okunurdur (KRR-16, TC-AUD-02).
- İki personel aynı anda "Üzerime al" derse ilk gelen alır: servis talebi kilitleyerek yeniden okur ve atanmış mı diye bakar.

**Hafta 4'te testlerin yakaladığı üç hata (RSK-28..RSK-30):** Kapanmış talepte işlem isteği sunucu hatası (500) veriyordu; kapanmış talebe yorum reddinin sebebi ekranda görünmüyordu; yeni görünümlerde izin denetimi açıkça yazılmamıştı. Üçünü de ilk test koşusu gösterdi, düzeltmeden sonra aynı testler geçti.

**Kapsam kararı (KRR-18):** Proje Faz 5'te biter. Değişiklik yönetimi, SLA, anket, KPI ve DÖF gelecek çalışmadır; RTM'de "KAPSAM DIŞI" görünür, panelde "Kapsam dışı" yazar.

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
- Testlerin işe yaradığı **mutasyon denetimiyle** gösterildi: `tools/mutation_check.py` kodun kopyasına bilinçli hatalar ekler. Hafta 2'de 4/4, Hafta 3'te 8/8 hata yakalandı (`docs/evidence/hafta-03/mutation-check.md`).
- Tarayıcı testleri (`e2e/week2_auth_roles.py`, Hafta 3'te `e2e/week3_tickets.py`) Django testlerinin tamamlayıcısıdır: gerçek Chromium'da giriş yapar, adres çubuğuna kısıtlı sayfayı yazar, mobil genişliği ve klavye kullanımını dener.

## 6. Arayüz

- Django Templates + Bootstrap 5.3.8 (yerel dosya, internetsiz demo çalışır).
- `static/css/app.css` yalnız Bootstrap değişkenlerini ve birkaç bileşeni özelleştirir. Durum renkleri (Açık, İşlemde, Çözüldü, Kapandı) yalnız talep durumunu anlatmak için kullanılır.
- Giriş sayfasındaki "Bir talep nasıl ilerler?" paneli, Hafta 5'te kurulacak durum makinesini kullanıcıya baştan gösterir.
- Panelin yetki tablosundaki "Hafta N" etiketleri `roles.py` içindeki `Capability.week` değerinden gelir; `CURRENT_WEEK = 3`.
- Talep ayrıntısındaki dört adımlı şerit, giriş sayfasındaki süreç panelinin talebe uygulanmış hâlidir; şu anki adım durum rengiyle gösterilir.

## 7. Vize sorularına malzeme (Hafta 1-3'ten)

| Soru | Kullanılabilecek somut örnek | Kaynak |
|---|---|---|
| S1 (12207, uyarlama) | 6.4.9 Verification ve 6.4.11 Validation süreçleri; Acquisition/Supply kapsam dışı | STANDARDS.md §4 |
| S2 (29148, RTM) | MOD-ROLE için FR-06, FR-09; MOD-TICKET için FR-14 (kabul kriteri → TC-TKT-07 → PASS); RTM satırları | SRS §5, §7.1, RTM.md |
| S3 (IEEE 1016) | Bağlam ve bileşim görünümleri; katmanlı yapı; kayıt düzeyi erişim etkileşimi; paydaş kaygıları tablosu | SDD §1, §3, §4, §8.2 |
| S4 (25010) | Security / confidentiality (başkasının talebinde 404), Maintainability / modularity (katman kuralı, TC-ARCH), kapsam %94,21, Interaction capability (kontrast ≥ 4.5:1) | QUALITY_METRICS.md |
| S5 (IEEE 1012) | RSK-21 (Türkçe harf hatası, test genişletilerek bulundu), RSK-23 (E2E'nin DEBUG sayfasını görmesi), RSK-19 (mobil kusur), RSK-06 (test aracındaki sayım hatası), RSK-25 (Windows kodlama hatası, ortam simülasyonuyla bulundu) | RISKS.md |

## 8. Sık sorulabilecek sorular

- **"Rol kontrolünü neden şablonda yapmadınız?"** Şablondaki koşul yalnız görünümü değiştirir. Adresi bilen kullanıcı şablonu atlar. Denetim sunucudaki görünümdedir.
- **"Neden 403, bazen de 404?"** Sayfa role kapalıysa 403 ile açıklarız. Başkasının talebine erişimde 404 döneriz (Hafta 3'te uygulandı); böylece kaydın var olup olmadığı sızmaz.
- **"Talep sahibi önceliği neden kendisi seçiyor?"** FR-12 böyle tanımlandı; geçici karardır (AK-03, KRR-13). Hafta 4'te destek personeli değiştirebilecek ve değişiklik işlem geçmişine yazılacak.
- **"Testlerin geçtiğini nasıl kanıtlıyorsunuz?"** RTM'nin sonuç sütunu test çıktısından otomatik üretiliyor; JSON ve günlükler her haftanın `docs/evidence/hafta-NN` klasöründe.
- **"Neden özel kullanıcı modeli?"** Django belgeleri yeni projede baştan önerir; ileride alan eklemek (ör. departman) kolay olur, sonradan geçiş zordur.
