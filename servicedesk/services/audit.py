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
