"""MOD-AUDIT iş kuralları: işlem geçmişi (FR-20, Hafta 4).

İşlem geçmişine yalnız bu modülden yazılır. Kayıt, işlemi yapan servis fonksiyonuyla
aynı veritabanı işlemi (transaction) içinde oluşturulur; işlem geri alınırsa kayıt da
oluşmaz, kayıt oluşmazsa işlem de geri alınır.
"""

from __future__ import annotations

from ..models import Ticket, TicketEvent


def record_event(ticket: Ticket, actor, kind: str, *, old_value: str = "", new_value: str = "") -> TicketEvent:
    """Değiştirilemez bir işlem geçmişi kaydı ekler (aktör, UTC zaman, eski ve yeni değer)."""
    return TicketEvent.objects.create(
        ticket=ticket, actor=actor, kind=kind, old_value=old_value or "", new_value=new_value or ""
    )


def _display(kind: str, value: str) -> str:
    """Kayıttaki ham değeri arayüz etiketine çevirir (durum ve öncelik kodları)."""
    if not value:
        return ""
    if kind == TicketEvent.Kind.STATUS_CHANGED and value in Ticket.Status.values:
        return Ticket.Status(value).label
    if kind in (TicketEvent.Kind.PRIORITY_CHANGED, TicketEvent.Kind.CREATED) and value in Ticket.Priority.values:
        return Ticket.Priority(value).label
    return value


def history_for(ticket: Ticket) -> list[dict]:
    """Talebin işlem geçmişi, kronolojik sırayla ve arayüz etiketleriyle (FR-21).

    Kayıt bazlı erişim çağıran görünümde sağlanır: talep `visible_tickets_for` kümesinden gelir.
    """
    events = TicketEvent.objects.filter(ticket=ticket).select_related("actor").order_by("created_at", "pk")
    return [
        {
            "kind": event.kind,
            "label": event.get_kind_display(),
            "actor": event.actor.get_full_name() or event.actor.username,
            "old": _display(event.kind, event.old_value),
            "new": _display(event.kind, event.new_value),
            "created_at": event.created_at,
        }
        for event in events
    ]
