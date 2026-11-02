"""MOD-AUTH / MOD-ROLE veri modeli.

Özel kullanıcı modeli Hafta 1'de oluşturuldu; Hafta 2'de rol izinleri (Meta.permissions)
eklendi. Django belgeleri yeni projelerde baştan özel kullanıcı modeli tanımlanmasını
önerir; sonradan geçiş zordur.
Model, Django'nun hazır AbstractUser altyapısını değiştirmeden kullanır.

NFR-12 (kişisel veri asgarisi): yalnız kullanıcı adı, ad, soyad ve e-posta tutulur.
"""

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Meta(AbstractUser.Meta):
        verbose_name = "kullanıcı"
        verbose_name_plural = "kullanıcılar"
        # Uygulama düzeyi izinler. Rol grupları bu izinleri taşır (roles.py).
        permissions = [
            ("access_support_workspace", "Destek kuyruğu çalışma alanına erişebilir"),
            ("access_manager_panel", "Yönetim paneline erişebilir"),
        ]

    def __str__(self) -> str:
        full_name = self.get_full_name()
        return full_name or self.username
