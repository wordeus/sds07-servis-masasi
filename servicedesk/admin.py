"""Django yönetim sitesi (FR-07): kullanıcı oluşturma ve rol (grup) atama."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "first_name", "last_name", "email", "roles", "is_active", "is_staff")
    list_filter = ("groups", "is_active", "is_staff", "is_superuser")

    def get_queryset(self, request):
        # Liste sayfasında her satır için ayrı grup sorgusu (N+1) oluşmasın.
        return super().get_queryset(request).prefetch_related("groups")

    @admin.display(description="Rol grupları")
    def roles(self, obj):
        return ", ".join(sorted(group.name for group in obj.groups.all())) or "-"
