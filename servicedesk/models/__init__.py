"""Veri modeli paketi (NFR-16).

Modüller sorumluluğa göre ayrılır: `user.py` (MOD-AUTH, MOD-ROLE), `ticket.py`
(MOD-TICKET), `activity.py` (yorumlar ve işlem geçmişi, MOD-AUDIT). Django modelleri
bu paketten içe aktarır; uygulama etiketi ve migration geçmişi değişmez.
"""

from .activity import Comment, ImmutableEventError, TicketEvent
from .ticket import Category, Ticket
from .user import User

__all__ = ["Category", "Comment", "ImmutableEventError", "Ticket", "TicketEvent", "User"]
