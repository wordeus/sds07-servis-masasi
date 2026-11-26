"""MOD-TICKET testleri: durum makinesi ve işlem geçmişi görünümü (FR-18, FR-19, FR-20, FR-21; Hafta 5)."""

import re
from datetime import UTC, datetime

from django.contrib.messages import get_messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase
from django.urls import reverse

from servicedesk.models import Comment, Ticket, TicketEvent
from servicedesk.roles import AGENT
from servicedesk.services.assignment import assign_ticket, take_ticket
from servicedesk.services.workflow import change_status

from .helpers import make_user
from .test_tickets import TicketFixtures, detail

S = Ticket.Status
CSRF_VALUE = re.compile(rb'name="csrfmiddlewaretoken" value="[^"]+"')


def status_url(ticket) -> str:
    return reverse("servicedesk:ticket_status", args=[ticket.pk])


def notes(response) -> list[str]:
    return [str(m) for m in get_messages(response.wsgi_request)]


class WorkflowTests(TicketFixtures, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.agent2 = make_user("selin", AGENT, first_name="Selin")

    def assigned_ticket(self, agent=None):
        ticket = self.ticket(self.requester)
        take_ticket(ticket, agent or self.agent)
        ticket.refresh_from_db()
        return ticket

    def status_events(self, ticket):
        return list(
            TicketEvent.objects.filter(ticket=ticket, kind="STATUS_CHANGED").values_list(
                "actor__username", "old_value", "new_value"
            )
        )

    def test_full_lifecycle(self):
        """TC-WF-01: Atanmış Destek Personeli talebi İşlemde ve Çözüldü (çözüm açıklamasıyla) durumuna, talep sahibi Kapandı durumuna taşır; her geçiş eski ve yeni durumla tek kayıt yazar; başarı mesajı gösterilir; kapanan talepte durum düğmesi ve yorum formu yoktur."""
        ticket = self.assigned_ticket()
        self.client.force_login(self.agent)
        self.assertContains(self.client.get(detail(ticket.pk)), 'data-target="IN_PROGRESS"')
        response = self.client.post(status_url(ticket), {"target": "IN_PROGRESS"})
        self.assertRedirects(response, detail(ticket.pk))
        self.assertIn(f"{ticket.number} talebinin durumu İşlemde olarak değiştirildi.", notes(response))
        self.client.post(status_url(ticket), {"target": "RESOLVED", "resolution": "Yazıcı sürücüsü güncellendi."})
        self.client.force_login(self.requester)
        page = self.client.get(detail(ticket.pk))
        self.assertContains(page, "Yazıcı sürücüsü güncellendi.")
        self.assertContains(page, 'data-target="CLOSED"')
        self.client.post(status_url(ticket), {"target": "CLOSED"})
        ticket.refresh_from_db()
        self.assertEqual((ticket.status, ticket.resolution), (S.CLOSED, "Yazıcı sürücüsü güncellendi."))
        self.assertEqual(
            self.status_events(ticket),
            [("can", "OPEN", "IN_PROGRESS"), ("can", "IN_PROGRESS", "RESOLVED"), ("ayse", "RESOLVED", "CLOSED")],
        )
        closed = self.client.get(detail(ticket.pk))
        self.assertNotContains(closed, 'data-testid="status-form"')
        self.assertNotContains(closed, 'data-testid="comment-form"')

    def test_resolution_is_required(self):
        """TC-WF-02: Çözüldü geçişinde boş veya yalnız boşluktan oluşan çözüm açıklaması reddedilir (aria-invalid); 2.000 karakterden uzun açıklama reddedilir; durum değişmez ve kayıt yazılmaz."""
        ticket = self.assigned_ticket()
        change_status(ticket, self.agent, S.IN_PROGRESS)
        self.client.force_login(self.agent)
        for resolution, message in (
            ("", "Çözüm açıklaması zorunludur."),
            ("   ", "Çözüm açıklaması zorunludur."),
            ("x" * 2001, "en fazla 2000"),
        ):
            with self.subTest(length=len(resolution)):
                response = self.client.post(status_url(ticket), {"target": "RESOLVED", "resolution": resolution})
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, message)
                self.assertContains(response, 'aria-invalid="true"')
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, S.IN_PROGRESS)
        self.assertEqual(len(self.status_events(ticket)), 1)

    def test_progress_requires_assignment_and_role(self):
        """TC-WF-03: Talebe atanmamış Destek Personeli ve Talep Sahibi talebi ilerletemez (403); atanmamış talep Yönetici tarafından da İşlemde durumuna alınamaz; Yönetici atanmış her talebi ilerletir; servis aynı kuralları uygular."""
        ticket = self.assigned_ticket(self.agent)
        for user in (self.agent2, self.requester, self.no_role):
            with self.subTest(user=user.username):
                self.client.force_login(user)
                self.assertEqual(self.client.post(status_url(ticket), {"target": "IN_PROGRESS"}).status_code, 403)
        self.client.force_login(self.agent2)
        self.assertNotContains(self.client.get(detail(ticket.pk)), 'data-testid="status-form"')
        with self.assertRaises(PermissionDenied):
            change_status(ticket, self.agent2, S.IN_PROGRESS)
        unassigned = self.ticket(self.requester, "Atanmamış talep")
        with self.assertRaises(ValidationError):
            change_status(unassigned, self.manager, S.IN_PROGRESS)
        self.client.force_login(self.manager)
        self.assertContains(
            self.client.post(status_url(unassigned), {"target": "IN_PROGRESS"}, follow=True),
            "Talep önce bir destek personeline atanmalıdır.",
        )
        change_status(ticket, self.manager, S.IN_PROGRESS)
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, S.IN_PROGRESS)
        unassigned.refresh_from_db()
        self.assertEqual(unassigned.status, S.OPEN)

    def test_close_rules(self):
        """TC-WF-04: Çözülmüş talebi talep sahibi kendisi ve Yönetici kapatır; atanmış Destek Personeli kapatamaz (403); başkasının talebini talep sahibi kapatamaz (adres 404, servis PermissionDenied)."""
        first = self.assigned_ticket()
        change_status(first, self.agent, S.IN_PROGRESS)
        change_status(first, self.agent, S.RESOLVED, resolution="Çözüldü")
        self.client.force_login(self.agent)
        self.assertEqual(self.client.post(status_url(first), {"target": "CLOSED"}).status_code, 403)
        self.client.force_login(self.other_requester)
        self.assertEqual(self.client.post(status_url(first), {"target": "CLOSED"}).status_code, 404)
        with self.assertRaises(PermissionDenied):  # servis de talep sahipliğini denetler
            change_status(first, self.other_requester, S.CLOSED)
        self.client.force_login(self.manager)
        self.assertRedirects(self.client.post(status_url(first), {"target": "CLOSED"}), detail(first.pk))
        first.refresh_from_db()
        self.assertEqual(first.status, S.CLOSED)
        self.assertEqual(self.status_events(first)[-1], ("elif", "RESOLVED", "CLOSED"))

    def test_undefined_transitions_are_rejected(self):
        """TC-WF-05: Tanımsız geçişler sunucuda reddedilir: Açık→Çözüldü, Açık→Kapandı, İşlemde→Kapandı, Çözüldü→İşlemde (yeniden açma yok, AK-01), Kapandı→herhangi bir durum ve geçersiz değer; doğrudan POST'ta durum değişmez, kayıt yazılmaz."""
        ticket = self.assigned_ticket()
        self.client.force_login(self.manager)

        def attempt(target, expected_status):
            response = self.client.post(status_url(ticket), {"target": target, "resolution": "x"}, follow=True)
            self.assertNotEqual(response.status_code, 500)
            ticket.refresh_from_db()
            self.assertEqual(ticket.status, expected_status, target)

        for target in ("RESOLVED", "CLOSED", "OPEN", "HACKED"):
            attempt(target, S.OPEN)
        change_status(ticket, self.manager, S.IN_PROGRESS)
        for target in ("CLOSED", "OPEN", "IN_PROGRESS"):
            attempt(target, S.IN_PROGRESS)
        change_status(ticket, self.manager, S.RESOLVED, resolution="Tamam")
        for target in ("IN_PROGRESS", "OPEN", "RESOLVED"):
            attempt(target, S.RESOLVED)
        change_status(ticket, self.manager, S.CLOSED)
        for target in ("OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"):
            attempt(target, S.CLOSED)
        with self.assertRaises(ValidationError):
            change_status(ticket, self.manager, S.IN_PROGRESS)
        self.assertEqual(len(self.status_events(ticket)), 3)
        self.assertEqual(self.client.get(status_url(ticket)).status_code, 405)

    def test_history_is_shown_chronologically(self):
        """TC-WF-06: Talep ayrıntısı işlem geçmişini kronolojik sırayla, İstanbul saatiyle, işlem türü, eski→yeni değer ve kişiyle gösterir; talep sahibi kendi talebinin geçmişini görür; başkasının talebinde 404 alır ve geçmiş sızmaz."""
        ticket = self.ticket(self.requester, priority="P3")
        assign_ticket(ticket, self.manager, self.agent)
        change_status(ticket, self.agent, S.IN_PROGRESS)
        TicketEvent.objects.filter(ticket=ticket, kind="CREATED").update(
            created_at=datetime(2026, 3, 1, 9, 5, tzinfo=UTC)
        )
        self.client.force_login(self.requester)
        page = self.client.get(detail(ticket.pk))
        items = re.findall(r'data-testid="history-item" data-kind="(\w+)"', page.content.decode())
        self.assertEqual(items, ["CREATED", "ASSIGNED", "STATUS_CHANGED"])
        self.assertContains(page, "01.03.2026 12:05")
        self.assertContains(page, "<strong>Durum değişikliği</strong>: Açık → İşlemde", html=False)
        self.assertContains(page, "<strong>Talep oluşturuldu</strong>: P3 (Orta)", html=False)
        self.client.force_login(self.other_requester)
        other = self.client.get(detail(ticket.pk))
        self.assertEqual(other.status_code, 404)
        self.assertNotContains(other, "Durum değişikliği", status_code=404)
        self.assertFalse(Comment.objects.exists())
