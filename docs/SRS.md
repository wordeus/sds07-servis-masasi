# SDS-07 Yazılım Gereksinim Belirtimi (SRS)

| Alan | Değer |
|---|---|
| Doküman kimliği | SDS07-SRS |
| Sürüm | 0.4 (taslak) |
| Tarih | 26.11.2026 |
| Durum | Taslak, öğretim elemanı geri bildirimi bekliyor |
| Hazırlayan | Burak Nigiz (2100002062). Tek kişilik proje. |
| Onaylayan | [Boş: öğretim elemanı geri bildirimi sonrası] |
| Yapı dayanağı | ISO/IEC/IEEE 29148:2018, madde 9.6 "Software requirements specification (SRS) content" |

## Revizyon geçmişi

| Sürüm | Tarih | Yazar | Değişiklik |
|---|---|---|---|
| 0.1 | 30.10.2026 | Burak Nigiz | Hafta 1: ilk kapsam, aktörler, rol-yetki matrisi (plan), FR-01..FR-37, NFR-01..NFR-16, SLA/KPI kuralları, kabul kriterleri ve haftalık plan |
| 0.2 | 30.10.2026 | Burak Nigiz | Hafta 2: rol matrisi koddan üretildi (`roles.py`), Hafta 2'de uygulanan Django izinleri eklendi, Hafta 1-2 kabul kriterleri testlerle doğrulandı |
| 0.3 | 30.10.2026 | Burak Nigiz | Hafta 3: FR-12..FR-15 ve NFR-16 kabul kriterleri ayrıntılandırıldı (§7.1); Hafta 3 izinleri; AK-03 için geçici karar; NFR-07 kapsamı talep ekranlarına genişletildi; FR-10 kabul kriteri güncellendi |
| 0.4 | 26.11.2026 | Burak Nigiz | Hafta 4: teslim kapsamı Faz 5'te biter (KRR-18; §1.2, §2.6): FR-22..FR-37 ve NFR-13..NFR-15 gelecek çalışma; FR-16, FR-17, FR-20 kabul kriterleri (§7.1); Hafta 4 izinleri (§4); AK-03 kapandı (KRR-17) |

Not: Hafta 1-3 belgeleri geç kayıt nedeniyle birlikte hazırlandı; tarihler gerçek hazırlanma tarihidir.

Gereksinimlerin izlenebilirliği ve gerçek test sonuçları [RTM.md](RTM.md) dosyasındadır. RTM'nin kaynağı [traceability/requirements.csv](traceability/requirements.csv) dosyasıdır. Bu belgedeki gereksinim kimlikleri değişmez; silinen gereksinim "İptal" olarak işaretlenir, kimliği yeniden kullanılmaz.

---

## 1. Giriş

### 1.1 Amaç (29148 §9.6.2)

Bu belge, SDS-07 "ISO 9001 İlkelerini Destekleyen IT Servis Masası ve Süreç Takip Sistemi" yazılımının gereksinimlerini tanımlar. Hedef okuyucular proje ekibi, öğretim elemanı ve test/doğrulama sorumlularıdır.

### 1.2 Kapsam (29148 §9.6.3)

Sistem, kurum içi BT destek taleplerini kayıt altına alır, öncelik ve SLA hedeflerine göre izler, değişiklikleri yönetici onayıyla yürütür, müşteri memnuniyetini ve uygunsuzlukları ölçer ve iyileştirme faaliyetlerine bağlar. Böylece ISO 9001'in müşteri odaklılık, süreç yaklaşımı, kanıta dayalı karar verme ve iyileştirme ilkelerini destekler.

**Kapsam içi (proje talimatı, Ürün kapsamı 1-10):**

1. Talep sahibi, destek personeli ve yönetici rolleri
2. Destek talebi oluşturma, listeleme, kategori, öncelik, atama ve yorum
3. Incident akışı: Open → In Progress → Resolved → Closed
4. Basit değişiklik yönetimi: gerekçe, etki, risk, geri dönüş planı, yönetici onayı/reddi, uygulama sonucu
5. Önceliğe göre ilk yanıt ve çözüm SLA hedefleri
6. Süre dolmadan uygulama içi uyarı; ihlalde yöneticiye eskalasyon
7. Kapanmış talep için sahibinin bir kez verebildiği 1-5 memnuniyet puanı
8. Talep sayıları, ortalama süreler, SLA uyumu ve memnuniyet KPI paneli
9. Aktör, zaman ve durum değişikliklerini içeren işlem geçmişi
10. Uygunsuzluk, kök neden, düzeltici faaliyet ve etkinlik kontrolü kaydı

**Kapsam dışı:** e-posta/SMS bildirimi, mesai takvimine göre SLA (başlangıçta 7/24), dizin hizmeti (LDAP/AD) entegrasyonu, e-postayla talep açma, ayrı REST API, React/SPA, JWT, mikroservis, Kubernetes, yapay zekâ özellikleri, varlık/CMDB yönetimi, bilgi bankası, çok kiracılı yapı, üretim ortamına dağıtım otomasyonu.

**Teslim kapsamı (Hafta 4 kararı, KRR-18):** Proje Faz 5'te (11.12.2026) tamamlanır. Bu teslimde kapsam içi 1, 2, 3 ve 9. maddelerin talep bölümü uygulanır. 4-8 ve 10. maddeler (değişiklik yönetimi, SLA, uyarı ve eskalasyon, memnuniyet anketi, KPI paneli, uygunsuzluk ve DÖF) ile performans, yetkisiz erişim günlüğü ve Firefox uyumu (NFR-13..NFR-15) **gelecek çalışmadır**. Bu gereksinimlerin kimlikleri ve metinleri korunur; RTM'de "KAPSAM DIŞI (gelecek çalışma)" olarak görünürler. FR-20'nin değişiklik kararları ve düzeltici faaliyet kısmı da aynı nedenle kapsam dışıdır.

**Önemli sınır:** Yazılım ISO 9001 belgelendirmesi sağlamaz ve uygunluk beyanı yerine geçmez. Kuruluşun kalite yönetim sistemi uygulamalarını destekleyen bir araçtır. SLA süreleri kuruluş politikasıdır; ISO 9001 bu süreleri belirlemez.

### 1.3 Tanımlar ve kısaltmalar

| Terim | Tanım |
|---|---|
| Talep (Incident) | Bir kullanıcının BT hizmetiyle ilgili sorun veya isteğinin kaydı |
| İlk yanıt | Destek personeli veya yöneticinin talebe ilk müdahalesi (bkz. §6.2) |
| Çözüm | Talebin In Progress → Resolved geçişi |
| SLA | Hizmet düzeyi hedefi; bu projede önceliğe göre ilk yanıt ve çözüm süreleri |
| Eskalasyon | SLA ihlalinin yöneticilere bildirilmesi ve talebin işaretlenmesi |
| Değişiklik kaydı | BT ortamında yapılacak bir değişikliğin gerekçe, etki, risk ve geri dönüş planıyla kaydı |
| Uygunsuzluk | Bir şartın karşılanmaması (ör. SLA ihlali, düşük memnuniyet) |
| Düzeltici faaliyet | Uygunsuzluğun kök nedenini gidermek için yapılan faaliyet |
| Etkinlik kontrolü | Düzeltici faaliyetin amacına ulaşıp ulaşmadığının doğrulanması |
| KPI | Anahtar performans göstergesi |
| FR / NFR | Fonksiyonel / fonksiyonel olmayan gereksinim |
| MOD | Mimari modül kimliği (bkz. [SDD.md](SDD.md)) |
| TC | Test durumu kimliği (bkz. [TEST_PLAN.md](TEST_PLAN.md)) |
| PT-Ü*n* | Proje talimatı, Ürün kapsamı madde *n* |
| PT-YK | Proje talimatı, yetkilendirme kuralları paragrafı |
| PT-SLA | Proje talimatı, SLA kuralları paragrafı |
| PT-TEK | Proje talimatı, Teknoloji bölümü |
| PT-ÇB / PT-KNT | Proje talimatı, Çalışma biçimi / Gerçek kanıt kuralı |
| DJ-SEC | Django resmî güvenlik ve dağıtım kontrol listesi önerileri |
| EKİP | Proje ekibinin (tek kişi: Burak Nigiz) kararı veya varsayımı; öğretim elemanı geri bildirimine açıktır |

