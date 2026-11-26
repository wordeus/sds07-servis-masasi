"""MOD-TICKET iş kuralları: talep durum makinesi (FR-18, FR-19; Hafta 5).

İzin verilen geçişler yalnız şunlardır (tek yönlü, atlama yok):

    Open → In Progress → Resolved → Closed

* Open → In Progress ve In Progress → Resolved: talebe atanmış Destek Personeli
  (`progress_ticket`) veya Yönetici (`progress_any_ticket`). Talep atanmış olmalıdır.
* In Progress → Resolved geçişinde çözüm açıklaması zorunludur.
* Resolved → Closed: talep sahibi kendi talebini onaylayarak (`close_ticket`) veya Yönetici.
* Diğer her geçiş (atlama, geri dönme, kapanmış talebin değiştirilmesi) sunucuda reddedilir.
  Resolved → In Progress "yeniden açma" geçişi yoktur (AK-01, KRR-19).

Her başarılı geçiş işlem geçmişine eski ve yeni durumla yazılır (FR-20). İzin bu
fonksiyonun içinde de denetlenir; görünümü atlayan bir çağrı kuralı delemez.
"""

from __future__ import annotations

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from ..models import Ticket, TicketEvent
from ..roles import PERM_CLOSE_TICKET, PERM_PROGRESS_ANY_TICKET, PERM_PROGRESS_TICKET
from .audit import record_event

S = Ticket.Status
NEXT_STATUS = {S.OPEN: S.IN_PROGRESS, S.IN_PROGRESS: S.RESOLVED, S.RESOLVED: S.CLOSED}
RESOLUTION_MAX_LENGTH = 2000


def _may_progress(user, ticket: Ticket) -> bool:
    if user.has_perm(PERM_PROGRESS_ANY_TICKET):
        return True
    return user.has_perm(PERM_PROGRESS_TICKET) and ticket.assignee_id == user.pk


def _may_close(user, ticket: Ticket) -> bool:
    if user.has_perm(PERM_PROGRESS_ANY_TICKET):
        return True
    return user.has_perm(PERM_CLOSE_TICKET) and ticket.requester_id == user.pk


def is_allowed(user, ticket: Ticket, target: str) -> bool:
    """Kullanıcı talebi `target` durumuna taşıyabilir mi? (Arayüzde düğmeyi göstermek için.)"""
    if NEXT_STATUS.get(ticket.status) != target:
        return False
    if target == S.CLOSED:
        return _may_close(user, ticket)
    return _may_progress(user, ticket) and ticket.assignee_id is not None


def available_transition(user, ticket: Ticket) -> str | None:
    """Kullanıcının bu talepte yapabileceği tek geçişin hedef durumu (yoksa None)."""
    target = NEXT_STATUS.get(ticket.status)
    return target if target and is_allowed(user, ticket, target) else None


def change_status(ticket: Ticket, actor, target: str, *, resolution: str = "") -> Ticket:
    """Talebi bir sonraki duruma taşır. Tanımsız geçiş ValidationError, yetkisiz geçiş PermissionDenied."""
    if target not in S.values:
        raise ValidationError("Geçersiz durum.")
    with transaction.atomic():
        current = Ticket.objects.select_for_update().get(pk=ticket.pk)
        if NEXT_STATUS.get(current.status) != target:
            raise ValidationError(
                f"{S(current.status).label} durumundaki talep {S(target).label} durumuna geçirilemez."
            )
        if target == S.CLOSED:
            if not _may_close(actor, current):
                raise PermissionDenied
        else:
            if not _may_progress(actor, current):
                raise PermissionDenied
            if current.assignee_id is None:
                raise ValidationError("Talep önce bir destek personeline atanmalıdır.")
        fields = ["status", "updated_at"]
        if target == S.RESOLVED:
            resolution = (resolution or "").strip()
            if not resolution:
                raise ValidationError({"resolution": "Çözüm açıklaması zorunludur."})
            if len(resolution) > RESOLUTION_MAX_LENGTH:
                raise ValidationError(
                    {"resolution": f"Çözüm açıklaması en fazla {RESOLUTION_MAX_LENGTH} karakter olabilir."}
                )
            current.resolution = resolution
            fields.append("resolution")
        old = current.status
        current.status = target
        current.save(update_fields=fields)
        record_event(current, actor, TicketEvent.Kind.STATUS_CHANGED, old_value=old, new_value=target)
    return current
