"""MOD-AUTH veri modeli (Hafta 1).

Bu hafta yalnız özel kullanıcı modeli vardır. Django belgeleri yeni projelerde
baştan özel kullanıcı modeli tanımlanmasını önerir; sonradan geçiş zordur.
Model, Django'nun hazır AbstractUser altyapısını değiştirmeden kullanır.

NFR-12 (kişisel veri asgarisi): yalnız kullanıcı adı, ad, soyad ve e-posta tutulur.
"""

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Meta(AbstractUser.Meta):
        verbose_name = "kullanıcı"
        verbose_name_plural = "kullanıcılar"

    def __str__(self) -> str:
        full_name = self.get_full_name()
        return full_name or self.username
