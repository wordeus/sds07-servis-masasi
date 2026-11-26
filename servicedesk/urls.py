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
    # Hafta 4: yorum, üzerine alma, atama, öncelik (yalnız POST)
    path("talepler/<int:pk>/yorum/", views.TicketCommentView.as_view(), name="ticket_comment"),
    path("talepler/<int:pk>/uzerine-al/", views.TicketTakeView.as_view(), name="ticket_take"),
    path("talepler/<int:pk>/ata/", views.TicketAssignView.as_view(), name="ticket_assign"),
    path("talepler/<int:pk>/oncelik/", views.TicketPriorityView.as_view(), name="ticket_priority"),
    path("kategoriler/", views.CategoryListView.as_view(), name="category_list"),
    path("kategoriler/<int:pk>/durum/", views.CategoryToggleView.as_view(), name="category_toggle"),
]
