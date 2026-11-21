"""MOD-TICKET iş kuralları: kayıt bazlı erişim, talep oluşturma, filtreleme, kategoriler.

Erişim politikası (FR-14, KRR-07):
* `view_all_tickets` izni olan (Destek Personeli, Yönetici, sistem yöneticisi) tüm talepleri görür.
* Yalnız `view_ticket` izni olan (Talep Sahibi) yalnız kendi açtığı talepleri görür.
* İzni olmayan hiçbir talep görmez.

Tüm liste ve ayrıntı sorguları `visible_tickets_for` üzerinden yapılır. Başkasına ait
bir talebin numarası bilinse bile kayıt bu sorgu kümesinde yer almadığı için ayrıntı
görünümü 404 döndürür; kaydın var olup olmadığı açığa çıkmaz.
"""

from __future__ import annotations

from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Count, Q, QuerySet

from ..models import Category, Ticket
from ..roles import AGENT, PERM_VIEW_ALL_TICKETS, PERM_VIEW_TICKET

UNASSIGNED = "none"  # Atanan filtresinde "atanmamış" seçeneğinin değeri


def visible_tickets_for(user) -> QuerySet[Ticket]:
    """Kullanıcının görebileceği talepler (kayıt bazlı erişim politikası)."""
    tickets = Ticket.objects.select_related("category", "requester", "assignee")
    if not getattr(user, "is_authenticated", False):
        return tickets.none()
    if user.has_perm(PERM_VIEW_ALL_TICKETS):
        return tickets
    if user.has_perm(PERM_VIEW_TICKET):
        return tickets.filter(requester=user)
    return tickets.none()


@dataclass(frozen=True)
class TicketFilters:
    """Liste filtresi (FR-13). Boş alan o ölçüte göre filtrelenmez demektir."""

    status: str = ""
    priority: str = ""
    category: Category | None = None
    assignee: str = ""  # "" | "none" | kullanıcı kimliği (metin)


def filter_tickets(tickets: QuerySet[Ticket], filters: TicketFilters) -> QuerySet[Ticket]:
    """Görünür talepleri filtreler. Filtre, görünürlük kümesini daraltır; asla genişletmez."""
    if filters.status:
        tickets = tickets.filter(status=filters.status)
    if filters.priority:
        tickets = tickets.filter(priority=filters.priority)
    if filters.category is not None:
        tickets = tickets.filter(category=filters.category)
    if filters.assignee == UNASSIGNED:
        tickets = tickets.filter(assignee__isnull=True)
    elif filters.assignee:
        tickets = tickets.filter(assignee_id=filters.assignee)
    return tickets


def open_queue(user) -> QuerySet[Ticket]:
    """Destek kuyruğu: görünür ve durumu Açık olan talepler, en eskisi önce."""
    return visible_tickets_for(user).filter(status=Ticket.Status.OPEN).order_by("created_at", "pk")


def status_counts(user) -> list[dict]:
    """Kullanıcının görebildiği taleplerin duruma göre sayıları, süreç sırasıyla (panel özeti)."""
    rows = visible_tickets_for(user).order_by().values("status").annotate(total=Count("pk"))
    totals = {row["status"]: row["total"] for row in rows}
    return [{"code": s.value, "label": s.label, "count": totals.get(s.value, 0)} for s in Ticket.Status]


def create_ticket(*, requester, title: str, description: str, category: Category, priority: str) -> Ticket:
    """Yeni talep (FR-12). Durum her zaman Open; numara kayıttan sonra oluşur."""
    if not category.is_active:
        raise ValidationError({"category": "Pasif kategoriyle talep açılamaz."})
    ticket = Ticket(requester=requester, title=title, description=description, category=category, priority=priority)
    ticket.full_clean()
    ticket.save()
    return ticket


def active_categories() -> QuerySet[Category]:
    """Yeni talep formunda listelenen kategoriler (FR-15: pasif kategori listelenmez)."""
    return Category.objects.filter(is_active=True)


def all_categories() -> QuerySet[Category]:
    """Kategori yönetimi ve filtre listesi; her kategorinin talep sayısıyla."""
    return Category.objects.annotate(ticket_count=Count("tickets"))


def create_category(*, name: str, description: str = "") -> Category:
    """Yeni kategori (FR-15). Aynı ad kuralı modeldedir (Category.clean); yönetim sitesi de aynı kuralı uygular."""
    category = Category(name=" ".join(name.split()), description=description.strip())
    category.full_clean()
    category.save()
    return category


def get_category(pk: int) -> Category | None:
    return Category.objects.filter(pk=pk).first()


def set_category_active(category: Category, active: bool) -> Category:
    """Kategoriyi pasifleştirir veya yeniden etkinleştirir. Kategori silinmez."""
    if category.is_active != active:
        category.is_active = active
        category.save(update_fields=["is_active"])
    return category


def assignee_choices() -> list[tuple[str, str]]:
    """Atanan filtresi seçenekleri: atanmamış + Destek Personeli rolündeki kullanıcılar."""
    agents = (
        get_user_model()
        .objects.filter(Q(groups__name=AGENT.group_name) | Q(assigned_tickets__isnull=False))
        .distinct()
        .order_by("first_name", "last_name", "username")
    )
    return [(UNASSIGNED, "Atanmamış")] + [(str(u.pk), u.get_full_name() or u.username) for u in agents]


STEP_TEXT = {
    Ticket.Status.OPEN: "Talep kaydedildi; ilk yanıt bekleniyor.",
    Ticket.Status.IN_PROGRESS: "Destek personeli talep üzerinde çalışıyor.",
    Ticket.Status.RESOLVED: "Çözüm talep sahibinin onayına sunuldu.",
    Ticket.Status.CLOSED: "Talep kapandı.",
}


def status_steps(current: str) -> list[dict]:
    """Ayrıntı sayfasındaki süreç şeridi: her adım için geçildi / şu an / sırada bilgisi."""
    order = list(Ticket.Status)
    index = order.index(Ticket.Status(current))
    return [
        {
            "code": status.value,
            "label": status.label,
            "text": STEP_TEXT[status],
            "state": "done" if i < index else "current" if i == index else "next",
        }
        for i, status in enumerate(order)
    ]
