"""Tüm şablonlara kullanıcının rol bilgisini ve uygulama sürümünü ekler (FR-08)."""

from . import __version__
from .roles import get_role


def role_context(request):
    context = {"app_version": __version__, "current_role": None, "role_label": None}
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return context
    role = get_role(user)
    context["current_role"] = role
    if role is not None:
        context["role_label"] = role.label
    elif user.is_superuser:
        context["role_label"] = "Sistem yöneticisi"
    return context
