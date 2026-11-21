"""MOD-UI görünümleri: panel, destek kuyruğu, yönetim paneli (Hafta 2; Hafta 3'te talep özetleri).

Erişim kuralı (FR-04, FR-09):
* Oturumu olmayan kullanıcı giriş sayfasına yönlendirilir (`next` korunur).
* Oturumu olan ama izni olmayan kullanıcı HTTP 403 alır.
* Denetim, istek yöntemi (GET/POST) ne olursa olsun görünüm çalışmadan önce yapılır.
"""

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView

from ..roles import PERM_MANAGER_PANEL, PERM_SUPPORT_WORKSPACE, PERM_VIEW_TICKET, capabilities_for, get_role
from ..services.tickets import open_queue, status_counts

QUEUE_PREVIEW = 25  # Destek kuyruğunda gösterilen en eski açık talep sayısı


class DashboardView(LoginRequiredMixin, TemplateView):
    """Her rolün giriş sonrası gördüğü kişisel panel."""

    template_name = "servicedesk/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        role = get_role(user)
        context["capabilities"] = capabilities_for(role)
        if user.has_perm(PERM_VIEW_TICKET):
            context["status_counts"] = status_counts(user)
        return context


class SupportWorkspaceView(PermissionRequiredMixin, TemplateView):
    """Destek kuyruğu çalışma alanı: açık talepler, en eskisi önce. Destek Personeli ve Yönetici rollerine açıktır."""

    permission_required = PERM_SUPPORT_WORKSPACE
    template_name = "servicedesk/support_workspace.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queue = open_queue(self.request.user)
        context["queue"] = queue[:QUEUE_PREVIEW]
        context["queue_total"] = queue.count()
        return context


class ManagerPanelView(PermissionRequiredMixin, TemplateView):
    """Yönetim paneli. Yalnız Yönetici rolüne açıktır."""

    permission_required = PERM_MANAGER_PANEL
    template_name = "servicedesk/manager_panel.html"
