from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ServicedeskConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "servicedesk"
    verbose_name = "Servis Masası"

    def ready(self):
        # FR-06: Her `migrate` sonrasında rol grupları ve izinleri kodda tanımlı
        # matrisle eşitlenir. Django'nun izin oluşturma alıcısı (auth) bizden önce
        # bağlandığı için bu noktada uygulamanın izinleri veritabanında hazırdır.
        from .roles import sync_role_groups_on_migrate

        post_migrate.connect(
            sync_role_groups_on_migrate,
            sender=self,
            dispatch_uid="servicedesk.sync_role_groups",
        )