### 1.4 Referanslar

Standart baskıları, resmî bağlantılar ve madde numaralarının doğrulama durumu [STANDARDS.md](STANDARDS.md) dosyasındadır. Diğer kaynaklar: proje talimatı, iki haftalık ilerleme raporu şablonu, dönem sonu teslim şablonu ve vize soruları belgesi.

---

## 2. Genel tanım

### 2.1 Ürün perspektifi (29148 §9.6.4)

Tarayıcıdan kullanılan, sunucu tarafında işlenen bağımsız bir web uygulamasıdır. Tek Django 5.2 LTS projesi içinde tek uygulama (`servicedesk`) bulunur; iç yapı modüllere (MOD) ayrılır. Yerel geliştirmede SQLite kullanılır. SLA kontrolü Hafta 7'de bir yönetim komutu olarak eklenecek ve işletim sistemi zamanlayıcısıyla (Windows Görev Zamanlayıcısı veya cron) çalıştırılacaktır. Bağlam diyagramı: [SDD.md §3](SDD.md).

### 2.2 Ürün işlevleri (29148 §9.6.5)

| Modül | İşlev | Hafta |
|---|---|---|
| MOD-AUTH | Giriş, çıkış, oturum | 2 |
| MOD-ROLE | Rol grupları, rol-izin matrisi, sunucu tarafı yetkilendirme | 2 |
| MOD-UI | Ortak şablonlar, gezinme, hata sayfaları | 2 |
| MOD-CFG | Ayarlar, güvenlik profili, saat dilimi, test altyapısı | 1 |
| MOD-TICKET | Talep, kategori, öncelik, atama, yorum | 3-4 |
| MOD-AUDIT | İşlem geçmişi | 4-5 |
| MOD-WF | Durum makinesi | 5 |
| MOD-CHANGE | Değişiklik yönetimi | 6 |
| MOD-SLA | SLA hesaplama, uyarı, eskalasyon | 7-8 |
| MOD-NOTIF | Uygulama içi bildirim | 8 |
| MOD-SURVEY | Memnuniyet anketi | 9 |
| MOD-KPI | KPI paneli | 9 |
| MOD-CAPA | Uygunsuzluk ve düzeltici faaliyet | 10 |

### 2.3 Kullanıcı özellikleri (29148 §9.6.6)

| Aktör | Tanım | Teknik yetkinlik |
|---|---|---|
| Talep Sahibi | Destek isteyen çalışan; yalnız kendi kayıtlarını görür | Temel tarayıcı kullanımı |
| Destek Personeli | Talepleri üstlenen ve çözen BT çalışanı | Orta |
| Yönetici | Atama, değişiklik onayı, eskalasyon, KPI ve düzeltici faaliyetlerden sorumlu | Orta |
| Sistem yöneticisi | Django superuser; kullanıcı ve rol atamalarını yönetim sitesinden yapar | İleri |
| Zamanlayıcı (sistem aktörü) | SLA kontrol komutunu periyodik çalıştırır (Hafta 7) | - |

### 2.4 Sınırlamalar (29148 §9.6.7)

- Python, Django 5.2 LTS (sabitlenmiş yama: 5.2.18), Django Templates, Bootstrap 5 (5.3.8, yerel dosya), yerel geliştirmede SQLite.
- Django'nun hazır kullanıcı, oturum, grup, izin, form ve ORM altyapısı kullanılır; ayrı REST API, JWT, SPA, mikroservis kullanılmaz.
- Arayüz Türkçedir. Saatler UTC saklanır, Europe/Istanbul gösterilir.
- Dış hizmete (e-posta, bulut API) bağımlılık yoktur; demo çevrimdışı çalışabilir (yazı tipi ve Bootstrap yerel).

### 2.5 Varsayımlar ve bağımlılıklar (29148 §9.6.8)

| Kimlik | Varsayım | Doğrulayacak |
|---|---|---|
| VAR-01 | Kesin takvim verilene kadar 14 hafta ve 7 iki haftalık sprint geçerlidir; ilerleme haftalık paketler ve raporlarla izlenir | Öğretim elemanı |
| VAR-02 | SLA süreleri 7/24 takvim süresiyle ölçülür; mesai takvimi yoktur | Burak Nigiz |
| VAR-03 | Her kullanıcıya tek rol atanır; birden çok grup varsa öncelik Yönetici > Destek Personeli > Talep Sahibi | Burak Nigiz |
| VAR-04 | Kullanıcı ve rol yönetimini yalnız sistem yöneticisi (superuser) yapar | Burak Nigiz |
| VAR-05 | Saat dilimi gösterimi IANA tz veritabanındaki Europe/Istanbul kurallarına dayanır; Windows'ta `tzdata` paketi gerekir | Burak Nigiz |
| VAR-06 | Proje tek kişiliktir: Burak Nigiz (2100002062) tüm rolleri üstlenir. Bağımsız inceleme yapılamadığı için doğrulama otomatik kapılara (test, statik analiz, RTM tutarlılık denetimi) ve öğretim elemanı geri bildirimine dayanır | Burak Nigiz |
| VAR-07 | Başlangıç SLA hedefleri (§6.1) proje varsayımıdır; kuruluş politikasıyla değiştirilebilir | Burak Nigiz / öğretim elemanı |

### 2.6 Gereksinimlerin dağıtımı (29148 §9.6.9)

| Hafta | Sprint | Kapsam | Gereksinimler |
|---|---|---|---|
| 1 | 1 | Kapsam, gereksinimler, standart araştırması, kurulum ve doğrulama altyapısı | NFR-01, NFR-04, NFR-05, NFR-09..NFR-12 |
| 2 | 1 | Giriş/çıkış, roller, sunucu tarafı yetkilendirme, arayüz, tarayıcı testleri | FR-01..FR-11, NFR-02, NFR-03, NFR-06..NFR-08 |
| 3 | 2 | Talep oluşturma ve listeleme, kayıt bazlı erişim, kategoriler, modüler mimari | FR-12..FR-15, NFR-16 |
| 4 | 2 | Atama ve üzerine alma, yorumlar, işlem geçmişinin ilk sürümü | FR-16, FR-17, FR-20 |
| 5 | 3 | Durum geçişleri ve işlem geçmişi görünümü; final belgesi, sunum ve demo (bitiş fazı) | FR-18, FR-19, FR-21 |
| 6 | 3 | **Kapsam dışı (gelecek çalışma, KRR-18):** Değişiklik yönetimi; vize hazırlığı | FR-22..FR-25 |
| 7 | 4 | **Kapsam dışı (gelecek çalışma, KRR-18):** SLA politikası, hesaplama ve tekrarlanabilir kontrol | FR-26, FR-27, FR-30 |
| 8 | 4 | **Kapsam dışı (gelecek çalışma, KRR-18):** Uyarı, eskalasyon ve bildirim kutusu | FR-28, FR-29, FR-31 |
| 9 | 5 | **Kapsam dışı (gelecek çalışma, KRR-18):** Memnuniyet anketi ve KPI paneli | FR-32..FR-34 |
| 10 | 5 | **Kapsam dışı (gelecek çalışma, KRR-18):** Uygunsuzluk ve düzeltici faaliyet | FR-35..FR-37 |
| 11-12 | 6 | **Kapsam dışı (gelecek çalışma, KRR-18):** Güvenlik sertleştirme, performans, tarayıcı uyumu, kalite ölçümleri, CI/CD | NFR-13..NFR-15 |
| 13-14 | 7 | **Faz 5'e taşındı (KRR-18):** final belgesi, sunum, demo | - |

Her faz (Hafta 1-5) ayrı paket, ayrı ilerleme raporu ve ayrı GitHub etiketiyle (`hafta-N`) teslim edilir. Faz 5 bitiş fazıdır (KRR-18).

---

## 3. Paydaş gereksinimleri (StRS özeti)

### 3.1 Kullanıcı hikâyeleri

