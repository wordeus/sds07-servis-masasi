"""MOD-TICKET testleri: üzerine alma, atama ve öncelik değişikliği (FR-16, AK-03; Hafta 4)."""

from django.contrib.messages import get_messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase
from django.urls import reverse

from servicedesk.models import Ticket, TicketEvent
from servicedesk.roles import AGENT
from servicedesk.services.assignment import assign_ticket, change_priority, take_ticket

from .helpers import make_user
from .test_tickets import TicketFixtures, detail


def url(name: str, ticket) -> str:
    return reverse(f"servicedesk:{name}", args=[ticket.pk])


def notes(response) -> list[str]:
    return [str(m) for m in get_messages(response.wsgi_request)]


class AssignmentTests(TicketFixtures, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.agent2 = make_user("selin", AGENT, first_name="Selin")
        cls.inactive_agent = make_user("eski", AGENT, is_active=False)

    def events(self, ticket, kind):
        return list(TicketEvent.objects.filter(ticket=ticket, kind=kind).values_list("old_value", "new_value"))

    def test_agent_takes_unassigned_ticket(self):
        """TC-ASN-01: Destek Personeli atanmamış talebi üzerine alır (atanan kendisi, işlem geçmişine kayıt, başarı mesajı); atanmış talebi ikinci bir personel üzerine alamaz."""
        ticket = self.ticket(self.requester)
        self.client.force_login(self.agent)
        page = self.client.get(detail(ticket.pk))
        self.assertContains(page, 'data-testid="take-form"')
        response = self.client.post(url("ticket_take", ticket))
        self.assertRedirects(response, detail(ticket.pk))
        ticket.refresh_from_db()
        self.assertEqual(ticket.assignee, self.agent)
        self.assertIn(f"{ticket.number} talebini üzerinize aldınız.", notes(response))
        self.assertEqual(self.events(ticket, "ASSIGNED"), [("", "Can")])
        self.assertNotContains(self.client.get(detail(ticket.pk)), 'data-testid="take-form"')
        self.client.force_login(self.agent2)
        second = self.client.post(url("ticket_take", ticket), follow=True)
        self.assertContains(second, "Bu talep zaten bir destek personeline atanmış.")
        ticket.refresh_from_db()
        self.assertEqual(ticket.assignee, self.agent)
        self.assertEqual(len(self.events(ticket, "ASSIGNED")), 1)

    def test_manager_assigns_only_to_agents(self):
        """TC-ASN-02: Yönetici talebi Destek Personeline atar ve yeniden atar (eski ve yeni değer kaydedilir); Talep Sahibi, Yönetici, rolsüz veya pasif kullanıcıya atama reddedilir, talep değişmez."""
        ticket = self.ticket(self.requester)
        self.client.force_login(self.manager)
        page = self.client.get(detail(ticket.pk))
        options = page.context["assign_form"].fields["assignee"].queryset
        self.assertEqual(set(options), {self.agent, self.agent2})
        response = self.client.post(url("ticket_assign", ticket), {"assignee": self.agent.pk})
        self.assertRedirects(response, detail(ticket.pk))
        self.client.post(url("ticket_assign", ticket), {"assignee": self.agent2.pk})
        ticket.refresh_from_db()
        self.assertEqual(ticket.assignee, self.agent2)
        self.assertEqual(self.events(ticket, "ASSIGNED"), [("", "Can"), ("Can", "Selin")])
        for user in (self.requester, self.manager, self.no_role, self.inactive_agent):
            with self.subTest(assignee=user.username):
                rejected = self.client.post(url("ticket_assign", ticket), {"assignee": user.pk})
                self.assertEqual(rejected.status_code, 200)
                self.assertContains(rejected, "yalnız Destek Personeli rolündeki bir kullanıcıya atanabilir")
                self.assertContains(rejected, 'aria-invalid="true"')
        same = self.client.post(url("ticket_assign", ticket), {"assignee": self.agent2.pk})
        self.assertContains(same, "Talep zaten bu kişiye atanmış.")
        ticket.refresh_from_db()
        self.assertEqual(ticket.assignee, self.agent2)
        self.assertEqual(len(self.events(ticket, "ASSIGNED")), 2)
        with self.assertRaises(ValidationError):
            assign_ticket(ticket, self.manager, self.requester)

    def test_action_urls_enforce_roles(self):
        """TC-ASN-03: Talep Sahibi üzerine alma, atama ve öncelik adreslerine 403 alır; Destek Personeli atamaya 403 alır; GET isteği 405, oturumsuz istek giriş sayfasına yönlenir; servis fonksiyonları da izni denetler."""
        ticket = self.ticket(self.requester)
        forbidden = {
            self.requester: ("ticket_take", "ticket_assign", "ticket_priority"),
            self.agent: ("ticket_assign",),
            self.no_role: ("ticket_take", "ticket_assign", "ticket_priority", "ticket_comment"),
        }
        for user, names in forbidden.items():
            self.client.force_login(user)
            for name in names:
                with self.subTest(user=user.username, url=name):
                    self.assertEqual(self.client.post(url(name, ticket), {"assignee": self.agent.pk}).status_code, 403)
        self.client.force_login(self.manager)
        for name in ("ticket_take", "ticket_assign", "ticket_priority", "ticket_comment"):
            self.assertEqual(self.client.get(url(name, ticket)).status_code, 405)
        self.client.logout()
        response = self.client.post(url("ticket_take", ticket))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/hesap/giris/", response["Location"])
        for call in (
            lambda: take_ticket(ticket, self.requester),
            lambda: assign_ticket(ticket, self.agent, self.agent2),
            lambda: change_priority(ticket, self.requester, "P1"),
        ):
            with self.assertRaises(PermissionDenied):
                call()
        ticket.refresh_from_db()
        self.assertEqual((ticket.assignee, ticket.priority), (None, "P3"))
        self.assertEqual(TicketEvent.objects.filter(ticket=ticket).count(), 1)  # yalnız oluşturma

    def test_staff_change_priority(self):
        """TC-ASN-04: Destek Personeli ve Yönetici önceliği değiştirir (eski ve yeni değer kaydedilir); geçersiz veya aynı öncelik reddedilir; Talep Sahibi öncelik formunu görmez."""
        ticket = self.ticket(self.requester, priority="P3")
        self.client.force_login(self.requester)
        self.assertNotContains(self.client.get(detail(ticket.pk)), 'data-testid="priority-form"')
        self.client.force_login(self.agent)
        response = self.client.post(url("ticket_priority", ticket), {"priority": "P1"})
        self.assertRedirects(response, detail(ticket.pk))
        self.assertIn("Öncelik P1 (Kritik) olarak değiştirildi.", notes(response))
        self.client.force_login(self.manager)
        self.client.post(url("ticket_priority", ticket), {"priority": "P2"})
        ticket.refresh_from_db()
        self.assertEqual(ticket.priority, "P2")
        self.assertEqual(self.events(ticket, "PRIORITY_CHANGED"), [("P3", "P1"), ("P1", "P2")])
        invalid = self.client.post(url("ticket_priority", ticket), {"priority": "P9"})
        self.assertEqual(invalid.status_code, 200)
        self.assertContains(invalid, 'aria-invalid="true"')
        self.assertContains(
            self.client.post(url("ticket_priority", ticket), {"priority": "P2"}), "Talep zaten bu öncelikte."
        )
        ticket.refresh_from_db()
        self.assertEqual(ticket.priority, "P2")
        self.assertEqual(len(self.events(ticket, "PRIORITY_CHANGED")), 2)

    def test_closed_ticket_cannot_be_changed(self):
        """TC-ASN-05: Kapanmış talepte üzerine alma, atama ve öncelik değişikliği reddedilir; işlem formları gösterilmez; işlem geçmişine kayıt yazılmaz."""
        ticket = self.ticket(self.requester)
        # Durum geçişleri Hafta 5'te eklenecek; test verisi için durum doğrudan yazılır.
        Ticket.objects.filter(pk=ticket.pk).update(status=Ticket.Status.CLOSED)
        ticket.refresh_from_db()
        self.client.force_login(self.manager)
        self.assertNotContains(self.client.get(detail(ticket.pk)), 'data-testid="ticket-actions"')
        for name in ("ticket_take", "ticket_assign", "ticket_priority"):
            with self.subTest(url=name):
                data = {"assignee": self.agent.pk, "priority": "P1"}
                response = self.client.post(url(name, ticket), data, follow=True)
                self.assertContains(response, "Kapanmış talepte bu işlem yapılamaz.")
        for call in (
            lambda: take_ticket(ticket, self.agent),
            lambda: assign_ticket(ticket, self.manager, self.agent),
            lambda: change_priority(ticket, self.manager, "P1"),
        ):
            with self.assertRaises(ValidationError):
                call()
        ticket.refresh_from_db()
        self.assertEqual((ticket.assignee, ticket.priority), (None, "P3"))
        self.assertEqual(TicketEvent.objects.filter(ticket=ticket).count(), 1)
