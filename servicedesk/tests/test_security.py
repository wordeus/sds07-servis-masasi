"""Güvenlik NFR testleri (Hafta 1): NFR-01."""

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.test import TestCase

from .helpers import TEST_PASSWORD, make_user


class PasswordStorageTests(TestCase):
    def test_password_hashing_and_rules(self):
        """TC-SEC-01: Parola PBKDF2-SHA256 ile özetlenerek saklanır; kısa, yaygın ve yalnız rakamdan oluşan parolalar reddedilir."""
        user = make_user("parola.test", password=TEST_PASSWORD)
        self.assertTrue(user.password.startswith("pbkdf2_sha256$"))
        self.assertNotIn(TEST_PASSWORD, user.password)
        for weak in ("Kisa1!", "password123", "12345678901"):
            with self.subTest(weak=weak):
                with self.assertRaises(ValidationError):
                    validate_password(weak, user=user)
        validate_password(TEST_PASSWORD, user=user)  # Güçlü parola kabul edilir