| Kimlik | Hikâye | İlgili gereksinim |
|---|---|---|
| US-01 | Bir çalışan olarak hesabımla giriş yapmak istiyorum ki taleplerimi güvenle izleyebileyim. | FR-01..FR-05 |
| US-02 | Bir sistem yöneticisi olarak kullanıcılara rol atamak istiyorum ki herkes yalnız yetkili olduğu işlemleri yapsın. | FR-06, FR-07 |
| US-03 | Bir kullanıcı olarak hangi rolle çalıştığımı ve neler yapabileceğimi görmek istiyorum. | FR-08, FR-10 |
| US-04 | Bir talep sahibi olarak kategori ve öncelik seçerek talep açmak ve yalnız kendi taleplerimi görmek istiyorum. | FR-12..FR-14 |
| US-05 | Bir destek personeli olarak atanmamış talepleri üzerime almak, yorumlamak ve çözmek istiyorum. | FR-16..FR-19 |
| US-06 | Bir yönetici olarak değişiklikleri risk ve geri dönüş planıyla değerlendirip onaylamak veya reddetmek istiyorum. | FR-22..FR-25 |
| US-07 | Bir destek personeli olarak SLA süresi dolmadan uyarı almak istiyorum. | FR-26..FR-28, FR-31 |
| US-08 | Bir yönetici olarak ihlal olan talepleri anında öğrenmek istiyorum. | FR-29, FR-30 |
| US-09 | Bir talep sahibi olarak kapanan talebime puan vermek istiyorum. | FR-32 |
| US-10 | Bir yönetici olarak talep sayılarını, ortalama süreleri, SLA uyumunu ve memnuniyeti tek panelde görmek istiyorum. | FR-33, FR-34 |
| US-11 | Bir yönetici olarak uygunsuzlukları kök neden ve düzeltici faaliyetle izleyip etkinliğini doğrulamak istiyorum. | FR-35..FR-37 |
| US-12 | Bir denetçi olarak kimin neyi ne zaman değiştirdiğini görmek istiyorum. | FR-20, FR-21 |

### 3.2 İş kuralları

| Kimlik | Kural | Kaynak |
|---|---|---|
| BR-01 | Talep sahibi yalnız kendi kayıtlarına erişir. | PT-YK |
| BR-02 | Yetki sunucuda denetlenir; düğmeyi veya bağlantıyı gizlemek yetkilendirme sayılmaz. Doğrudan adres ve form istekleri de denetlenir. | PT-YK |
| BR-03 | Onaylanmamış değişiklik uygulanamaz. | PT-YK |
| BR-04 | Değişikliği açan kullanıcı aynı kaydı onaylayamaz (görevler ayrılığı). | EKİP |
| BR-05 | İlk yanıt ve çözüm süreleri ayrı hesaplanır; süre 7/24 takvim süresidir. | PT-SLA |
| BR-06 | Zaman damgaları UTC saklanır, Europe/Istanbul gösterilir. | PT-SLA |
| BR-07 | Memnuniyet puanı yalnız Closed durumundaki talep için, yalnız talep sahibi tarafından, yalnız bir kez ve 1-5 arası tam sayı olarak verilir. | PT-Ü7 |
| BR-08 | Her durum değişikliği aktör, UTC zaman, eski ve yeni değerle kaydedilir; kayıt arayüzden değiştirilemez veya silinemez. | PT-Ü9 |
| BR-09 | SLA kontrolü kaç kez çalıştırılırsa çalıştırılsın aynı olay için birden fazla bildirim üretmez. | PT-SLA |
| BR-10 | SLA hedefleri kuruluş politikasıdır; ISO 9001'in belirlediği süreler gibi sunulmaz. | PT-SLA |
| BR-11 | Closed durumundaki talebe yorum eklenemez. | EKİP |
| BR-12 | Düzeltici faaliyet, etkinlik kontrolü "Etkili" sonuçlanmadan kapatılamaz. | PT-Ü10 |

---

## 4. Rol-yetki matrisi

Matris koddaki tanımdan üretilmiştir (`servicedesk/roles.py`, `CAPABILITIES`). Panelde her kullanıcıya kendi rolünün satırları gösterilir.

| Yetenek | Talep Sahibi | Destek Personeli | Yönetici | Hafta |
|---|---|---|---|---|
| Giriş yapma ve kendi panelini görme | Kendi hesabı | Kendi hesabı | Kendi hesabı | 2 |
| Destek kuyruğu çalışma alanı | - | Tam erişim | Tam erişim | 2 |
| Yönetim paneli | - | - | Tam erişim | 2 |
| Talep oluşturma | Kendi adına | Kendi adına | Kendi adına | 3 |
| Talepleri görüntüleme | Yalnız kendi talepleri | Tüm talepler | Tüm talepler | 3 |
| Kategori ekleme ve pasifleştirme | - | - | Tam erişim | 3 |
| Talebe yorum ekleme | Kendi taleplerine | Tüm taleplere | Tüm taleplere | 4 |
| Talebi üzerine alma | - | Atanmamış talepler | Atanmamış talepler | 4 |
| Talebi destek personeline atama | - | - | Tüm talepler | 4 |
| Talep önceliğini değiştirme | - | Tüm talepler | Tüm talepler | 4 |
| Durum ilerletme (Açık → İşlemde → Çözüldü) | - | Kendisine atanmış talepler | Tüm talepler | 5 |
| Talebi kapatma (Çözüldü → Kapandı) | Kendi talebini onaylayarak | - | Tüm talepler | 5 |
| Değişiklik kaydı açma ve uygulama sonucu girme | - | Sonuç yalnız onaylı kayıtta | Sonuç yalnız onaylı kayıtta | Kapsam dışı |
| Değişikliği onaylama veya reddetme | - | - | Kendi açtığı kayıt hariç | Kapsam dışı |
| SLA süre uyarılarını alma | - | Kendisine atanmış talepler | - | Kapsam dışı |
| SLA ihlali eskalasyonlarını alma | - | - | Tüm ihlaller | Kapsam dışı |
| Memnuniyet puanı verme | Kendi kapanmış talebine bir kez | - | - | Kapsam dışı |
| KPI paneli | - | - | Tam erişim | Kapsam dışı |
| Uygunsuzluk kaydı açma | - | Tam erişim | Tam erişim | Kapsam dışı |
| Kök neden, düzeltici faaliyet ve etkinlik kontrolü | - | - | Tam erişim | Kapsam dışı |

**Hafta 4'te uygulanan Django izinleri** (her `migrate` sonrasında gruplara uygulanır; tablo koddan üretildi):

| Grup (rol) | İzinler |
|---|---|
| Talep Sahibi | `servicedesk.add_comment`, `servicedesk.add_ticket`, `servicedesk.view_ticket` |
| Destek Personeli | `servicedesk.access_support_workspace`, `servicedesk.add_comment`, `servicedesk.add_ticket`, `servicedesk.change_ticket_priority`, `servicedesk.take_ticket`, `servicedesk.view_all_tickets`, `servicedesk.view_ticket` |
| Yönetici | `servicedesk.access_manager_panel`, `servicedesk.access_support_workspace`, `servicedesk.add_category`, `servicedesk.add_comment`, `servicedesk.add_ticket`, `servicedesk.assign_ticket`, `servicedesk.change_category`, `servicedesk.change_ticket_priority`, `servicedesk.take_ticket`, `servicedesk.view_all_tickets`, `servicedesk.view_category`, `servicedesk.view_ticket` |

`view_ticket` talep ekranlarına erişimi verir; hangi kayıtların görüleceğini `view_all_tickets` izni ve kayıt bazlı politika (`services/tickets.py`, `visible_tickets_for`) belirler: bu izni olmayan kullanıcı yalnız kendi açtığı talepleri görür (FR-14).

Sistem yöneticisi (superuser) tüm izinlere sahiptir ve yönetim sitesine (`/admin/`) erişen tek hesap türüdür.

---

## 5. Belirtilmiş gereksinimler (29148 §9.6.10)

Gereksinim dili: "-malıdır / -melidir" zorunluluk bildirir. Her gereksinim tek bir koşulu tanımlar, ölçülebilir bir kabul kriteriyle doğrulanır ve RTM'de bir mimari bileşene ve teste bağlanır (29148 §5.2.5, §5.2.7). Öncelik ölçeği: Çok Yüksek / Yüksek / Orta / Düşük.

### 5.1 Dış arayüzler (29148 §9.6.11)

- **Kullanıcı arayüzü:** Django şablonları ve Bootstrap 5.3.8 ile sunucu tarafında üretilen HTML sayfaları; masaüstü ve 360 px genişliğe kadar mobil tarayıcı.
- **Yazılım arayüzleri:** Yok (ayrı API kapsam dışı). Veritabanı erişimi yalnız Django ORM üzerinden yapılır.
- **İletişim:** HTTP(S). Üretim profilinde HTTPS yönlendirmesi ve güvenli çerezler zorunludur.

