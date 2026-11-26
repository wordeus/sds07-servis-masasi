"""FR-20: Hafta 4'ten önce açılmış talepler için "Talep oluşturuldu" kaydı (Hafta 4).

İşlem geçmişi Hafta 4'te eklendi. Daha önce açılmış her talebin geçmişi de oluşturmayla
başlasın diye, oluşturma kaydı olmayan talebe bir CREATED kaydı eklenir: aktör talep
sahibi, yeni değer talebin önceliği. Kaydın zamanı migration'ın çalıştığı andır; talebin
gerçek oluşturma zamanı talep kaydında (`created_at`) durur.

Tekrar çalıştırılabilir; geri alma işlemi kayıt silmez (işlem geçmişi yalnız eklenir).
"""

from django.db import migrations


def add_created_events(apps, schema_editor):
    ticket_model = apps.get_model("servicedesk", "Ticket")
    event_model = apps.get_model("servicedesk", "TicketEvent")
    db = schema_editor.connection.alias
    missing = ticket_model.objects.using(db).exclude(events__kind="CREATED").order_by("pk")
    event_model.objects.using(db).bulk_create(
        event_model(ticket_id=t.pk, actor_id=t.requester_id, kind="CREATED", new_value=t.priority) for t in missing
    )


class Migration(migrations.Migration):
    dependencies = [
        ("servicedesk", "0005_comment_ticketevent_permissions"),
    ]

    operations = [
        migrations.RunPython(add_created_events, migrations.RunPython.noop),
    ]
