"""FR-11: Geliştirme ortamı için her rolden bir demo kullanıcı oluşturur.

Güvenlik kuralları:
* DEBUG kapalıyken (üretim) çalışmayı reddeder.
* Parola koda gömülü değildir: --password, SDS07_DEMO_PASSWORD ortam değişkeni
  ya da rastgele üretilen parola kullanılır ve parola kurallarından (NFR-01) geçer.
* Tekrar çalıştırıldığında kopya kullanıcı üretmez; mevcut demo kullanıcıları günceller.
* Demo kullanıcılarında gerçek kişi verisi yoktur (NFR-12).
"""

import os
import secrets

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from servicedesk.roles import AGENT, MANAGER, REQUESTER, sync_role_groups

DEMO_USERS = (
    ("demo.talep", "Demo", "Talep Sahibi", REQUESTER),
    ("demo.destek", "Demo", "Destek Personeli", AGENT),
    ("demo.yonetici", "Demo", "Yönetici", MANAGER),
)


class Command(BaseCommand):
    help = "Geliştirme ortamında her rol için bir demo kullanıcı oluşturur veya günceller."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            help=(
                "Demo kullanıcıların parolası. Verilmezse SDS07_DEMO_PASSWORD ortam "
                "değişkeni, o da yoksa rastgele bir parola kullanılır."
            ),
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Bu komut yalnız geliştirme ortamında (DEBUG açıkken) çalışır.")

        password = options.get("password") or os.environ.get("SDS07_DEMO_PASSWORD")
        generated = not password
        if generated:
            password = secrets.token_urlsafe(12)
        try:
            validate_password(password)
        except ValidationError as exc:
            raise CommandError("Parola kurallara uymuyor: " + " ".join(exc.messages)) from exc

        sync_role_groups()
        user_model = get_user_model()
        with transaction.atomic():
            for username, first_name, last_name, role in DEMO_USERS:
                user, created = user_model.objects.get_or_create(username=username)
                user.first_name = first_name
                user.last_name = last_name
                user.is_active = True
                user.set_password(password)
                user.save()
                user.groups.set([Group.objects.get(name=role.group_name)])
                action = "Oluşturuldu" if created else "Güncellendi"
                self.stdout.write(f"{action}: {username} ({role.label})")

        if generated:
            self.stdout.write(self.style.WARNING(f"Üretilen parola: {password}  (yalnız bu çıktıda gösterilir)"))