### 5.2 Fonksiyonel gereksinimler (29148 §9.6.12)

#### MOD-AUTH: Kimlik doğrulama (Hafta 2)

| ID | Gereksinim | Öncelik | Kaynak | Doğrulama |
|---|---|---|---|---|
| FR-01 | Sistem, etkin bir kullanıcının kullanıcı adı ve parolasıyla oturum açmasını sağlamalı ve başarılı girişten sonra kullanıcıyı kendi paneline (`/`) yönlendirmelidir. Oturumu açık kullanıcı giriş sayfasını açtığında paneline yönlendirilmelidir. | Çok Yüksek | PT-Ü1, PT-TEK | Test |
| FR-02 | Sistem, hatalı parola, bilinmeyen kullanıcı adı veya pasif hesapla yapılan girişte oturum açmamalı ve üç durumda da aynı genel hata mesajını göstermelidir; mesaj hangi bilginin hatalı olduğunu veya hesabın durumunu açığa vurmamalıdır. | Yüksek | PT-Ü1, DJ-SEC | Test |
| FR-03 | Sistem, oturumu yalnız CSRF korumalı POST isteğiyle kapatmalı, çıkıştan sonra giriş sayfasına yönlendirmeli ve GET ile gelen çıkış isteğini HTTP 405 ile reddetmelidir. | Yüksek | PT-Ü1, DJ-SEC | Test |
| FR-04 | Sistem, giriş sayfası ve statik dosyalar dışındaki her sayfa için oturum istemeli; oturumsuz GET ve POST isteklerini, istenen adresi `next` parametresinde koruyarak giriş sayfasına yönlendirmelidir. | Çok Yüksek | PT-YK | Test |
| FR-05 | Sistem, girişten sonra `next` parametresiyle yalnız aynı site içindeki adreslere yönlendirmeli; başka alan adına işaret eden değerleri yok sayıp kullanıcıyı paneline yönlendirmelidir. | Yüksek | DJ-SEC | Test |

#### MOD-ROLE: Roller ve yetkilendirme (Hafta 2)

| ID | Gereksinim | Öncelik | Kaynak | Doğrulama |
|---|---|---|---|---|
| FR-06 | Sistem, Talep Sahibi, Destek Personeli ve Yönetici rollerini Django grubu olarak her `migrate` sonunda otomatik oluşturmalı ve her grubun izinlerini koddaki rol-izin matrisiyle birebir eşitlemelidir; işlem tekrarlandığında kopya oluşturmamalıdır. | Çok Yüksek | PT-Ü1, PT-TEK | Test |
| FR-07 | Sistem yöneticisi, Django yönetim sitesinden kullanıcı oluşturabilmeli ve kullanıcıya rol grubu atayabilmelidir; diğer roller yönetim sitesine erişememelidir. | Yüksek | PT-Ü1 | Test |
| FR-08 | Sistem, kullanıcının rolünü grup üyeliğinden belirlemeli ve her sayfanın üst bilgisinde göstermelidir. Birden çok rol grubunda öncelik Yönetici > Destek Personeli > Talep Sahibi olmalı; rol grubu olmayan kullanıcıya "Rol atanmamış" uyarısı gösterilmelidir. | Yüksek | PT-Ü1 | Test |
| FR-09 | Sistem, rol gerektiren her sayfa ve form isteğinde (GET ve POST) yetkiyi sunucuda, görünüm çalışmadan önce denetlemeli; yetkisi olmayan oturumlu kullanıcıya HTTP 403 ve rolünü ve istenen adresi belirten Türkçe hata sayfası döndürmelidir. | Çok Yüksek | PT-YK | Test |
| FR-10 | Gezinme menüsü yalnız kullanıcının izinli olduğu bölümlerin bağlantılarını göstermelidir. Bu gereksinim FR-09'un yerine geçmez. | Orta | PT-YK | Test |
| FR-11 | Sistem, geliştirme ortamında her rol için bir demo kullanıcı oluşturan, tekrar çalıştırıldığında kopya üretmeyen, parolayı koda gömmeyen ve DEBUG kapalıyken çalışmayı reddeden bir yönetim komutu sağlamalıdır. | Düşük | PT-ÇB | Test |

#### MOD-TICKET: Talep işlemleri (Hafta 3-4)

| ID | Gereksinim | Öncelik | Kaynak | Doğrulama |
|---|---|---|---|---|
| FR-12 | Sistem, talep oluşturma yetkisi olan kullanıcının başlık (5-200 karakter), açıklama (zorunlu), etkin bir kategori ve öncelik (P1-P4) girerek talep oluşturmasını sağlamalı; talebe benzersiz numara, UTC oluşturma zamanı ve "Open" durumu atamalıdır. | Çok Yüksek | PT-Ü2 | Test |
| FR-13 | Sistem, talepleri durum, öncelik, kategori ve atanan kişiye göre filtrelenebilir ve sayfa başına 25 kayıtla sayfalanmış olarak listelemelidir. | Yüksek | PT-Ü2 | Test |
| FR-14 | Talep sahibi başkasına ait bir talebin ayrıntı, yorum, anket veya işlem adresine doğrudan istek gönderdiğinde sistem HTTP 404 döndürmeli ve kaydın varlığını açığa vurmamalıdır. Liste sorguları da yalnız kullanıcının kendi kayıtlarını içermelidir. | Çok Yüksek | PT-YK | Test |
| FR-15 | Yönetici veya sistem yöneticisi kategori ekleyip pasifleştirebilmeli; pasif kategori yeni talep formunda listelenmemelidir. | Orta | PT-Ü2 | Test |
| FR-16 | Yönetici talebi yalnız Destek Personeli rolündeki bir kullanıcıya atayabilmeli; destek personeli atanmamış talebi kendi üzerine alabilmelidir. | Yüksek | PT-Ü2 | Test |
| FR-17 | Talep sahibi kendi talebine, destek personeli ve yönetici tüm taleplere yorum ekleyebilmeli; Closed durumundaki talebe yorum eklenememelidir. | Yüksek | PT-Ü2 | Test |

#### MOD-WF ve MOD-AUDIT: Durum akışı ve işlem geçmişi (Hafta 4-5)

| ID | Gereksinim | Öncelik | Kaynak | Doğrulama |
|---|---|---|---|---|
| FR-18 | Sistem talep durumunun yalnız Open → In Progress → Resolved → Closed sırasıyla ilerlemesine izin vermeli; tanımsız geçiş isteklerini (doğrudan POST dahil) sunucuda reddetmelidir. | Çok Yüksek | PT-Ü3 | Test |
| FR-19 | Open → In Progress ve In Progress → Resolved geçişlerini yalnız talebe atanmış destek personeli veya yönetici, Resolved → Closed geçişini talep sahibi veya yönetici yapabilmelidir. Resolved geçişinde çözüm açıklaması zorunlu olmalıdır. | Çok Yüksek | PT-Ü3, PT-YK | Test |
| FR-20 | Sistem talep oluşturma, durum geçişi, atama, öncelik değişikliği, değişiklik kararları ve düzeltici faaliyet durum değişikliklerini aktör, UTC zaman, eski ve yeni değerle kaydetmeli; bu kayıtlar arayüzden düzenlenememeli ve silinememelidir. | Çok Yüksek | PT-Ü9 | Test |
| FR-21 | Talep ayrıntı sayfası o talebin işlem geçmişini kronolojik olarak Europe/Istanbul saatiyle göstermelidir; talep sahibi yalnız kendi talebinin geçmişini görebilmelidir. | Yüksek | PT-Ü9, PT-YK | Test |

#### MOD-CHANGE: Değişiklik yönetimi (Hafta 6)

