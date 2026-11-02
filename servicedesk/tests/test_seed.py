"""FR-11 testleri: demo kullanıcı komutu."""

from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command
from django.test import TestCase, override_settings

from servicedesk.management.commands.seed_demo_users import DEMO_USERS
from servicedesk.roles import get_role

DEMO_PASSWORD = "Demo-Parolasi-2026"


class SeedDemoUsersTests(TestCase):
    @override_settings(DEBUG=True)
    def test_seed_creates_one_user_per_role_idempotently(self):
        """TC-SEED-01: Demo komutu her rol için bir kullanıcı oluşturur; tekrar çalıştırılınca kopya üretmez."""
        call_command("seed_demo_users", password=DEMO_PASSWORD, stdout=StringIO())
        call_command("seed_demo_users", password=DEMO_PASSWORD, stdout=StringIO())

        users = get_user_model().objects.filter(username__in=[u[0] for u in DEMO_USERS])
        self.assertEqual(users.count(), len(DEMO_USERS))
        for username, _first, _last, role in DEMO_USERS:
            with self.subTest(username=username):
                user = users.get(username=username)
                self.assertEqual(get_role(user), role)
                self.assertEqual(user.groups.count(), 1)
                self.assertTrue(user.check_password(DEMO_PASSWORD))
                self.assertEqual(user.email, "")

    def test_seed_refuses_outside_development(self):
        """TC-SEED-02: DEBUG kapalıyken komut çalışmayı reddeder; zayıf parola da reddedilir; kullanıcı oluşmaz."""
        with override_settings(DEBUG=False):
            with self.assertRaises(CommandError):
                call_command("seed_demo_users", password=DEMO_PASSWORD, stdout=StringIO())
        with override_settings(DEBUG=True):
            with self.assertRaises(CommandError):
                call_command("seed_demo_users", password="12345", stdout=StringIO())
        self.assertFalse(get_user_model().objects.filter(username__startswith="demo.").exists())
