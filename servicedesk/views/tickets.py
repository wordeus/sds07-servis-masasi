"""MOD-TICKET görünümleri: talep listesi, yeni talep, talep ayrıntısı (Hafta 3).

Yetki iki katmanda denetlenir:
1. Rol düzeyi (403): `PermissionRequiredMixin` görünüm çalışmadan önce izni sorar (FR-09).
2. Kayıt düzeyi (404): sorgu kümesi `visible_tickets_for` politikasından gelir; başkasına ait
   talebin ayrıntı adresi istendiğinde kayıt kümede olmadığı için 404 döner (FR-14, KRR-07).
Görünümler modellere doğrudan sorgu yazmaz; bütün sorgular services/ katmanındadır (NFR-16).
"""

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.views.generic import DetailView, FormView, ListView

from ..forms import TicketFilterForm, TicketForm
from ..roles import PERM_ADD_TICKET, PERM_VIEW_ALL_TICKETS, PERM_VIEW_TICKET
from ..services.tickets import create_ticket, filter_tickets, status_steps, visible_tickets_for

PAGE_SIZE = 25  # FR-13
FILTER_FIELDS = ("status", "priority", "category", "assignee")


def add_validation_errors(form, error: ValidationError) -> None:
    """Servis katmanının doğrulama hatalarını forma taşır (alan dışı hatalar genel hata olur)."""
    for field, messages_ in error.message_dict.items():
        form.add_error(field if field in form.fields else None, messages_)


class TicketListView(PermissionRequiredMixin, ListView):
    """Görünür talepler; durum, öncelik, kategori ve atanan kişiye göre filtre; sayfa başına 25 kayıt."""

    permission_required = PERM_VIEW_TICKET
    template_name = "servicedesk/tickets/ticket_list.html"
    context_object_name = "tickets"
    paginate_by = PAGE_SIZE

    def get_queryset(self):
        self.filter_form = TicketFilterForm(self.request.GET)
        return filter_tickets(visible_tickets_for(self.request.user), self.filter_form.to_filters())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.copy()
        query.pop("page", None)
        context.update(
            {
                "filter_form": self.filter_form,
                "filter_query": query.urlencode(),
                "is_filtered": any(self.request.GET.get(name) for name in FILTER_FIELDS),
                "sees_all": self.request.user.has_perm(PERM_VIEW_ALL_TICKETS),
            }
        )
        return context


class TicketCreateView(PermissionRequiredMixin, FormView):
    """Yeni talep (FR-12). Talep sahibi oturumdaki kullanıcıdır; durum Open olarak başlar."""

    permission_required = PERM_ADD_TICKET
    template_name = "servicedesk/tickets/ticket_form.html"
    form_class = TicketForm

    def form_valid(self, form):
        try:
            ticket = create_ticket(requester=self.request.user, **form.cleaned_data)
        except ValidationError as exc:
            add_validation_errors(form, exc)
            return self.form_invalid(form)
        messages.success(self.request, f"{ticket.number} numaralı talebiniz oluşturuldu. Durumu: Açık.")
        return redirect("servicedesk:ticket_detail", pk=ticket.pk)


class TicketDetailView(PermissionRequiredMixin, DetailView):
    """Talep ayrıntısı. Görünmeyen kayıt için 404 (FR-14)."""

    permission_required = PERM_VIEW_TICKET
    template_name = "servicedesk/tickets/ticket_detail.html"
    context_object_name = "ticket"

    def get_queryset(self):
        return visible_tickets_for(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["steps"] = status_steps(self.object.status)
        return context
