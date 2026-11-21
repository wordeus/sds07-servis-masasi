# Geliştirme ve belge prosedürleri

| Alan | Değer |
|---|---|
| Doküman kimliği | SDS07-PRC |
| Sürüm | 0.3 |
| Tarih | 30.10.2026 |
| Hazırlayan | Burak Nigiz (2100002062) |
| İlişkili | ISO 9001:2026 7.5.2 ve 7.5.3 (dokümante bilginin oluşturulması ve kontrolü); ISO/IEC/IEEE 12207:2026 6.3.5 ve 6.3.8 |

## PRC-01 Sürüm kontrolü ve dal stratejisi

- Ana dal `main` her zaman çalışır durumdadır; CI yeşil olmadan birleştirme yapılmaz.
- Her iş için kısa ömürlü dal açılır: `feat/<kısa-ad>`, `fix/<kısa-ad>`, `docs/<kısa-ad>`.
- Değişiklik Pull Request ile gelir. Proje tek kişilik olduğundan PR'ı açan kişi PRC-03 kontrol listesini kendisi uygular ve CI yeşil olmadan birleştirmez. Bağımsız inceleme yerine öğretim elemanı geri bildirimi kullanılır (RSK-03).

## PRC-02 Commit mesajları (Conventional Commits)

`<tür>(<kapsam>): <özet>`. Türler: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`. Gereksinim veya test kimliği gövdede yazılır.

Örnek: `feat(role): rol gruplarını post_migrate ile eşitle` ve gövdede `FR-06, TC-ROLE-01..03`.

## PRC-03 Pull Request inceleme kontrol listesi

- [ ] Değişiklik bir gereksinime (FR/NFR) bağlı ve `requirements.csv` güncel
- [ ] Yeni veya değişen davranış için TC kimlikli test var; `tests.csv` güncel
- [ ] Yetki gerektiren her yeni görünümde sunucu tarafı denetim ve doğrudan adres/POST testi var
- [ ] Zaman alanları UTC; arayüzde İstanbul saati
- [ ] `ruff`, `check`, `makemigrations --check`, testler ve kapsam CI'da yeşil
- [ ] SRS/SDD/RTM/CHANGELOG gerekiyorsa güncellendi
- [ ] Gizli bilgi (parola, anahtar) koda veya belgeye girmedi

## PRC-04 Tamamlanma tanımı (hafta)

[TEST_PLAN.md §4](TEST_PLAN.md) çıkış ölçütleri sağlanır, haftanın kanıtları `docs/evidence/hafta-NN/` altına yazılır, RTM `--week N --strict` ile üretilir, haftalık ilerleme raporu hazırlanır ve `docs/PROJECT_STATE.md` güncellenir.

## PRC-05 Belge kontrolü

- Her belgenin başında kimlik, sürüm, tarih, durum, hazırlayan ve onaylayan alanları bulunur.
- Belgeler kodla aynı depoda tutulur; değişiklik geçmişi Git'tedir. Belge içi revizyon tablosu sürüm atlamalarında güncellenir.
- `docs/RTM.md` ve `docs/TEST_RESULTS.md` elle düzenlenmez; `tools/build_rtm.py` ile üretilir.
- Kanıtlar `docs/evidence/hafta-NN/` altında saklanır ve sonradan değiştirilmez. Yeni koşu yeni dosyadır. Önceki haftaların kanıt klasörleri sonraki paketlerde olduğu gibi korunur.
- Taslaklar "taslak" durumunda kalır; Burak Nigiz okuyup onayladıktan sonra "onaylandı" yapılır.

## PRC-06 Gerçek kanıt kuralı

- Koşulmayan test **NOT RUN**, yapılmayan ölçüm **ÖLÇÜLMEDİ** yazılır.
- Commit kimliği, PR numarası, çalışma saati ve katkı oranı yalnız gerçek kayıttan yazılır.
- Projedeki her kod ve belge, sunumda ve vizede açıklanabilecek düzeyde anlaşılır tutulur.

## PRC-07 Rol-izin matrisinde değişiklik

1. `servicedesk/roles.py` içinde `ROLE_PERMISSIONS` ve gerekirse `CAPABILITIES` güncellenir.
2. SRS §4 tablosu koddan yeniden üretilir.
3. `python manage.py migrate` çalıştırılır (gruplar otomatik eşitlenir).
4. TC-ROLE testleri güncellenir; doğrudan adres ve POST testleri eklenir.

Yönetim sitesinden gruplara elle izin eklemek kalıcı değildir; bir sonraki `migrate` matrise geri döndürür.

## PRC-08 Tarayıcı (E2E) testlerinin koşulması

- E2E testleri yalnız `tools/run_e2e.sh` ile koşulur. Betik koşudan önce portun boş olduğunu, koşudan sonra sunucunun kapandığını denetler; eski bir sunucuya karşı yanlış PASS alınmasını önler (RSK-20).
- Sunucu `DJANGO_DEBUG=0` ile çalışır; böylece hata sayfaları üretimdeki gibi görünür (RSK-23, KRR-15).
- Gezinme başlatan her tıklama `page.expect_navigation()` içinde yapılır; aksi hâlde sonraki adım isteği iptal edebilir (RSK-22).
- Her koşu geçici veritabanı ve rastgele demo parolasıyla yapılır; parola hiçbir dosyaya yazılmaz.
- Ekran görüntüleri ilgili haftanın kanıt klasörüne yazılır ve incelenir; testin geçmesi tek başına yeterli sayılmaz (RSK-19).

## PRC-09 Yeni ekran veya işlem eklerken (Hafta 3'ten itibaren)

1. İş kuralı `servicedesk/services/` içinde bir fonksiyon olarak yazılır; görünüm yalnız bu fonksiyonu çağırır (`.objects` görünümde kullanılmaz).
2. Kayıt okuyan her görünümün sorgu kümesi `visible_tickets_for` gibi bir politika fonksiyonundan gelir; başka kullanıcının kaydı için doğrudan adres testi yazılır (404 beklenir).
3. Görünüm sınıfı `LoginRequiredMixin` veya `PermissionRequiredMixin` içerir; gerekiyorsa izin `ROLE_PERMISSIONS`'a eklenir (PRC-07).
4. Durum değiştiren işlem yalnız POST ve CSRF belirteciyle yapılır; GET için 405 testi yazılır.
5. TC-ARCH-01 ve TC-ARCH-02 kuralı otomatik denetler; mutasyon denetimine yeni kural için bir mutasyon eklenir (`tools/mutation_check.py`).
