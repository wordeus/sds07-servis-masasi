# Teslim öncesi kontroller (30.10.2026)

Hafta 1-3 paketleri GitHub'a gönderilmeden önce yapılan iki kontrolün gerçek çıktılarıdır. Her iki kontrol de bir hata buldu; hatalar düzeltildi ve düzeltme aynı kontrolle yeniden denetlendi. Kod ve testler değişmedi; yalnız `.gitignore` ve `.github/workflows/ci.yml` değişti. Bu yüzden haftaların test ve ölçüm kanıtları geçerliliğini korur.

| Dosya | İçerik | Kayıt |
|---|---|---|
| `gitignore-denetimi.txt` | Her paket boş bir git deposuna kopyalanıp `git status --porcelain --ignored` ile denetlendi. Düzeltme öncesinde `docs/reports/` (raporlar ve içerik dosyaları) ile `docs/evidence/` altındaki kurulum günlükleri yok sayılıyordu, yani depoya girmeyecekti. Düzeltme sonrasında `docs/` altında yok sayılan dosya 0. | RSK-24 |
| `windows-kodlama-simulasyonu.txt` | CI'daki komutlar, Windows'un yönlendirilmiş çıktı kodlaması (cp1252) taklit edilerek koşuldu. Hafta 2-3'te `manage.py test -v 2`, rol eşitlemesinin "oluşturuldu" çıktısında; üç haftada da `tools/build_rtm.py` "RTM yazıldı" çıktısında `UnicodeEncodeError` ile durdu. UTF-8 çıktıyla aynı komutlar geçti. | RSK-25 |
| `win_encoding_sim.sh` | Simülasyonda kullanılan betiğin kendisi (bulut çalışma alanındaki yollarla, olduğu gibi). | RSK-25 |

## Simülasyonun sınırları

- Linux'ta Windows kod sayfası yalnız standart çıktı için taklit edilebildi (`PYTHONIOENCODING=cp1252`). Dosya okuma/yazma varsayılan kodlaması taklit edilemedi. Projedeki dosya işlemleri zaten açıkça `encoding="utf-8"` kullanıyor.
- Hafta 1 test adımındaki 3 hata (TC-CFG-02 alt testlerinde `UnicodeDecodeError`) simülasyonun kendi yan etkisidir. Alt süreç cp1252 yazıyor, üst süreç Linux'ta UTF-8 okuyor. Windows'ta iki süreç aynı kod sayfasını kullandığı için bu hata beklenmez. Bu adım sonuç olarak sayılmadı.
- Düzeltme `PYTHONUTF8: "1"` ortam değişkenidir (Python UTF-8 kipi). Windows'taki gerçek etkisi bu ortamda denenemedi. Doğrulaması GitHub Actions'daki ilk Windows koşusudur (TC-CI-01). O koşuya kadar RSK-25 "Azaltıldı" durumunda kalır.
- Etkileşimli PowerShell penceresinde sorun oluşmaz, çünkü Python konsola UTF-8 yazar. Sorun yalnız çıktı dosyaya veya başka bir programa yönlendirildiğinde (CI günlüğü, `> kayit.txt`, `Tee-Object`) ortaya çıkar.
- CI eşdeğeri koşuda RTM'ye yalnız birim test sonuçları verildi (CI'daki gibi). Bu yüzden oradaki gereksinim sayıları resmî RTM'den farklıdır. Resmî RTM, E2E ve elle yapılan kontrollerin sonuçlarını da içerir.

## Sonuç

Düzeltme GitHub Actions'ta doğrulandı: Hafta 1 ve Hafta 2 commit'lerinin GitHub Actions koşularında windows-latest işleri Python 3.12 ve 3.13 ile başarılı oldu (02.11.2026; koşu #1, commit 29f962c; koşu #3, commit 6dd3dc9). Bu yüzden RSK-25 kapandı. Koşu kayıtları: `../../hafta-01/ci-github-actions-2026-11-02.json`, `../../hafta-02/ci-github-actions-2026-11-02.json`.