| ID | Gereksinim | Öncelik | Kaynak | Doğrulama |
|---|---|---|---|---|
| FR-22 | Destek personeli ve yönetici başlık, açıklama, gerekçe, etki, risk düzeyi (Düşük/Orta/Yüksek), risk açıklaması, geri dönüş planı ve planlanan uygulama zamanı zorunlu olan değişiklik kaydı oluşturabilmeli; kayıt "Onay Bekliyor" durumunda başlamalıdır. | Yüksek | PT-Ü4 | Test |
| FR-23 | Yalnız Yönetici rolü "Onay Bekliyor" durumundaki değişikliği onaylayabilmeli veya reddedebilmeli; ret için gerekçe zorunlu olmalı; kaydı açan kullanıcı kendi kaydını onaylayamamalıdır. | Çok Yüksek | PT-Ü4 | Test |
| FR-24 | Sistem, "Onaylandı" durumunda olmayan değişiklik için uygulama sonucu kaydını sunucuda reddetmelidir. | Çok Yüksek | PT-YK, PT-Ü4 | Test |
| FR-25 | Onaylanan değişikliğin uygulama sonucu (Başarılı / Başarısız-geri alındı), gerçek uygulama zamanı ve not ile kaydedilebilmeli; sonuç kaydından sonra değişiklik değiştirilememelidir. | Yüksek | PT-Ü4 | Test |

#### MOD-SLA ve MOD-NOTIF: SLA, uyarı ve eskalasyon (Hafta 7-8)

| ID | Gereksinim | Öncelik | Kaynak | Doğrulama |
|---|---|---|---|---|
| FR-26 | Sistem her öncelik için ilk yanıt ve çözüm hedef sürelerini yapılandırılabilir SLA politikası olarak saklamalıdır; başlangıç değerleri §6.1'deki tablodur. | Yüksek | PT-Ü5, PT-SLA | Test |
| FR-27 | Sistem ilk yanıt ve çözüm sürelerini §6.2 ve §6.3'teki olay tanımlarına ve sınır kurallarına göre ayrı ayrı hesaplamalıdır. | Çok Yüksek | PT-SLA | Test |
| FR-28 | Arka plan kontrolü, kalan süresi hedef sürenin %20'si veya daha azı olan ve henüz sonuçlanmamış her SLA ölçütü için talebe atanmış destek personeline bir kez uygulama içi uyarı üretmelidir (atanmamışsa yöneticilere). | Yüksek | PT-Ü6 | Test |
| FR-29 | İhlal gerçekleşen her SLA ölçütü için tüm Yönetici rolü kullanıcılarına bir kez eskalasyon bildirimi üretilmeli ve talep "eskale edildi" olarak işaretlenmelidir. | Yüksek | PT-Ü6 | Test |
| FR-30 | SLA kontrol komutu kaç kez çalıştırılırsa çalıştırılsın aynı (talep, ölçüt, olay türü) için en fazla bir bildirim üretmeli; bu kural veritabanı tekillik kısıtıyla güvenceye alınmalıdır. Kesintiden sonra çalıştırıldığında kaçırılan olayları tamamlamalıdır. | Yüksek | PT-SLA | Test |
| FR-31 | Kullanıcı okunmamış bildirim sayısını menüde görebilmeli, yalnız kendi bildirimlerini listeleyebilmeli ve okundu olarak işaretleyebilmelidir. | Orta | PT-Ü6 | Test |

#### MOD-SURVEY, MOD-KPI, MOD-CAPA (Hafta 9-10)

| ID | Gereksinim | Öncelik | Kaynak | Doğrulama |
|---|---|---|---|---|
| FR-32 | Talep Closed durumundayken yalnız talep sahibi 1-5 arası tam sayı puan ve isteğe bağlı yorum verebilmeli; her talep için en fazla bir anket kaydı olmalı (veritabanı tekillik kısıtı) ve verilen puan değiştirilememelidir. | Yüksek | PT-Ü7 | Test |
| FR-33 | Yönetici, seçtiği tarih aralığı için oluşturulan/kapanan talep sayılarını (durum, öncelik, kategoriye göre), ortalama ilk yanıt ve çözüm sürelerini, ilk yanıt ve çözüm SLA uyum oranlarını, ortalama memnuniyet puanını ve anket yanıt oranını görebilmelidir; panel diğer rollere kapalı olmalıdır. | Yüksek | PT-Ü8 | Test |
| FR-34 | KPI değerleri §6.5'teki pay/payda ve dönem kurallarına göre hesaplanmalı; payda sıfırsa değer "veri yok" olarak gösterilmelidir. | Yüksek | PT-SLA, PT-Ü8 | Test |
| FR-35 | Destek personeli ve yönetici; kaynak (SLA ihlali, düşük memnuniyet, iç denetim, müşteri şikâyeti, diğer), açıklama ve isteğe bağlı ilişkili talep ile uygunsuzluk kaydı açabilmelidir. | Yüksek | PT-Ü10 | Test |
| FR-36 | Yönetici kök neden analizini (yöntem ve bulgu) ve düzeltici faaliyeti (açıklama, sorumlu, termin) kaydedebilmeli; kayıt Açık → Analiz → Faaliyet → Etkinlik Kontrolü → Kapalı sırasıyla ilerlemelidir. | Yüksek | PT-Ü10 | Test |
| FR-37 | Yönetici etkinlik kontrolü sonucunu (Etkili / Etkili değil) ve kanıt notunu kaydetmeli; "Etkili değil" sonucu kaydı Faaliyet durumuna geri döndürmeli, "Etkili" sonucu kaydı kapatmalıdır. | Yüksek | PT-Ü10 | Test |

### 5.3 Kullanılabilirlik gereksinimleri (29148 §9.6.13)

| ID | Gereksinim | Öncelik | Doğrulama |
|---|---|---|---|
| NFR-06 | Arayüz Türkçe olmalı; sayfa dili `lang="tr"` bildirilmeli; form etiketleri ve hata sayfaları Türkçe olmalıdır. | Yüksek | Test |
| NFR-07 | Giriş ve panel sayfaları (Hafta 3'ten itibaren talep listesi ve talep ayrıntısı da) 360 px genişlikte sayfa düzeyinde ve iç kapsayıcılarda yatay kaydırma gerektirmeden kullanılabilmelidir. | Orta | Test (E2E) |
| NFR-08 | Giriş akışı yalnız klavyeyle tamamlanabilmeli, odaklanan öğe görünür odak çizgisiyle belirtilmeli; metin ve düğme kontrastı en az 4.5:1 olmalıdır (WCAG 2.1 AA hedefi; uyum iddiası değildir). Hafta 2'de giriş ve panel ekranları, Hafta 11-12'de tüm ekranlar ölçülür. | Orta | Test (E2E) |

### 5.4 Performans gereksinimleri (29148 §9.6.14)

| ID | Gereksinim | Öncelik | Doğrulama |
|---|---|---|---|
| NFR-13 | Talep listesi sayfası, 1.000 talep içeren SQLite veritabanında yerel geliştirme makinesinde 100 ardışık istekte 95. persentilde 500 ms'den kısa sürede yanıt vermelidir (Hafta 11-12'de ölçülecek; şu an ÖLÇÜLMEDİ). | Orta | Test (ölçüm) |

### 5.5 Mantıksal veritabanı gereksinimleri (29148 §9.6.15)

- Zaman damgaları UTC saklanır (`USE_TZ=True`); gösterim Europe/Istanbul'dur (NFR-05).
- İşlem geçmişi kayıtları yalnız eklenir; güncelleme ve silme arayüzden yapılamaz (FR-20).
- Anket (talep başına bir) ve SLA bildirimleri (talep, ölçüt, olay türü başına bir) veritabanı tekillik kısıtıyla korunur (FR-30, FR-32).
- Varlıklar ve ilişkileri (Hafta 3: User, Category, Ticket; diğerleri planlı): [SDD.md §6](SDD.md) (bilgi görünümü, ER diyagramı).

### 5.6 Tasarım kısıtları (29148 §9.6.16)

- Tek Django projesi, tek uygulama (`servicedesk`), modüler iç yapı; iş kuralları görünümlerden ayrı servis fonksiyonlarında tutulur. Hafta 3'te `models/`, `services/`, `views/` paketleri kuruldu; katman kuralı TC-ARCH-01 ile her test koşusunda denetlenir (NFR-16).
- Kimlik doğrulama, oturum, grup, izin, form ve ORM için Django'nun hazır altyapısı kullanılır.
- Bağımlılıklar sabitlenir (`requirements*.txt`); yeni bağımlılık ekleme kararı gerekçesiyle [SDD.md §9](SDD.md) karar günlüğüne yazılır.

### 5.7 Standartlara uyum (29148 §9.6.17)

