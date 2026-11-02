"""MOD-UI görünümleri (Hafta 2).

Erişim kuralı (FR-04, FR-09):
* Oturumu olmayan kullanıcı giriş sayfasına yönlendirilir (`next` korunur).
* Oturumu olan ama izni olmayan kullanıcı HTTP 403 alır.
* Denetim, istek yöntemi (GET/POST) ne olursa olsun görünüm çalışmadan önce yapılır.
"""

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView

from .roles import PERM_MANAGER_PANEL, PERM_SUPPORT_WORKSPACE, capabilities_for, get_role


class DashboardView(LoginRequiredMixin, TemplateView):
    """Her rolün giriş sonrası gördüğü kişisel panel."""

    template_name = "servicedesk/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        role = get_role(self.request.user)
        context["capabilities"] = capabilities_for(role)
        return context


class SupportWorkspaceView(PermissionRequiredMixin, TemplateView):
    """Destek kuyruğu çalışma alanı. Destek Personeli ve Yönetici rollerine açıktır."""

    permission_required = PERM_SUPPORT_WORKSPACE
    template_name = "servicedesk/support_workspace.html"


class ManagerPanelView(PermissionRequiredMixin, TemplateView):
    """Yönetim paneli. Yalnız Yönetici rolüne açıktır."""

    permission_required = PERM_MANAGER_PANEL
    template_name = "servicedesk/manager_panel.html"
