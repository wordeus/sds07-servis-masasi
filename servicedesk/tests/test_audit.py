"""MOD-AUDIT testleri: işlem geçmişi (FR-20; Hafta 4)."""

import importlib
from datetime import timedelta

from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from django.db import connection
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from servicedesk.models import ImmutableEventError, Ticket, TicketEvent
from servicedesk.roles import AGENT
from servicedesk.services.assignment import assign_ticket, change_priority, take_ticket

from .helpers import make_user
from .test_tickets import TicketFixtures

backfill = importlib.import_module("servicedesk.migrations.0006_ticket_created_events")


class AuditTests(TicketFixtures, TestCase):
    def test_each_action_writes_one_event(self):
        """TC-AUD-01: Talep oluşturma, üzerine alma, atama ve öncelik değişikliği işlem geçmişine tam bir kez yazılır: aktör, UTC zaman, eski ve yeni değer; reddedilen işlem kayıt yazmaz."""
        before = timezone.now()
        ticket = self.ticket(self.requester, priority="P3")
        take_ticket(ticket, self.agent)
        change_priority(ticket, self.agent, "P1")
        assign_ticket(ticket, self.manager, make_user("selin", AGENT))
        with self.assertRaises(ValidationError):
            change_priority(ticket, self.manager, "P1")  # aynı öncelik: reddedilir
        rows = list(
            TicketEvent.objects.filter(ticket=ticket).values_list("kind", "actor__username", "old_value", "new_value")
        )
        self.assertEqual(
            rows,
            [
                ("CREATED", "ayse", "", "P3"),
                ("ASSIGNED", "can", "", "Can"),
                ("PRIORITY_CHANGED", "can", "P3", "P1"),
                ("ASSIGNED", "elif", "Can", "selin"),
            ],
        )
        for event in TicketEvent.objects.filter(ticket=ticket):
            self.assertEqual(event.created_at.utcoffset(), timedelta(0))
            self.assertGreaterEqual(event.created_at, before)

    def test_events_cannot_be_changed_or_deleted(self):
        """TC-AUD-02: Kaydedilmiş işlem geçmişi kaydı değiştirilemez ve silinemez; yönetim sitesinde ekleme, değiştirme ve silme yetkisi yoktur (sistem yöneticisi dahil)."""
        ticket = self.ticket(self.requester)
        event = TicketEvent.objects.get(ticket=ticket)
        event.new_value = "P1"
        with self.assertRaises(ImmutableEventError):
            event.save()
        with self.assertRaises(ImmutableEventError):
            event.delete()
        event.refresh_from_db()
        self.assertEqual(event.new_value, "P3")
        admin = make_user("root", is_staff=True, is_superuser=True)
        self.client.force_login(admin)
        changelist = reverse("admin:servicedesk_ticketevent_changelist")
        self.assertEqual(self.client.get(changelist).status_code, 200)
        self.assertEqual(self.client.get(reverse("admin:servicedesk_ticketevent_add")).status_code, 403)
        change = self.client.post(reverse("admin:servicedesk_ticketevent_change", args=[event.pk]), {"new_value": "X"})
        self.assertEqual(change.status_code, 403)
        self.assertEqual(
            self.client.get(reverse("admin:servicedesk_ticketevent_delete", args=[event.pk])).status_code, 403
        )
        event.refresh_from_db()
        self.assertEqual(event.new_value, "P3")
        self.assertEqual(TicketEvent.objects.filter(ticket=ticket).count(), 1)

    def test_backfill_adds_missing_created_events_once(self):
        """TC-AUD-03: 0006 veri migration'ı Hafta 4 öncesi talepler için tek bir "Talep oluşturuldu" kaydı ekler (aktör talep sahibi, yeni değer öncelik); tekrar çalıştırıldığında kopya üretmez."""
        old = Ticket.objects.create(
            requester=self.requester, title="Eski talep", description="Hafta 3", category=self.hardware, priority="P2"
        )
        new = self.ticket(self.requester)
        self.assertFalse(TicketEvent.objects.filter(ticket=old).exists())

        class Editor:
            pass

        editor = Editor()
        editor.connection = connection
        backfill.add_created_events(django_apps, editor)
        backfill.add_created_events(django_apps, editor)
        self.assertEqual(
            list(TicketEvent.objects.filter(ticket=old).values_list("kind", "actor__username", "new_value")),
            [("CREATED", "ayse", "P2")],
        )
        self.assertEqual(TicketEvent.objects.filter(ticket=new).count(), 1)
