"""MOD-TICKET iş kuralları: yorumlar (FR-17, Hafta 4).

Kurallar:
* Yorum yetkisi (`add_comment`) olan kullanıcı, görebildiği talebe yorum ekler: talep
  sahibi kendi talebine, Destek Personeli ve Yönetici tüm taleplere. Hangi talebin
  görüleceğini `visible_tickets_for` belirler; görünüm talebi bu kümeden alır, böylece
  başkasının talebinin yorum adresi 404 döner (FR-14).
* Kapanmış (Closed) talebe yorum eklenemez.
* Yorum boş olamaz ve en fazla 2.000 karakterdir.
"""

from __future__ import annotations

from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import QuerySet

from ..models import Comment, Ticket
from ..roles import PERM_ADD_COMMENT
from .tickets import visible_tickets_for


def can_comment(user, ticket: Ticket) -> bool:
    return user.has_perm(PERM_ADD_COMMENT) and ticket.status != Ticket.Status.CLOSED


def add_comment(ticket: Ticket, author, body: str) -> Comment:
    if not author.has_perm(PERM_ADD_COMMENT) or not visible_tickets_for(author).filter(pk=ticket.pk).exists():
        raise PermissionDenied
    if ticket.status == Ticket.Status.CLOSED:
        raise ValidationError("Kapanmış talebe yorum eklenemez.")
    comment = Comment(ticket=ticket, author=author, body=body.strip())
    comment.full_clean()
    comment.save()
    return comment


def comments_for(ticket: Ticket) -> QuerySet[Comment]:
    """Talebin yorumları, eskiden yeniye."""
    return Comment.objects.filter(ticket=ticket).select_related("author").order_by("created_at", "pk")
