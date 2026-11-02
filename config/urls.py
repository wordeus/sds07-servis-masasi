"""Kök URL yapılandırması.

Giriş/çıkış Django'nun hazır LoginView/LogoutView sınıflarıyla sağlanır (MOD-AUTH).
LogoutView yalnız POST kabul eder (Django 5.x), bu da FR-03'ü karşılar.
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from servicedesk.forms import LoginForm

admin.site.site_header = "SDS-07 Servis Masası yönetimi"
admin.site.site_title = "SDS-07 yönetim"
admin.site.index_title = "Kullanıcılar, roller ve kayıtlar"

urlpatterns = [
    path(
        "hesap/giris/",
        auth_views.LoginView.as_view(
            authentication_form=LoginForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("hesap/cikis/", auth_views.LogoutView.as_view(), name="logout"),
    path("admin/", admin.site.urls),
    path("", include("servicedesk.urls")),
]
