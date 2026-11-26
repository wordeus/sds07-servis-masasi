"""Django yönetim sitesi (FR-07): kullanıcı oluşturma ve rol (grup) atama.

Hafta 3'te kategori ve talep, Hafta 4'te yorum ve işlem geçmişi (salt okunur) kayıtları eklendi.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Category, Comment, Ticket, TicketEvent, User


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


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)

    def has_delete_permission(self, request, obj=None):
        # FR-15: kategori silinmez, pasifleştirilir; eski talepler kategorisini korur.
        return False


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("number", "title", "status", "priority", "category", "requester", "assignee", "created_at")
    list_filter = ("status", "priority", "category")
    search_fields = ("title",)
    list_select_related = ("category", "requester", "assignee")
    readonly_fields = ("number", "status", "created_at", "updated_at")

    def has_delete_permission(self, request, obj=None):
        # İzlenebilirlik (ISO 9001:2026 8.5.2): talep kaydı silinmez; kapatma Hafta 5'te durum akışıyla yapılır.
        return False


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("ticket", "author", "created_at")
    list_select_related = ("ticket", "author")
    readonly_fields = ("ticket", "author", "body", "created_at")

    def has_add_permission(self, request):
        return False  # Yorum talep sayfasından eklenir (FR-17)

    def has_delete_permission(self, request, obj=None):
        return False  # İzlenebilirlik: yorum silinmez


@admin.register(TicketEvent)
class TicketEventAdmin(admin.ModelAdmin):
    """İşlem geçmişi salt okunurdur: eklenemez, değiştirilemez, silinemez (FR-20)."""

    list_display = ("ticket", "kind", "old_value", "new_value", "actor", "created_at")
    list_filter = ("kind",)
    list_select_related = ("ticket", "actor")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
