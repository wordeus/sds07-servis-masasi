"""MOD-TICKET iş kuralları: üzerine alma, atama ve öncelik değişikliği (FR-16, AK-03; Hafta 4).

Kurallar:
* Destek Personeli (ve Yönetici) atanmamış bir talebi kendi üzerine alır.
* Yönetici talebi yalnız Destek Personeli rol grubundaki etkin bir kullanıcıya atar.
* Destek Personeli ve Yönetici talebin önceliğini değiştirir (KRR-13'ün yerine KRR-17).
* Kapanmış (Closed) talepte atama ve öncelik değiştirilemez.
* Her başarılı işlem işlem geçmişine eski ve yeni değerle yazılır (FR-20).

İzin denetimi bu fonksiyonların içinde de yapılır; görünüm denetimini atlayan bir çağrı
(ör. yönetim komutu veya yeni bir görünüm) kuralı delemez.
"""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import QuerySet

from ..models import Ticket, TicketEvent
from ..roles import AGENT, PERM_ASSIGN_TICKET, PERM_CHANGE_PRIORITY, PERM_TAKE_TICKET
from .audit import record_event


def display_name(user) -> str:
    return (user.get_full_name() or user.username) if user else ""


def agents() -> QuerySet:
    """Atanabilir kullanıcılar: Destek Personeli rol grubundaki etkin kullanıcılar (FR-16)."""
    return (
        get_user_model()
        .objects.filter(groups__name=AGENT.group_name, is_active=True)
        .distinct()
        .order_by("first_name", "last_name", "username")
    )


def _locked(ticket: Ticket) -> Ticket:
    """Talebi işlem süresince kilitleyerek yeniden okur (eşzamanlı üzerine alma)."""
    return Ticket.objects.select_for_update().get(pk=ticket.pk)


def _ensure_not_closed(ticket: Ticket) -> None:
    if ticket.status == Ticket.Status.CLOSED:
        raise ValidationError("Kapanmış talepte bu işlem yapılamaz.")


def can_take(user, ticket: Ticket) -> bool:
    return user.has_perm(PERM_TAKE_TICKET) and ticket.assignee_id is None and ticket.status != Ticket.Status.CLOSED


def take_ticket(ticket: Ticket, user) -> Ticket:
    """Atanmamış talebi kullanıcının üzerine alır (FR-16)."""
    if not user.has_perm(PERM_TAKE_TICKET):
        raise PermissionDenied
    with transaction.atomic():
        current = _locked(ticket)
        _ensure_not_closed(current)
        if current.assignee_id is not None:
            raise ValidationError("Bu talep zaten bir destek personeline atanmış.")
        current.assignee = user
        current.save(update_fields=["assignee", "updated_at"])
        record_event(current, user, TicketEvent.Kind.ASSIGNED, new_value=display_name(user))
    return current


def assign_ticket(ticket: Ticket, actor, assignee) -> Ticket:
    """Talebi Destek Personeli rolündeki bir kullanıcıya atar (FR-16; yalnız Yönetici)."""
    if not actor.has_perm(PERM_ASSIGN_TICKET):
        raise PermissionDenied
    if assignee is None or not agents().filter(pk=assignee.pk).exists():
        raise ValidationError({"assignee": "Talep yalnız Destek Personeli rolündeki bir kullanıcıya atanabilir."})
    with transaction.atomic():
        current = _locked(ticket)
        _ensure_not_closed(current)
        if current.assignee_id == assignee.pk:
            raise ValidationError({"assignee": "Talep zaten bu kişiye atanmış."})
        old = display_name(current.assignee)
        current.assignee = assignee
        current.save(update_fields=["assignee", "updated_at"])
        record_event(current, actor, TicketEvent.Kind.ASSIGNED, old_value=old, new_value=display_name(assignee))
    return current


def change_priority(ticket: Ticket, actor, priority: str) -> Ticket:
    """Talebin önceliğini değiştirir (AK-03; Destek Personeli ve Yönetici)."""
    if not actor.has_perm(PERM_CHANGE_PRIORITY):
        raise PermissionDenied
    if priority not in Ticket.Priority.values:
        raise ValidationError({"priority": "Geçersiz öncelik."})
    with transaction.atomic():
        current = _locked(ticket)
        _ensure_not_closed(current)
        if current.priority == priority:
            raise ValidationError({"priority": "Talep zaten bu öncelikte."})
        old = current.priority
        current.priority = priority
        current.save(update_fields=["priority", "updated_at"])
        record_event(current, actor, TicketEvent.Kind.PRIORITY_CHANGED, old_value=old, new_value=priority)
    return current
