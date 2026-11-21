from django.urls import path

from . import views

app_name = "servicedesk"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("destek/", views.SupportWorkspaceView.as_view(), name="support_workspace"),
    path("yonetim/", views.ManagerPanelView.as_view(), name="manager_panel"),
    # Hafta 3: talepler ve kategoriler (MOD-TICKET)
    path("talepler/", views.TicketListView.as_view(), name="ticket_list"),
    path("talepler/yeni/", views.TicketCreateView.as_view(), name="ticket_create"),
    path("talepler/<int:pk>/", views.TicketDetailView.as_view(), name="ticket_detail"),
    path("kategoriler/", views.CategoryListView.as_view(), name="category_list"),
    path("kategoriler/<int:pk>/durum/", views.CategoryToggleView.as_view(), name="category_toggle"),
]
