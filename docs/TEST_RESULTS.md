# Doğrulama ve Geçerleme Test Sonuçları

> Bu dosya `tools/build_rtm.py` tarafından üretilir. Sonuçlar yalnız gerçek çalıştırma kayıtlarından gelir.
> Üretim: 26.11.2026 03:29 (Europe/Istanbul) · Aktif hafta: 3

| Kaynak | Tür | Başlangıç (İstanbul) | Ortam | Özet |
|---|---|---|---|---|
| `docs/evidence/hafta-03/unit-results.json` | django-unit-integration | 30.10.2026 09:38 | python 3.13.18, django 5.2.18, platform Linux-6.18.44-fc-v185-x86_64-with-glibc2.39 | run=49, failures=0, errors=0, skipped=0, successful=True |
| `docs/evidence/hafta-03/e2e-results.json` | e2e-playwright | 30.10.2026 09:39 | browser chromium 153.0.8010.12, python 3.13.18, platform Linux-6.18.44-fc-v185-x86_64-with-glibc2.39 | run=9, failures=0, errors=0, successful=True |
| `docs/evidence/hafta-03/e2e-week3-results.json` | e2e-playwright | 30.10.2026 09:39 | browser chromium 153.0.8010.12, python 3.13.18, platform Linux-6.18.44-fc-v185-x86_64-with-glibc2.39 | run=4, failures=0, errors=0, successful=True |
| `docs/evidence/hafta-03/manual-checks.json` | manual-and-scripted-checks | 30.10.2026 09:43 | platform Linux (bulut çalışma alanı) | run=3, failures=0, not_run=1 |
| `docs/evidence/hafta-03/ci-github-actions-2026-11-21.json` | github-actions | 22.11.2026 00:08 | platform GitHub Actions: ubuntu-latest ve windows-latest, Python 3.12 ve 3.13 | run=1, failures=0, jobs_passed=4, jobs_total=4 |
| `docs/evidence/hafta-03/windows-2026-11-26/unit-results.json` | django-unit-integration | 26.11.2026 03:27 | python 3.13.17, django 5.2.18, platform Windows-11-10.0.26300-SP0 | run=49, failures=0, errors=0, skipped=0, successful=True |
| `docs/evidence/hafta-03/windows-2026-11-26/manual-checks.json` | manual-and-scripted-checks | 26.11.2026 03:27 | platform Windows 11 Pro 10.0.26300 (Burak Nigiz'in bilgisayarı) | run=1, failures=0, not_run=0 |
| ölçüm | coverage_percent | - | - | 94.21 |
| ölçüm | ruff_findings | - | - | 0 |

| Test ID | Doğrulanan gereksinim | Test seviyesi | Ön koşul ve test girdisi | Beklenen çıktı | Hafta | Sonuç | Kanıt |
|---|---|---|---|---|---|---|---|
| TC-AUTH-01 | FR-01 | Entegrasyon | Oturumsuz istemci; GET /hesap/giris/ | 200; login.html; username/password/csrf alanları var | 2 | **PASS** | unit-results.json |
| TC-AUTH-02 | FR-01 | Entegrasyon | Etkin Talep Sahibi; doğru parola ile POST | 302 → /; oturumda doğru kullanıcı kimliği | 2 | **PASS** | unit-results.json |
| TC-AUTH-03 | FR-01 | Entegrasyon | Oturumu açık kullanıcı; GET /hesap/giris/ | 302 → / | 2 | **PASS** | unit-results.json |
| TC-AUTH-04 | FR-02 | Entegrasyon | Yanlış parola ve bilinmeyen kullanıcı adı ile iki POST | 200; hata kodu invalid_login; iki yanıtta aynı mesaj; oturum yok; aria-invalid | 2 | **PASS** | unit-results.json |
| TC-AUTH-05 | FR-02 | Entegrasyon | Pasif hesap; doğru parola ile POST | 200; invalid_login; oturum yok | 2 | **PASS** | unit-results.json |
| TC-AUTH-06 | FR-03 | Entegrasyon | Oturumu açık kullanıcı; POST /hesap/cikis/ | 302 → giriş; oturum silinmiş; / isteği girişe yönlenir | 2 | **PASS** | unit-results.json |
| TC-AUTH-07 | FR-03 | Entegrasyon | Oturumu açık kullanıcı; GET /hesap/cikis/ | 405; oturum açık kalır | 2 | **PASS** | unit-results.json |
| TC-AUTH-08 | FR-04 | Entegrasyon | Oturumsuz istemci; /; /destek/; /yonetim/ için GET ve POST | 302 → /hesap/giris/?next=<adres> | 2 | **PASS** | unit-results.json |
| TC-AUTH-09 | FR-05 | Entegrasyon | Geçerli giriş POST; next=https://kotu.example/ ve //kotu.example/giris | 302 → / (dış adres yok sayılır) | 2 | **PASS** | unit-results.json |
| TC-AUTH-10 | FR-05 | Entegrasyon | Geçerli giriş POST; next=/destek/ | 302 → /destek/ | 2 | **PASS** | unit-results.json |
| TC-ROLE-01 | FR-06 | Entegrasyon | Boş test veritabanında migrate | Üç rol grubu mevcut | 2 | **PASS** | unit-results.json |
| TC-ROLE-02 | FR-06 | Entegrasyon | Migrate sonrası gruplar | Her grubun izinleri ROLE_PERMISSIONS ile birebir aynı | 2 | **PASS** | unit-results.json |
| TC-ROLE-03 | FR-06 | Entegrasyon | Senkronizasyon iki kez; ardından elle izin sapması | İkinci çalıştırmada değişiklik yok; sapma geri alınır (+1/-1) | 2 | **PASS** | unit-results.json |
| TC-ROLE-04 | FR-07 | Entegrasyon | Superuser yönetim sitesinde kullanıcıya Destek Personeli grubunu atar; Talep Sahibi /admin/ açar | Atama kaydedilir (302); rol Destek Personeli; Talep Sahibi admin girişine yönlenir | 2 | **PASS** | unit-results.json |
| TC-ROLE-05 | FR-08 | Birim | Çok gruplu; tek gruplu; grupsuz ve anonim kullanıcı | Yönetici > Destek Personeli > Talep Sahibi; grupsuz/anonim → rol yok | 2 | **PASS** | unit-results.json |
| TC-ROLE-06 | FR-08 | Entegrasyon | Her rol ve rolsüz kullanıcı ile GET / | Rol etiketi ve role açık yetkiler görünür; başka rolün yetkisi görünmez; rolsüzde uyarı | 2 | **PASS** | unit-results.json |
| TC-ROLE-07 | FR-09 | Entegrasyon | Talep Sahibi ve rolsüz kullanıcı; GET /destek/ ve /yonetim/ | 403 (panel 200) | 2 | **PASS** | unit-results.json |
| TC-ROLE-08 | FR-09 | Entegrasyon | Destek Personeli; GET /destek/ ve /yonetim/ | 200 ve 403 | 2 | **PASS** | unit-results.json |
| TC-ROLE-09 | FR-09 | Entegrasyon | Yönetici; GET /destek/ ve /yonetim/ | 200 ve 200 | 2 | **PASS** | unit-results.json |
| TC-ROLE-10 | FR-09 | Entegrasyon | Yetkisiz ve yetkili kullanıcılarla POST | Yetkisizde 403; yetkilide 405 (yetki yöntemden önce denetlenir) | 2 | **PASS** | unit-results.json |
| TC-ROLE-11 | FR-09 | Entegrasyon | Talep Sahibi; GET /yonetim/ | 403; 403.html; Türkçe başlık; rol ve adres yazılı; Traceback yok | 2 | **PASS** | unit-results.json |
| TC-ROLE-12 | FR-10 | Entegrasyon | Her rol; rolsüz ve superuser ile GET / | Menüde yalnız yetkili bölümlerin bağlantıları | 2 | **PASS** | unit-results.json |
| TC-ROLE-13 | FR-10 | Entegrasyon | Her rol, rolsüz ve superuser ile GET / | Talepler bağlantısı talep izni olanlarda; Kategoriler yalnız Yönetici ve superuser'da | 3 | **PASS** | unit-results.json |
| TC-SEED-01 | FR-11 | Entegrasyon | DEBUG açık; seed_demo_users iki kez | 3 demo kullanıcı; her biri tek doğru grupta; parola doğru; e-posta boş | 2 | **PASS** | unit-results.json |
| TC-SEED-02 | FR-11 | Entegrasyon | DEBUG kapalı; ardından DEBUG açık ve zayıf parola | İki durumda CommandError; kullanıcı oluşmaz | 2 | **PASS** | unit-results.json |
| TC-SEC-01 | NFR-01 | Birim | Kullanıcı oluşturma; zayıf parolalarla doğrulama | Özet pbkdf2_sha256$ ile başlar; düz parola yok; 3 zayıf parola reddedilir | 1 | **PASS** | unit-results.json |
| TC-SEC-02 | NFR-02 | Entegrasyon | enforce_csrf_checks=True istemci; belirteçsiz ve belirteçli POST | Belirteçsizde 403 (403_csrf.html); belirteçli çıkış 302 | 2 | **PASS** | unit-results.json |
| TC-SEC-03 | NFR-03 | Entegrasyon | Başarılı giriş yanıtı | sessionid çerezi HttpOnly; SameSite=Lax; max-age=28800 | 2 | **PASS** | unit-results.json |
| TC-CFG-01 | NFR-05 | Entegrasyon | date_joined = 2026-01-15 09:30 UTC | Veritabanında 09:30 (UTC); şablonda 15.01.2026 12:30 | 1 | **PASS** | unit-results.json |
| TC-CFG-02 | NFR-04 | Sistem (yapılandırma) | Üretim profili; eksik SECRET_KEY / ALLOWED_HOSTS ya da DEBUG=1 | Süreç hata koduyla durur; mesaj eksik değişkeni adlandırır | 1 | **PASS** | unit-results.json |
| TC-CFG-03 | NFR-03; NFR-04 | Sistem (yapılandırma) | Üretim profili; tam ortam değişkenleri | check --deploy --fail-level WARNING çıkış kodu 0; Secure çerezler ve SSL yönlendirme açık | 1 | **PASS** | unit-results.json |
| TC-CFG-04 | NFR-06 | Entegrasyon | GET /hesap/giris/ ve olmayan adres | lang=tr; Türkçe etiketler; Türkçe 404 sayfası | 2 | **PASS** | unit-results.json |
| TC-CFG-05 | NFR-04 | Birim | Geçerli; boş ve geçersiz ortam değişkeni değerleri | Doğru ayrıştırma; geçersiz değerde ImproperlyConfigured | 1 | **PASS** | unit-results.json |
| TC-CFG-06 | NFR-11 | Entegrasyon | Superuser; GET yönetim sitesi kullanıcı listesi ve ekleme formu | AUTH_USER_MODEL=servicedesk.User; iki sayfa 200; kullanıcı ve Rol grupları sütunu görünür | 1 | **PASS** | unit-results.json |
| TC-QA-01 | NFR-09 | Statik analiz | coverage run manage.py test; coverage json | Üretim kodu satır+dal kapsamı ≥ %80 | 1 | **PASS** | coverage.json (Kapsam %94.21 (eşik %80.0)) |
| TC-QA-02 | NFR-10 | Statik analiz | ruff check . --output-format json | 0 bulgu | 1 | **PASS** | ruff.json (0 bulgu) |
| TC-QA-03 | NFR-09 | Birim | Bilinçli PASS/FAIL/ERROR/SKIP/alt test örnekleri | Her sonuç TC kimliğiyle doğru kaydedilir; JSON özeti doğru | 1 | **PASS** | unit-results.json |
| TC-QA-04 | NFR-09 | Birim | Örnek test durumları ve gereksinim satırları (PASS/NOT RUN/FAIL/planlı/testsiz) | Gereksinim durumu ve özet sayıları doğru; FAIL baskın; 'NOT RUN' bölünmeden sayılır | 1 | **PASS** | unit-results.json |
| TC-INST-01 | NFR-11 | Kurulum | Temiz sanal ortam; pip install -r requirements.txt; migrate; test | Kurulum ve testler hatasız (her işletim sistemi ayrı kaydedilir) | 1 | **PASS** | manual-checks.json |
| TC-CI-01 | NFR-11 | CI | GitHub Actions matrisi: ubuntu/windows × Python 3.12/3.13 | Tüm işler yeşil | 1 | **PASS** | ci-github-actions-2026-11-21.json; manual-checks.json |
| TC-INS-01 | NFR-12 | İnceleme | User modeli; seed komutu ve şablonların incelenmesi | Yalnız kullanıcı adı/ad/soyad/e-posta; demo verisinde gerçek kişi yok | 1 | **PASS** | manual-checks.json |
| TC-E2E-01 | FR-01; NFR-06 | Sistem (E2E) | Chromium; GET /hesap/giris/ | Sayfa yüklenir; konsol hatası yok; Türkçe başlık | 2 | **PASS** | e2e-results.json (Plex Sans yüklendi=True) |
| TC-E2E-02 | FR-01; FR-08; FR-10 | Sistem (E2E) | demo.talep ile tarayıcıdan giriş | Panel; rol rozeti Talep Sahibi; Destek/Yönetim bağlantısı yok | 2 | **PASS** | e2e-results.json (menü bağlantıları: Panelim, tickets) |
| TC-E2E-03 | FR-09 | Sistem (E2E) | demo.talep oturumunda adres çubuğuna /yonetim/ ve /destek/ | 403 sayfası; rol bilgisi görünür | 2 | **PASS** | e2e-results.json (/yonetim/ → 403; /destek/ → 403) |
| TC-E2E-04 | FR-09 | Sistem (E2E) | demo.destek ile giriş; /destek/ ve /yonetim/ | Destek kuyruğu açılır; yönetim paneli 403 | 2 | **PASS** | e2e-results.json (/destek/ 200, /yonetim/ 403) |
| TC-E2E-05 | FR-09; FR-10 | Sistem (E2E) | demo.yonetici ile giriş | Menüde iki bağlantı; /destek/ ve /yonetim/ açılır | 2 | **PASS** | e2e-results.json (menüde iki bağlantı; iki sayfa 200) |
| TC-E2E-06 | FR-03 | Sistem (E2E) | Oturum açıkken Çıkış yap düğmesi | Giriş sayfası; / isteği girişe yönlenir | 2 | **PASS** | e2e-results.json (çıkış sonrası / → giriş) |
| TC-E2E-07 | NFR-07 | Sistem (E2E) | 360×740 görünüm alanı; giriş ve panel | scrollWidth ≤ clientWidth (yatay kaydırma yok) | 2 | **PASS** | e2e-results.json (giriş: sayfa 360/360 px, iç taşma yok; panel: sayfa 360/360 px, iç taşma yok) |
| TC-E2E-08 | NFR-08 | Sistem (E2E) | Yalnız klavye: Tab/Enter ile giriş; panelde Tab | Giriş tamamlanır; odaklanan öğede görünür odak çizgisi | 2 | **PASS** | e2e-results.json (ilk odak: İçeriğe geç; ikinci odak çizgisi: solid 3px) |
| TC-E2E-09 | NFR-08 | Sistem (E2E) | Hesaplanan renklerle kontrast ölçümü (WCAG formülü) | Gövde metni; ikincil metin ve birincil düğme ≥ 4.5:1 | 2 | **PASS** | e2e-results.json |
| TC-TKT-01 | FR-12 | Entegrasyon | Talep Sahibi; geçerli form ile POST /talepler/yeni/ | INC-000NNN numarası; durum OPEN; talep sahibi kendisi; UTC zaman; ayrıntıya yönlendirme; başarı mesajı | 3 | **PASS** | unit-results.json |
| TC-TKT-02 | FR-12; FR-15 | Entegrasyon | Kısa/uzun başlık, boş açıklama, pasif/olmayan kategori, geçersiz öncelik; forma eklenen status/requester/assignee | Form hatası ve aria-invalid; kayıt oluşmaz; eklenen alanlar yok sayılır | 3 | **PASS** | unit-results.json |
| TC-TKT-03 | FR-04; FR-09; FR-12 | Entegrasyon | Rolsüz kullanıcı ve oturumsuz istek; talep adreslerine GET/POST | Rolsüzde 403; oturumsuzda giriş sayfasına yönlendirme | 3 | **PASS** | unit-results.json |
| TC-TKT-04 | FR-13; FR-14 | Entegrasyon | İki talep sahibi, destek personeli, yönetici; GET /talepler/ | Talep sahibi yalnız kendi talebini, personel ve yönetici tümünü görür | 3 | **PASS** | unit-results.json |
| TC-TKT-05 | FR-13; FR-14 | Entegrasyon | Durum, öncelik, kategori ve atanan filtreleri; geçersiz değerler | Sonuç daralır; geçersiz değer yok sayılır; görünürlük genişlemez | 3 | **PASS** | unit-results.json |
| TC-TKT-06 | FR-13 | Entegrasyon | 30 talep; sayfa 1, 2, 3; filtreli sayfa bağlantısı | 25 + 5 kayıt; en yeni önce; filtre bağlantıda korunur; sayfa 3 için 404 | 3 | **PASS** | unit-results.json |
| TC-TKT-07 | FR-14 | Entegrasyon | Talep Sahibi; başkasının talebi ve olmayan numara için GET ve POST /talepler/<pk>/ | GET: ikisinde 404 ve aynı içerik, başlık ve numara görünmez; POST: ikisinde 405 | 3 | **PASS** | unit-results.json |
| TC-TKT-08 | FR-12; FR-14; NFR-05 | Entegrasyon | Destek personeli, yönetici ve talep sahibi; GET /talepler/<pk>/ | 200; numara, durum, öncelik, kategori, talep sahibi ve İstanbul saati (01.03.2026 12:05) | 3 | **PASS** | unit-results.json |
| TC-CAT-01 | FR-15 | Entegrasyon | Yönetici; POST /kategoriler/ yeni ad, aynı ad, Türkçe büyük harfli aynı ad, boş ad | Yeni ad eklenir; kopyalar (DONANIM, AĞ VE BAĞLANTI dahil) ve boş ad reddedilir | 3 | **PASS** | unit-results.json |
| TC-CAT-02 | FR-15; NFR-02 | Entegrasyon | Yönetici kategoriyi pasifleştirir; talep sahibi yeni talep formu ve doğrudan POST; GET ve CSRF belirteçsiz POST | Formda listelenmez; POST reddedilir; eski talep korunur; silinemez; GET 405; belirteçsiz 403 | 3 | **PASS** | unit-results.json |
| TC-CAT-03 | FR-09; FR-15 | Entegrasyon | Talep sahibi, destek personeli ve rolsüz kullanıcı; /kategoriler/ ve durum adresine GET/POST | 403; kategori değişmez | 3 | **PASS** | unit-results.json |
| TC-ARCH-01 | NFR-16 | Statik analiz | views/, services/ ve models/ kaynak kodu (Python AST) | Görünümde .objects yok; services'te views/HTTP/şablon içe aktarması yok; models'te services/views içe aktarması yok | 3 | **PASS** | unit-results.json |
| TC-ARCH-02 | FR-09; NFR-16 | Statik analiz | views/ paketindeki görünüm sınıfları (Python AST) | Her görünüm sınıfı LoginRequiredMixin veya PermissionRequiredMixin içerir | 3 | **PASS** | unit-results.json |
| TC-E2E-10 | FR-12; FR-13 | Sistem (E2E) | demo.talep; kısa başlıkla ve geçerli formla talep açma | Kısa başlık işaretlenir; INC numarası, Açık durumu, başarı mesajı; talep listede | 3 | **PASS** | e2e-week3-results.json |
| TC-E2E-11 | FR-14 | Sistem (E2E) | demo.destek talep açar; demo.talep adres çubuğuna o talebin adresini yazar | 404 ve Türkçe hata sayfası; başlık sızmaz; talep listede yok | 3 | **PASS** | e2e-week3-results.json (/talepler/2/ → 404; listede yok) |
| TC-E2E-12 | FR-13; NFR-07; NFR-08 | Sistem (E2E) | demo.destek; destek kuyruğu; P2 + Açık filtresi; 360×740 liste ve ayrıntı; durum rozeti renkleri | Talep kuyrukta ve filtrede; yatay taşma yok; rozet kontrastı ≥ 4.5:1 | 3 | **PASS** | e2e-week3-results.json |
| TC-E2E-13 | FR-15 | Sistem (E2E) | demo.yonetici kategori ekler ve pasifleştirir; demo.talep yeni talep formunu açar | Etkin kategori formda var; pasifleştirilince yok | 3 | **PASS** | e2e-week3-results.json (kategori eklendi ve formda göründü; pasifleştirilince formdan kalktı) |

| Sonuç | Test sayısı |
|---|---|
| PASS | 67 |