ISO 9001:2026 ana alan standardıdır; gereksinimlerin ilgili maddelerle eşlemesi RTM'nin "Standart eşlemesi" bölümünde ve [STANDARDS.md](STANDARDS.md) dosyasındadır. Eşleme, gereksinimin hangi madde amacını desteklediğini gösterir; uygunluk veya belgelendirme iddiası değildir.

### 5.8 Yazılım sistemi nitelikleri (29148 §9.6.18)

ISO/IEC 25010:2023 karakteristikleriyle eşleme:

| ID | Gereksinim | Karakteristik / alt karakteristik | Öncelik | Hafta |
|---|---|---|---|---|
| NFR-01 | Parolalar Django'nun varsayılan PBKDF2-SHA256 özet algoritmasıyla saklanmalı; en az 10 karakter, kullanıcı bilgilerine benzemeyen, yaygın olmayan ve yalnız rakamdan oluşmayan parola kuralları uygulanmalıdır. | Security / confidentiality (3.6.1) | Çok Yüksek | 1 |
| NFR-02 | Durum değiştiren her POST isteği geçerli CSRF belirteci olmadan HTTP 403 ile reddedilmelidir. | Security / integrity (3.6.2) | Çok Yüksek | 2 |
| NFR-03 | Oturum çerezi HttpOnly ve SameSite=Lax olmalı; oturum süresi 8 saat (28.800 sn) olmalı; üretim profilinde oturum ve CSRF çerezleri yalnız HTTPS üzerinden gönderilmelidir. | Security / confidentiality (3.6.1) | Yüksek | 2 |
| NFR-04 | Üretim profili; SECRET_KEY ve ALLOWED_HOSTS tanımsızken veya DEBUG açıkken başlamamalı, geçersiz ortam değişkeni değerlerini reddetmeli ve `manage.py check --deploy --fail-level WARNING` denetiminden gerekçesi belgelenmiş susturmalar dışında uyarısız geçmelidir. | Security / resistance (3.6.6) | Çok Yüksek | 1 |
| NFR-05 | Tüm zaman damgaları veritabanında UTC saklanmalı ve arayüzde Europe/Istanbul saatiyle "GG.AA.YYYY SS:dd" biçiminde gösterilmelidir. | Functional suitability / functional correctness (3.1.2) | Çok Yüksek | 1 |
| NFR-09 | Üretim kodunun (testler ve migration dosyaları hariç) satır ve dal kapsamı en az %80 olmalı; test sonuçları TC kimlikleriyle makinece okunur (JSON) biçimde kaydedilmelidir. | Maintainability / testability | Yüksek | 1 |
| NFR-10 | Kod tabanı yapılandırılmış ruff kural setinden (pycodestyle, pyflakes, import sırası, bugbear, Django, bandit güvenlik, pyupgrade) sıfır bulguyla geçmelidir; muafiyetler gerekçesiyle `pyproject.toml` içinde yazılı olmalıdır. | Maintainability / analysability | Orta | 1 |
| NFR-11 | Uygulama sabitlenmiş bağımlılıklarla Windows ve Ubuntu üzerinde Python 3.12 ve 3.13 ile `docs/INSTALL.md` adımları izlenerek kurulabilmeli ve testleri geçmelidir. | Flexibility / installability | Yüksek | 1 |
| NFR-12 | Sistem kullanıcı hakkında yalnız kullanıcı adı, ad, soyad ve e-posta saklamalı; demo ve test verilerinde gerçek kişi verisi kullanılmamalıdır (KVKK farkındalığı). | Security / confidentiality (3.6.1) | Yüksek | 1 |
| NFR-14 | Yetkisiz erişim denemeleri (403) kullanıcı adı, adres ve UTC zamanla uygulama günlüğüne yazılmalıdır. | Security / accountability (3.6.4) | Orta | 11-12 |
| NFR-15 | Arayüz Chromium tabanlı tarayıcıların ve Firefox'un güncel sürümlerinde E2E senaryolarını geçmelidir. | Flexibility / adaptability | Orta | 11-12 |
| NFR-16 | İş kuralları (yetki politikası, durum geçişi, SLA, KPI hesapları) görünüm katmanından ayrı servis modüllerinde bulunmalı; her MOD bir Python modülü veya paketiyle eşlenmelidir. | Maintainability / modularity (3.7.1) | Orta | 3 |

Not: Ders belgesindeki kalite sorusu ISO/IEC 25010'un 8 karakteristikli 2011 yapısını kullanır. 2023 baskısında karakteristik sayısı 9'dur: Usability yerine Interaction capability, Portability yerine Flexibility gelmiş ve Safety eklenmiştir ([STANDARDS.md](STANDARDS.md)).

---

## 6. SLA ve KPI tanım kuralları

### 6.1 Başlangıç SLA hedefleri (proje varsayımı, VAR-07)

| Öncelik | Anlam | İlk yanıt hedefi | Çözüm hedefi |
|---|---|---|---|
| P1 | Kritik: hizmet tamamen durdu | 30 dakika | 4 saat |
| P2 | Yüksek: önemli işlev etkilendi | 1 saat | 8 saat |
| P3 | Orta: geçici çözüm var | 4 saat | 24 saat |
| P4 | Düşük: bilgi/istek | 8 saat | 72 saat |

Bu değerler proje varsayımıdır (VAR-07); ISO 9001 bu süreleri belirlemez. Değerler yönetim sitesinden değiştirilebilir olacaktır (FR-26).

### 6.2 Olay tanımları

- **Başlangıç anı (t0):** Talebin oluşturulma zamanı (UTC).
- **İlk yanıt anı:** Destek personeli veya yöneticinin talebe ilk yorumu ya da talebin ilk Open → In Progress geçişi; hangisi önce olursa. Talep sahibinin kendi yorumu ve atama işlemi ilk yanıt sayılmaz.
- **Çözüm anı:** Talebin ilk In Progress → Resolved geçişi.
- **Saat:** 7/24 takvim süresi; duraklatma (ör. "kullanıcı bekleniyor") yoktur.

### 6.3 Sınır kuralları

- Hedef zaman = t0 + hedef süre.
- Olay hedef zamana **eşit veya önce** gerçekleşirse ölçüt **karşılandı** sayılır.
- Olay hedef zamandan **sonra** gerçekleşirse veya hedef zaman olay olmadan geçerse ölçüt **ihlal** sayılır. İhlal anı = hedef zaman.
- **Uyarı eşiği:** Kalan süre ≤ hedef sürenin %20'si ve ölçüt henüz sonuçlanmamışsa (ör. P1 çözüm: son 48 dakika).
- **Öncelik değişikliği:** Hedef zamanlar yeni önceliğe göre t0'dan yeniden hesaplanır; değişiklik işlem geçmişine yazılır. Önceden sonuçlanmış ölçütler değişmez.
- Karşılaştırmalar UTC değerlerle yapılır; gösterim Europe/Istanbul'dur.

### 6.4 Tekrarlanabilir arka plan kontrolü

- `manage.py check_sla` komutu (Hafta 7) her çalıştığında açık ölçütleri değerlendirir.
- Bildirim tekillik anahtarı: (talep, ölçüt [ilk yanıt/çözüm], olay türü [uyarı/eskalasyon]). Anahtar veritabanında tekil kısıtlıdır; aynı olay ikinci kez üretilemez.
- Komut kesintiden sonra çalıştırıldığında, kaçırılan uyarı ve ihlalleri bir kez üretir.

### 6.5 KPI pay/payda ve dönem kuralları

Dönem, Europe/Istanbul yerel günlerine göre [başlangıç günü 00:00, bitiş günü + 1 gün 00:00) yarı açık aralığıdır; sınırlar UTC'ye çevrilerek sorgulanır.

| KPI | Pay | Payda | Döneme atama |
|---|---|---|---|
| Oluşturulan talep sayısı | Dönemde oluşturulan talepler | - | Oluşturulma zamanı |
| Kapanan talep sayısı | Dönemde Closed olan talepler | - | Kapanma zamanı |
| Ortalama ilk yanıt süresi | Σ(ilk yanıt − t0) | İlk yanıtı dönemde olan talep sayısı | İlk yanıt zamanı |
| Ortalama çözüm süresi | Σ(çözüm − t0) | Çözümü dönemde olan talep sayısı | Çözüm zamanı |
| İlk yanıt SLA uyumu (%) | Karşılanan ilk yanıt ölçütleri | Karşılanan + ihlal edilen ilk yanıt ölçütleri | Oluşturulma zamanı |
| Çözüm SLA uyumu (%) | Karşılanan çözüm ölçütleri | Karşılanan + ihlal edilen çözüm ölçütleri | Oluşturulma zamanı |
| Ortalama memnuniyet | Σ puan | Anket sayısı | Talebin kapanma zamanı |
| Anket yanıt oranı (%) | Anket sayısı | Dönemde kapanan talep sayısı | Talebin kapanma zamanı |

