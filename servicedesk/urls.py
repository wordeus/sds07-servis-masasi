from django.urls import path

from . import views

app_name = "servicedesk"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("destek/", views.SupportWorkspaceView.as_view(), name="support_workspace"),
    path("yonetim/", views.ManagerPanelView.as_view(), name="manager_panel"),
]
