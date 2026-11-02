"""Testlerde ortak kullanılan yardımcılar."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from servicedesk.roles import Role

# Yalnız testlerde kullanılan, parola kurallarına uyan örnek parola.
TEST_PASSWORD = "Test-Parolasi-2026!"


def make_user(username: str, role: Role | None = None, *, password: str | None = None, **extra):
    """Kullanıcı oluşturur ve isteğe bağlı olarak rol grubuna ekler.

    Parola verilmezse kullanılamaz parola atanır (testte force_login kullanılır;
    böylece her testte maliyetli parola özetleme yapılmaz).
    """
    user = get_user_model().objects.create_user(username=username, password=password, **extra)
    if role is not None:
        user.groups.add(Group.objects.get(name=role.group_name))
    return user
