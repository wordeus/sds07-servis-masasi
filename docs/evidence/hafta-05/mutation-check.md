# Mutasyon denetimi (Hafta 5)

Amaç: Testlerin gerçek hataları yakalayabildiğini göstermek. Kodun geçici kopyasına bilinçli hata eklendi, tüm Django test takımı koşuldu ve başarısız olan TC'ler kaydedildi. Orijinal kod değiştirilmedi. Betik: `tools/mutation_check.py`.

| Mutasyon | Dosya | Eklenen hata | Koşulan test | Başarısız olan TC'ler | Sonuç |
|---|---|---|---|---|---|
| M1_requester_gets_support_perm | `servicedesk/roles.py` | Talep Sahibi rolüne destek kuyruğu izni verildi (yetki yükseltme) | 69 | TC-ROLE-07, TC-ROLE-10, TC-ROLE-12 | Yakalandı |
| M2_manager_panel_no_perm_check | `servicedesk/views/dashboard.py` | Yönetim panelinde izin denetimi yerine yalnız oturum denetimi | 69 | TC-ROLE-07, TC-ROLE-08, TC-ROLE-10, TC-ROLE-11 | Yakalandı |
| M3_session_two_weeks | `config/settings.py` | Oturum süresi 8 saatten 2 haftaya çıkarıldı | 69 | TC-SEC-03 | Yakalandı |
| M4_store_naive_local_time | `config/settings.py` | USE_TZ=False: zamanlar saat dilimsiz yerel saatle saklanır | 69 | TC-AUD-01, TC-CFG-01, TC-TKT-01, TC-TKT-08, TC-WF-06 | Yakalandı |
| M5_requester_sees_all_tickets | `servicedesk/services/tickets.py` | Kayıt bazlı erişim kuralı kaldırıldı: Talep Sahibi tüm talepleri görür (IDOR) | 69 | TC-CMT-03, TC-TKT-04, TC-TKT-05, TC-TKT-07, TC-WF-04, TC-WF-06 | Yakalandı |
| M6_detail_bypasses_policy | `servicedesk/views/tickets.py` | Ayrıntı görünümü politika fonksiyonunu atlayıp modelden doğrudan sorgular | 69 | TC-ARCH-01, TC-TKT-07, TC-WF-06 | Yakalandı |
| M7_inactive_category_selectable | `servicedesk/services/tickets.py` | Pasif kategori yeni talep formunda seçilebilir | 69 | TC-CAT-02 | Yakalandı |
| M8_turkish_duplicate_check_removed | `servicedesk/models/ticket.py` | Kategori adı tekilliğinde Türkçe büyük/küçük harf kuralı kaldırıldı | 69 | TC-CAT-01 | Yakalandı |
| M9_comment_visibility_check_removed | `servicedesk/services/comments.py` | Yorum servisi talebin görünürlüğünü denetlemiyor (başkasının talebine yorum) | 69 | TC-CMT-03 | Yakalandı |
| M10_closed_ticket_comment_allowed | `servicedesk/services/comments.py` | Kapanmış talebe yorum eklenebiliyor | 69 | TC-CMT-04 | Yakalandı |
| M11_assign_to_any_user | `servicedesk/services/assignment.py` | Talep Destek Personeli olmayan kullanıcıya atanabiliyor | 69 | TC-ASN-02 | Yakalandı |
| M12_priority_change_not_audited | `servicedesk/services/assignment.py` | Öncelik değişikliği işlem geçmişine yazılmıyor | 69 | TC-ASN-04, TC-AUD-01 | Yakalandı |
| M13_event_record_mutable | `servicedesk/models/activity.py` | Kaydedilmiş işlem geçmişi kaydı değiştirilebiliyor | 69 | TC-AUD-02 | Yakalandı |
| M14_transition_skip_allowed | `servicedesk/services/workflow.py` | Durum makinesi atlamaya ve geri dönmeye izin veriyor | 69 | TC-WF-05 | Yakalandı |
| M15_unassigned_agent_can_progress | `servicedesk/services/workflow.py` | Talebe atanmamış destek personeli talebi ilerletebiliyor | 69 | TC-WF-03 | Yakalandı |
| M16_resolution_not_required | `servicedesk/services/workflow.py` | Çözüldü geçişinde çözüm açıklaması zorunlu değil | 69 | TC-WF-02 | Yakalandı |
| M17_status_change_not_audited | `servicedesk/services/workflow.py` | Durum geçişi işlem geçmişine yazılmıyor | 69 | TC-WF-01, TC-WF-02, TC-WF-04, TC-WF-05, TC-WF-06 | Yakalandı |
| M18_requester_closes_any_ticket | `servicedesk/services/workflow.py` | Kapatma izni olan herkes başkasının talebini kapatabiliyor | 69 | TC-WF-04 | Yakalandı |

Koşu başlangıcı (UTC): 2026-11-26T08:27:46Z. Mutasyon puanı: 18/18 yakalandı.
