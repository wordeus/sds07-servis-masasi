"""Yapılandırma testleri (MOD-CFG): NFR-03, NFR-04, NFR-05, NFR-11."""

import os
import secrets
import subprocess
import sys
from datetime import UTC, datetime
from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.db import connection
from django.template import Context, Template
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from config.settings import env_bool, env_int, env_list

from .helpers import make_user


class AdminSiteSmokeTests(TestCase):
    def test_admin_works_with_custom_user_model(self):
        """TC-CFG-06: Kurulumdan sonra yönetim sitesi özel kullanıcı modeliyle açılır: kullanıcı listesi ve ekleme formu."""
        self.assertEqual(settings.AUTH_USER_MODEL, "servicedesk.User")
        admin_user = get_user_model().objects.create_superuser("kurulum.admin", email=None, password=None)
        make_user("liste.kullanici", first_name="Liste")
        self.client.force_login(admin_user)
        changelist = self.client.get(reverse("admin:servicedesk_user_changelist"))
        self.assertEqual(changelist.status_code, 200)
        self.assertContains(changelist, "liste.kullanici")
        self.assertContains(changelist, "Rol grupları")
        add_form = self.client.get(reverse("admin:servicedesk_user_add"))
        self.assertEqual(add_form.status_code, 200)


class EnvironmentParsingTests(SimpleTestCase):
    def test_environment_values_are_parsed_strictly(self):
        """TC-CFG-05: Ortam değişkenleri katı ayrıştırılır; geçersiz bool/tam sayı değeri yapılandırma hatası verir."""
        with mock.patch.dict(os.environ, {"SDS_B1": "on", "SDS_B2": "0", "SDS_I": "42", "SDS_L": "a.com, b.com,"}):
            self.assertTrue(env_bool("SDS_B1", default=False))
            self.assertFalse(env_bool("SDS_B2", default=True))
            self.assertEqual(env_int("SDS_I", default=1), 42)
            self.assertEqual(env_list("SDS_L", default=[]), ["a.com", "b.com"])
        with mock.patch.dict(os.environ, {"SDS_EMPTY": " "}):
            self.assertTrue(env_bool("SDS_EMPTY", default=True))
            self.assertEqual(env_int("SDS_EMPTY", default=7), 7)
            self.assertEqual(env_list("SDS_EMPTY", default=["x"]), ["x"])
            self.assertFalse(env_bool("SDS_UNDEFINED_VALUE", default=False))
        with mock.patch.dict(os.environ, {"SDS_BAD_BOOL": "belki", "SDS_BAD_INT": "on iki"}):
            with self.assertRaises(ImproperlyConfigured):
                env_bool("SDS_BAD_BOOL", default=False)
            with self.assertRaises(ImproperlyConfigured):
                env_int("SDS_BAD_INT", default=0)


class TimeZoneTests(TestCase):
    def test_utc_storage_and_istanbul_display(self):
        """TC-CFG-01: Zaman damgası veritabanında UTC saklanır ve arayüzde Europe/Istanbul (UTC+3) saatiyle gösterilir."""
        self.assertTrue(settings.USE_TZ)
        self.assertEqual(settings.TIME_ZONE, "Europe/Istanbul")

        moment = datetime(2026, 1, 15, 9, 30, tzinfo=UTC)
        user = make_user("zaman.test")
        type(user).objects.filter(pk=user.pk).update(date_joined=moment)
        with connection.cursor() as cursor:
            cursor.execute("SELECT date_joined FROM servicedesk_user WHERE id = %s", [user.pk])
            raw_value = cursor.fetchone()[0]
        self.assertTrue(str(raw_value).startswith("2026-01-15 09:30:00"), raw_value)

        rendered = Template("{{ value|date:'d.m.Y H:i' }}").render(Context({"value": moment}))
        self.assertEqual(rendered, "15.01.2026 12:30")


def _run_python(args: list[str], extra_env: dict) -> subprocess.CompletedProcess:
    """Ayarları ayrı bir Python sürecinde, temiz ortam değişkenleriyle yükler."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("DJANGO_")}
    env.update({"DJANGO_SETTINGS_MODULE": "config.settings", **extra_env})
    return subprocess.run(
        [sys.executable, *args],
        cwd=settings.BASE_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )


PRINT_SETTINGS = [
    "-c",
    "import django; django.setup(); from django.conf import settings as s; "
    "print(s.DEBUG, s.SESSION_COOKIE_SECURE, s.CSRF_COOKIE_SECURE, s.SECURE_SSL_REDIRECT)",
]
DEPLOY_CHECK = ["manage.py", "check", "--deploy", "--fail-level", "WARNING"]


class ProductionProfileTests(SimpleTestCase):
    def setUp(self):
        self.secret = secrets.token_urlsafe(50)

    def test_production_refuses_unsafe_configuration(self):
        """TC-CFG-02: Üretim profili SECRET_KEY veya ALLOWED_HOSTS tanımsızken ya da DEBUG açıkken başlamaz."""
        cases = (
            ({"DJANGO_ENV": "production", "DJANGO_ALLOWED_HOSTS": "sds07.example"}, "DJANGO_SECRET_KEY"),
            ({"DJANGO_ENV": "production", "DJANGO_SECRET_KEY": self.secret}, "DJANGO_ALLOWED_HOSTS"),
            (
                {
                    "DJANGO_ENV": "production",
                    "DJANGO_SECRET_KEY": self.secret,
                    "DJANGO_ALLOWED_HOSTS": "sds07.example",
                    "DJANGO_DEBUG": "1",
                },
                "DJANGO_DEBUG",
            ),
        )
        for env, expected_message in cases:
            with self.subTest(missing=expected_message):
                result = _run_python(PRINT_SETTINGS, env)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected_message, result.stderr)

    def test_deploy_check_passes_in_production(self):
        """TC-CFG-03: Üretim profilinde `check --deploy --fail-level WARNING` geçer; oturum ve CSRF çerezleri Secure'dur."""
        env = {
            "DJANGO_ENV": "production",
            "DJANGO_SECRET_KEY": self.secret,
            "DJANGO_ALLOWED_HOSTS": "sds07.example",
        }
        flags = _run_python(PRINT_SETTINGS, env)
        self.assertEqual(flags.returncode, 0, flags.stderr)
        self.assertEqual(flags.stdout.split(), ["False", "True", "True", "True"])

        check = _run_python(DEPLOY_CHECK, env)
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
