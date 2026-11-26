"""MOD-TICKET işlem görünümleri: yorum, üzerine alma, atama, öncelik (Hafta 4).

Ortak kurallar (TicketActionMixin):
* Yalnız POST kabul edilir (CSRF belirteci zorunlu); GET 405 döner.
* Rol düzeyi (403): `PermissionRequiredMixin` izni görünüm çalışmadan önce sorar (FR-09).
* Kayıt düzeyi (404): talep `visible_tickets_for` kümesinden alınır; talep sahibi başkasının
  talebinin işlem adresine istek gönderirse kayıt yokmuş gibi 404 döner (FR-14).
* Alan hatası (ör. boş yorum, geçersiz öncelik) formda gösterilir. Kural hatası (ör. kapanmış
  talep, zaten atanmış talep) sayfanın üstünde bildirim olarak gösterilir. Talep değişmez.
"""

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from ..forms import AssignForm, CommentForm, PriorityForm
from ..roles import PERM_ADD_COMMENT, PERM_ASSIGN_TICKET, PERM_CHANGE_PRIORITY, PERM_TAKE_TICKET
from ..services.assignment import assign_ticket, change_priority, display_name, take_ticket
from ..services.comments import add_comment
from ..services.tickets import visible_tickets_for
from .tickets import add_validation_errors, ticket_detail_context


class TicketActionMixin:
    """Talep üzerinde POST ile yapılan işlemlerin ortak iskeleti.

    İzin denetimi her görünüm sınıfında açıkça yazılır (PermissionRequiredMixin, TC-ARCH-02).
    """

    http_method_names = ["post"]
    form_class = None
    form_context_name = ""

    def post(self, request, pk):
        self.ticket = get_object_or_404(visible_tickets_for(request.user), pk=pk)
        form = self.form_class(request.POST) if self.form_class else None
        if form is not None and not form.is_valid():
            return self.show_errors(form)
        try:
            message = self.perform(form.cleaned_data if form is not None else {})
        except ValidationError as exc:
            if form is None or not hasattr(exc, "error_dict"):
                messages.error(request, " ".join(exc.messages))
                return redirect("servicedesk:ticket_detail", pk=pk)
            add_validation_errors(form, exc)
            return self.show_errors(form)
        messages.success(request, message)
        return redirect("servicedesk:ticket_detail", pk=pk)

    def perform(self, data: dict) -> str:
        raise NotImplementedError

    def show_errors(self, form):
        context = {"ticket": self.ticket, "object": self.ticket}
        context.update(ticket_detail_context(self.request.user, self.ticket, {self.form_context_name: form}))
        return render(self.request, "servicedesk/tickets/ticket_detail.html", context)


class TicketCommentView(PermissionRequiredMixin, TicketActionMixin, View):
    """Talebe yorum ekler (FR-17)."""

    permission_required = PERM_ADD_COMMENT
    form_class = CommentForm
    form_context_name = "comment_form"

    def perform(self, data):
        add_comment(self.ticket, self.request.user, data["body"])
        return "Yorumunuz eklendi."


class TicketTakeView(PermissionRequiredMixin, TicketActionMixin, View):
    """Atanmamış talebi oturumdaki destek personelinin üzerine alır (FR-16)."""

    permission_required = PERM_TAKE_TICKET

    def perform(self, data):
        take_ticket(self.ticket, self.request.user)
        return f"{self.ticket.number} talebini üzerinize aldınız."


class TicketAssignView(PermissionRequiredMixin, TicketActionMixin, View):
    """Talebi destek personeline atar (FR-16; yalnız Yönetici)."""

    permission_required = PERM_ASSIGN_TICKET
    form_class = AssignForm
    form_context_name = "assign_form"

    def perform(self, data):
        assign_ticket(self.ticket, self.request.user, data["assignee"])
        return f"{self.ticket.number} talebi {display_name(data['assignee'])} kişisine atandı."


class TicketPriorityView(PermissionRequiredMixin, TicketActionMixin, View):
    """Talebin önceliğini değiştirir (AK-03, KRR-17)."""

    permission_required = PERM_CHANGE_PRIORITY
    form_class = PriorityForm
    form_context_name = "priority_form"

    def perform(self, data):
        ticket = change_priority(self.ticket, self.request.user, data["priority"])
        return f"Öncelik {ticket.get_priority_display()} olarak değiştirildi."
