"""Görünüm paketi (MOD-UI, MOD-TICKET).

Görünümler HTTP isteğini karşılar, yetkiyi denetler ve iş kuralları için services/
katmanını çağırır; modellere doğrudan sorgu yazmaz (NFR-16, TC-ARCH-01).
"""

from .categories import CategoryListView, CategoryToggleView
from .dashboard import DashboardView, ManagerPanelView, SupportWorkspaceView
from .ticket_actions import TicketAssignView, TicketCommentView, TicketPriorityView, TicketTakeView
from .tickets import TicketCreateView, TicketDetailView, TicketListView

__all__ = [
    "CategoryListView",
    "CategoryToggleView",
    "DashboardView",
    "ManagerPanelView",
    "SupportWorkspaceView",
    "TicketAssignView",
    "TicketCommentView",
    "TicketCreateView",
    "TicketDetailView",
    "TicketListView",
    "TicketPriorityView",
    "TicketTakeView",
]
