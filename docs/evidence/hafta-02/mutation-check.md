# Mutasyon denetimi (Hafta 2)

Amaç: Testlerin gerçek hataları yakalayabildiğini göstermek. Kodun geçici kopyasına bilinçli hata eklendi, tüm Django test takımı koşuldu ve başarısız olan TC'ler kaydedildi. Orijinal kod değiştirilmedi. Betik: `tools/mutation_check.py`.

| Mutasyon | Dosya | Eklenen hata | Koşulan test | Başarısız olan TC'ler | Sonuç |
|---|---|---|---|---|---|
| M1_requester_gets_support_perm | `servicedesk/roles.py` | Talep Sahibi rolüne destek kuyruğu izni verildi (yetki yükseltme) | 35 | TC-ROLE-07, TC-ROLE-10, TC-ROLE-12 | Yakalandı |
| M2_manager_panel_no_perm_check | `servicedesk/views.py` | Yönetim panelinde izin denetimi yerine yalnız oturum denetimi | 35 | TC-ROLE-07, TC-ROLE-08, TC-ROLE-10, TC-ROLE-11 | Yakalandı |
| M3_session_two_weeks | `config/settings.py` | Oturum süresi 8 saatten 2 haftaya çıkarıldı | 35 | TC-SEC-03 | Yakalandı |
| M4_store_naive_local_time | `config/settings.py` | USE_TZ=False: zamanlar saat dilimsiz yerel saatle saklanır | 35 | TC-CFG-01 | Yakalandı |

Koşu başlangıcı (UTC): 2026-10-30T06:40:45Z. Mutasyon puanı: 4/4 yakalandı.
