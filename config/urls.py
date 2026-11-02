"""Kök URL yapılandırması (Hafta 1: kurulum).

Bu hafta yalnız Django yönetim sitesi vardır; kök adres yönetim sitesine yönlendirilir.
Giriş/çıkış ve rol bazlı sayfalar Hafta 2'de eklenecek (MOD-AUTH, MOD-ROLE).
"""

from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

admin.site.site_header = "SDS-07 Servis Masası yönetimi"
admin.site.site_title = "SDS-07 yönetim"
admin.site.index_title = "Kullanıcılar ve kayıtlar"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(url="/admin/", permanent=False)),
]
