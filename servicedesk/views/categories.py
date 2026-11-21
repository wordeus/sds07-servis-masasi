"""MOD-TICKET görünümleri: kategori yönetimi (FR-15, Hafta 3).

Yalnız Yönetici rolü (ve sistem yöneticisi) erişir. Kategori silinmez, pasifleştirilir;
pasif kategori yeni talep formunda listelenmez. Durum değişikliği yalnız POST ile yapılır.
"""

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView

from ..forms import CategoryForm
from ..roles import PERM_ADD_CATEGORY, PERM_CHANGE_CATEGORY, PERM_VIEW_CATEGORY
from ..services.tickets import all_categories, create_category, get_category, set_category_active
from .tickets import add_validation_errors


class CategoryListView(PermissionRequiredMixin, FormView):
    """Kategori listesi (talep sayılarıyla) ve yeni kategori formu."""

    permission_required = (PERM_VIEW_CATEGORY, PERM_ADD_CATEGORY)
    template_name = "servicedesk/categories/category_list.html"
    form_class = CategoryForm
    success_url = reverse_lazy("servicedesk:category_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = all_categories()
        return context

    def form_valid(self, form):
        try:
            category = create_category(**form.cleaned_data)
        except ValidationError as exc:
            add_validation_errors(form, exc)
            return self.form_invalid(form)
        messages.success(self.request, f"{category.name} kategorisi eklendi.")
        return super().form_valid(form)


class CategoryToggleView(PermissionRequiredMixin, View):
    """Kategoriyi pasifleştirir (active=0) veya yeniden etkinleştirir (active=1). Yalnız POST."""

    permission_required = PERM_CHANGE_CATEGORY
    http_method_names = ["post"]

    def post(self, request, pk):
        category = get_category(pk)
        if category is None:
            raise Http404("Kategori bulunamadı.")
        active = request.POST.get("active") == "1"
        set_category_active(category, active)
        verb = "etkinleştirildi" if active else "pasifleştirildi; yeni talep formunda listelenmeyecek"
        messages.success(request, f"{category.name} kategorisi {verb}.")
        return redirect("servicedesk:category_list")