Henüz sonuçlanmamış SLA ölçütleri paydaya katılmaz. Payda 0 ise değer "veri yok" gösterilir (0 değil).

---

## 7. Kabul kriterleri

### 7.1 Hafta 1-4 (ayrıntılı)

| Gereksinim | Kabul kriteri (Verilen / Olduğunda / Beklenen) | Test |
|---|---|---|
| FR-01 | Etkin kullanıcı verilmişken doğru kullanıcı adı ve parola gönderildiğinde yanıt 302 ile `/` adresine gider ve oturumda kullanıcı kimliği bulunur. Oturum açıkken `/hesap/giris/` açıldığında `/` adresine yönlendirilir. | TC-AUTH-01..03, TC-E2E-01, TC-E2E-02 |
| FR-02 | Hatalı parola, bilinmeyen kullanıcı veya pasif hesap verilmişken giriş gönderildiğinde yanıt 200 olur; hata kodu `invalid_login` olur; üç durumda mesaj aynıdır; oturum açılmaz. | TC-AUTH-04, TC-AUTH-05 |
| FR-03 | Oturum açıkken POST ile çıkış istendiğinde oturum silinir ve giriş sayfasına yönlendirilir. GET ile çıkış istendiğinde 405 döner ve oturum sürer. | TC-AUTH-06, TC-AUTH-07, TC-E2E-06 |
| FR-04 | Oturum yokken `/`, `/destek/`, `/yonetim/` adreslerine GET veya POST yapıldığında yanıt `/hesap/giris/?next=<adres>` adresine yönlendirir. | TC-AUTH-08 |
| FR-05 | `next=https://kotu.example/` veya `//kotu.example/giris` ile başarılı giriş yapıldığında kullanıcı `/` adresine gider; `next=/destek/` ile `/destek/` adresine gider. | TC-AUTH-09, TC-AUTH-10 |
| FR-06 | Boş veritabanında `migrate` çalıştığında üç grup oluşur ve izinleri matrisle aynıdır. Senkronizasyon tekrarlandığında değişiklik yapılmaz; elle eklenen/silinen izin bir sonraki senkronizasyonda geri alınır. | TC-ROLE-01..03 |
| FR-07 | Superuser yönetim sitesinde kullanıcıya Destek Personeli grubunu kaydettiğinde kullanıcının rolü Destek Personeli olur. Talep Sahibi `/admin/` açtığında yönetim girişine yönlendirilir. | TC-ROLE-04 |
| FR-08 | Her rol için panel açıldığında rol etiketi ve yalnız o role ait yetkiler görünür; rolsüz kullanıcıda "Rol atanmamış" uyarısı çıkar; çok gruplu kullanıcıda öncelik kuralı uygulanır. | TC-ROLE-05, TC-ROLE-06, TC-E2E-02 |
| FR-09 | Talep Sahibi ve rolsüz kullanıcı `/destek/` ve `/yonetim/` için 403 alır; Destek Personeli `/destek/` 200, `/yonetim/` 403 alır; Yönetici ikisinde 200 alır. Yetkisiz POST da 403 alır. 403 sayfası Türkçedir ve rolü ve adresi gösterir. | TC-ROLE-07..11, TC-E2E-03..05 |
| FR-10 | Menüde Talep Sahibi "Panelim"i, Destek Personeli ek olarak "Destek kuyruğu"nu, Yönetici ek olarak "Yönetim paneli"ni, superuser ek olarak "Yönetim sitesi"ni görür. Hafta 3'ten itibaren talep izni olan her rolde "Talepler", yalnız Yönetici ve superuser'da "Kategoriler" bağlantısı da görünür. | TC-ROLE-12, TC-ROLE-13, TC-E2E-02, TC-E2E-05 |
| FR-11 | DEBUG açıkken komut iki kez çalıştırıldığında tam 3 demo kullanıcı vardır, her biri tek doğru gruptadır. DEBUG kapalıyken veya zayıf parolayla komut hata verir ve kullanıcı oluşturmaz. | TC-SEED-01, TC-SEED-02 |
| NFR-01 | Parola özeti `pbkdf2_sha256$` ile başlar; düz parola saklanmaz; "Kisa1!", "password123" ve "12345678901" reddedilir. | TC-SEC-01 |
| NFR-02 | CSRF denetimi açık istemciyle belirteçsiz giriş/çıkış POST'u 403 alır; belirteçli çıkış 302 alır. | TC-SEC-02 |
| NFR-03 | Giriş yanıtındaki oturum çerezi HttpOnly, SameSite=Lax ve max-age=28800'dür; üretim profilinde Secure bayrakları açıktır. | TC-SEC-03, TC-CFG-03 |
| NFR-04 | Üretim profili eksik anahtar/host veya DEBUG=1 ile başlamaz; `check --deploy --fail-level WARNING` çıkış kodu 0'dır; geçersiz bool/tam sayı ortam değeri hata verir. | TC-CFG-02, TC-CFG-03, TC-CFG-05 |
| NFR-05 | 2026-01-15 09:30 UTC değeri veritabanında 09:30 olarak durur ve şablonda "15.01.2026 12:30" gösterilir. | TC-CFG-01 |
| NFR-06 | Giriş sayfasında `lang="tr"`, "Kullanıcı adı", "Parola", "Giriş yap" bulunur; 404 sayfası Türkçedir. | TC-CFG-04, TC-E2E-01 |
| NFR-07 | 360×740 görünüm alanında giriş ve panelde (Hafta 3'ten itibaren talep listesi ve ayrıntısında) `scrollWidth ≤ clientWidth` olur ve iç kapsayıcı taşması yoktur. | TC-E2E-07, TC-E2E-12 |
| NFR-08 | Yalnız klavyeyle giriş tamamlanır; ilk Tab "İçeriğe geç" bağlantısına gelir; odak çizgisi görünür; ölçülen kontrast oranları ≥ 4.5:1'dir. | TC-E2E-08, TC-E2E-09 |
| NFR-09 | Üretim kodu kapsamı ≥ %80'dir; test koşucusu PASS/FAIL/ERROR/SKIP ve alt test başarısızlığını doğru kaydeder; RTM üretici gereksinim durumlarını doğru hesaplar ve sayar. | TC-QA-01, TC-QA-03, TC-QA-04 |
| NFR-10 | `ruff check .` sıfır bulgu verir. | TC-QA-02 |
| NFR-11 | Temiz sanal ortamda kurulum, migrate ve testler Linux'ta Python 3.12 ve 3.13 ile hatasız tamamlanır; GitHub Actions matrisinde (Ubuntu/Windows × 3.12/3.13) tüm işler yeşil olur; yönetim sitesi özel kullanıcı modeliyle açılır. | TC-INST-01, TC-CFG-06, TC-CI-01 |
| NFR-12 | User modelinde ek kişisel veri alanı yoktur; demo kullanıcılarının adı "Demo" ve e-postası boştur. | TC-INS-01 |
| FR-12 | Talep Sahibi geçerli formu (başlık 5-200 karakter, açıklama, etkin kategori, P1-P4) gönderdiğinde talep `INC-000NNN` numarası, Open durumu, UTC oluşturma zamanı ve talep sahibi olarak kendisiyle kaydedilir ve ayrıntı sayfasına yönlendirilir. Kısa/uzun başlık, boş açıklama, pasif/olmayan kategori veya geçersiz öncelikle kayıt oluşmaz; forma eklenen durum, talep sahibi veya atanan alanı yok sayılır. Rolsüz kullanıcı 403 alır. | TC-TKT-01, TC-TKT-02, TC-TKT-03, TC-TKT-08, TC-E2E-10 |
| FR-13 | Liste durum, öncelik, kategori ve atanan (atanmamış dahil) filtreleriyle daralır; filtreler birlikte uygulanabilir; geçersiz filtre değeri yok sayılır. 30 talepte 1. sayfada 25, 2. sayfada 5 kayıt vardır; en yeni talep önce gelir; sayfa bağlantıları filtreyi korur; aralık dışı sayfa 404 döner. | TC-TKT-04, TC-TKT-05, TC-TKT-06, TC-E2E-10, TC-E2E-12 |
| FR-14 | Talep Sahibi listede yalnız kendi taleplerini görür; başkasının talebinin ayrıntı adresine GET isteği 404 döner ve yanıt var olmayan numarayla aynıdır (başlık ve numara görünmez). Destek Personeli ve Yönetici tüm talepleri görür. Filtre görünürlüğü genişletmez. | TC-TKT-04, TC-TKT-05, TC-TKT-07, TC-TKT-08, TC-E2E-11 |
| FR-15 | Yönetici kategori ekler; aynı ad (Türkçe büyük/küçük harf farkıyla da) ve boş ad reddedilir. Pasifleştirilen kategori yeni talep formunda listelenmez ve doğrudan POST ile seçilemez; mevcut talepler kategorisini korur; kategori silinemez. Durum değişikliği yalnız CSRF belirteçli POST ile yapılır; diğer roller 403 alır. | TC-TKT-02, TC-CAT-01, TC-CAT-02, TC-CAT-03, TC-E2E-13 |
| NFR-16 | `views/` modülleri model yöneticilerine (`.objects`) doğrudan erişmez; `services/` modülleri görünüm, şablon ve HTTP modüllerini içe aktarmaz; `models/` modülleri `services/` ve `views/`'i içe aktarmaz; her görünüm sınıfı oturum veya izin denetimi içerir. | TC-ARCH-01, TC-ARCH-02 |
| FR-16 | Destek Personeli atanmamış talebi üzerine alır; atanmış talebi ikinci bir personel alamaz. Yönetici talebi yalnız Destek Personeli rol grubundaki etkin kullanıcıya atar ve yeniden atar; Talep Sahibi, Yönetici, rolsüz veya pasif kullanıcıya atama reddedilir. Talep Sahibi üzerine alma, atama ve öncelik adreslerine 403 alır; Destek Personeli atamaya 403 alır; adresler yalnız POST kabul eder (GET 405). Kapanmış talepte atama yapılamaz. | TC-ASN-01, TC-ASN-02, TC-ASN-03, TC-ASN-05, TC-ROLE-14, TC-E2E-14, TC-E2E-15 |
| FR-17 | Talep Sahibi kendi talebine, Destek Personeli ve Yönetici tüm taleplere yorum ekler; yorumlar eskiden yeniye, yazan adı ve İstanbul saatiyle gösterilir; HTML kaçışlanır. Boş ve 2.000 karakterden uzun yorum reddedilir. Başkasının talebinin yorum adresine POST 404 döner ve yanıt var olmayan numarayla aynıdır (FR-14). Kapanmış talebe yorum eklenemez; form gösterilmez. | TC-CMT-01, TC-CMT-02, TC-CMT-03, TC-CMT-04, TC-ROLE-14, TC-E2E-14, TC-E2E-15, TC-E2E-16 |
| FR-20 (Hafta 4 bölümü) | Talep oluşturma, üzerine alma, atama ve öncelik değişikliği işlem geçmişine tam bir kez yazılır: aktör, UTC zaman, eski ve yeni değer. Reddedilen işlem kayıt yazmaz. Kayıt değiştirilemez ve silinemez; yönetim sitesinde salt okunurdur. Hafta 4 öncesi taleplere bir oluşturma kaydı eklenir. Durum geçişi kayıtları Hafta 5'te eklenir; değişiklik kararı ve düzeltici faaliyet kayıtları kapsam dışıdır (KRR-18). | TC-AUD-01, TC-AUD-02, TC-AUD-03, TC-ASN-04 |
| AK-03 kararı | Destek Personeli ve Yönetici talebin önceliğini değiştirir; değişiklik eski ve yeni değerle kaydedilir; aynı veya geçersiz öncelik reddedilir; Talep Sahibi öncelik formunu görmez (KRR-17). | TC-ASN-04 |

### 7.2 Sonraki haftalar (özet; ilgili hafta başında ayrıntılandırılacak)

- FR-16, FR-17: Hafta 4'te ayrıntılandırıldı (§7.1).
- FR-18..FR-21: İzin verilen/verilmeyen her geçiş çifti; rol ve atama koşulları; çözüm açıklaması zorunluluğu; her işlem için tek denetim kaydı; kayıtların değiştirilemezliği.
- FR-22..FR-25: Kapsam dışı (gelecek çalışma, KRR-18).
- FR-26..FR-31: Kapsam dışı (gelecek çalışma, KRR-18).
- FR-32..FR-37: Kapsam dışı (gelecek çalışma, KRR-18).

---

## 8. Doğrulama (29148 §9.6.19)

| Yöntem | Kullanım | Örnek |
|---|---|---|
| Test | Otomatik birim, entegrasyon ve sistem (E2E) testleri | TC-AUTH-*, TC-ROLE-*, TC-TKT-*, TC-CAT-*, TC-E2E-* |
| Analiz | Kapsam, statik analiz ve mimari kural denetimi | TC-QA-01, TC-QA-02, TC-ARCH-01, TC-ARCH-02 |
| İnceleme | Kod/şablon incelemesi | TC-INS-01 |
| Gösterim | Haftalık demoda canlı gösterim | Hafta sonu demo (ayrı kayıt) |

Bir gereksinim, eşlendiği tüm TC'ler gerçek koşuda PASS olduğunda "doğrulandı" sayılır. Sonuçlar elle yazılmaz; `tools/build_rtm.py` test çıktılarından üretir. Ayrıntı: [TEST_PLAN.md](TEST_PLAN.md).

## 9. Gereksinim kalitesi denetimi (29148 §5.2.5, §5.2.6)

- **Tek anlamlılık ve ölçülebilirlik:** Belirsiz sıfatlar ("hızlı", "kolay") yerine eşik ve davranış yazıldı (ör. NFR-03: 28.800 sn; NFR-08: 4.5:1).
- **Doğrulanabilirlik:** Hafta 1-3'ün her gereksinimi en az bir TC'ye bağlı; RTM tutarlılık denetimi testsiz aktif gereksinime izin vermiyor.
- **Tekillik:** FR-19 ve FR-30 birden fazla koşul içeriyor; Hafta 5 ve 7 başında alt gereksinimlere bölünecek.
- **Tutarlılık:** Rol matrisi koddan üretildi; SRS §4 ile uygulama aynı kaynaktan geliyor.
- **İzlenebilirlik:** Her gereksinimin kaynağı (PT, DJ-SEC, EKİP) ve mimari bileşeni yazılı.

## 10. Açık konular

| Kimlik | Konu | Karar sahibi |
|---|---|---|
| AK-01 | Resolved → In Progress "yeniden açma" geçişi eklenecek mi? (Proje talimatındaki akışta yok.) | Burak Nigiz / öğretim elemanı |
| AK-02 | Resolved talep, talep sahibi onaylamazsa belirli süre sonra otomatik kapansın mı? | Burak Nigiz |
| AK-03 | Önceliği talep sahibi mi seçecek, destek personeli mi belirleyecek? **Karar (Hafta 4, KRR-17):** Talep sahibi talep açarken önceliği seçer (FR-12); Destek Personeli ve Yönetici sonradan değiştirebilir ve değişiklik işlem geçmişine yazılır (FR-20). **Kapandı.** | Burak Nigiz |
| AK-04 | Yönetici rolü kullanıcı/rol yönetimi yapabilsin mi, yoksa yalnız superuser mı? | Burak Nigiz |
| AK-05 | Ders hangi baskıları bekliyor? ISO 9001:2015 mi 2026 mı, ISO/IEC 25010:2011 mi 2023 mü, ISO/IEC/IEEE 12207:2017 mi 2026 mı? | Öğretim elemanı |
| AK-06 | Grup numarası (ekip tek kişi: Burak Nigiz, 2100002062) | Burak Nigiz |
| AK-07 | Ayrıntılı SDS-07 proje dokümanı elde edilirse bu SRS ile karşılaştırılmalı. | Burak Nigiz |
| AK-08 | Kişisel verilerin korunması (KVKK) için aydınlatma metni ve saklama süresi kapsam içinde mi? | Burak Nigiz / öğretim elemanı |
