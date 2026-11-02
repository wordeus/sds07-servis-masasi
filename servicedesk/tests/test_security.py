"""Güvenlik NFR testleri: NFR-01..NFR-03."""

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse

from servicedesk.roles import REQUESTER

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


class CsrfTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = make_user("csrf.test", REQUESTER, password=TEST_PASSWORD)

    def test_state_changing_requests_require_csrf_token(self):
        """TC-SEC-02: CSRF belirteci olmayan giriş ve çıkış POST istekleri 403 ile reddedilir; belirteçle kabul edilir."""
        client = Client(enforce_csrf_checks=True)
        login = client.post(reverse("login"), {"username": "csrf.test", "password": TEST_PASSWORD})
        self.assertEqual(login.status_code, 403)
        self.assertContains(login, 'data-testid="error-csrf"', status_code=403)
        self.assertNotIn("_auth_user_id", client.session)

        client.force_login(self.user)
        logout_without_token = client.post(reverse("logout"))
        self.assertEqual(logout_without_token.status_code, 403)
        self.assertIn("_auth_user_id", client.session)

        client.get(reverse("servicedesk:dashboard"))  # Sayfa CSRF çerezini üretir
        token = client.cookies[settings.CSRF_COOKIE_NAME].value
        logout_with_token = client.post(reverse("logout"), {"csrfmiddlewaretoken": token})
        self.assertEqual(logout_with_token.status_code, 302)
        self.assertNotIn("_auth_user_id", client.session)


class SessionCookieTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = make_user("oturum.test", REQUESTER, password=TEST_PASSWORD)

    def test_session_cookie_flags_and_lifetime(self):
        """TC-SEC-03: Oturum çerezi HttpOnly ve SameSite=Lax'tır; oturum süresi 8 saattir (28.800 sn)."""
        response = self.client.post(reverse("login"), {"username": "oturum.test", "password": TEST_PASSWORD})
        cookie = response.cookies[settings.SESSION_COOKIE_NAME]
        self.assertTrue(cookie["httponly"])
        self.assertEqual(cookie["samesite"], "Lax")
        self.assertEqual(int(cookie["max-age"]), 8 * 60 * 60)
        self.assertEqual(settings.SESSION_COOKIE_AGE, 28800)
