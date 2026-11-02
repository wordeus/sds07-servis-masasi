"""Testlerde ortak kullanılan yardımcılar."""

from django.contrib.auth import get_user_model

# Yalnız testlerde kullanılan, parola kurallarına uyan örnek parola.
TEST_PASSWORD = "Test-Parolasi-2026!"


def make_user(username: str, *, password: str | None = None, **extra):
    """Kullanıcı oluşturur. Parola verilmezse kullanılamaz parola atanır."""
    return get_user_model().objects.create_user(username=username, password=password, **extra)
