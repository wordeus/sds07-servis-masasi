"""Veri modeli paketi (NFR-16).

Modüller sorumluluğa göre ayrılır: `user.py` (MOD-AUTH, MOD-ROLE), `ticket.py`
(MOD-TICKET). Django modelleri bu paketten içe aktarır; uygulama etiketi ve
migration geçmişi değişmez.
"""

from .ticket import Category, Ticket
from .user import User

__all__ = ["Category", "Ticket", "User"]
