"""MOD-TICKET testleri: FR-12, FR-13, FR-14 (Hafta 3)."""

import re
from datetime import UTC, datetime

from django.contrib.messages import get_messages
from django.core.exceptions import ValidationError
from django.db import connection
from django.test import TestCase
from django.urls import reverse

from servicedesk.models import Category, Ticket
from servicedesk.roles import AGENT, MANAGER, REQUESTER
from servicedesk.services.tickets import create_ticket, visible_tickets_for

from .helpers import make_user

LIST = reverse("servicedesk:ticket_list")
CREATE = reverse("servicedesk:ticket_create")
CSRF_VALUE = re.compile(rb'name="csrfmiddlewaretoken" value="[^"]+"')


def detail(pk: int) -> str:
    return reverse("servicedesk:ticket_detail", args=[pk])


class TicketFixtures:
    """Her rolden kullanıcılar ve varsayılan kategoriler (0004 veri migration'ı)."""

    @classmethod
    def setUpTestData(cls):
        cls.requester = make_user("ayse", REQUESTER, first_name="Ayşe", last_name="Demir")
        cls.other_requester = make_user("mert", REQUESTER, first_name="Mert")
        cls.agent = make_user("can", AGENT, first_name="Can")
        cls.manager = make_user("elif", MANAGER, first_name="Elif")
        cls.no_role = make_user("deniz")
        cls.hardware = Category.objects.get(name="Donanım")
        cls.network = Category.objects.get(name="Ağ ve bağlantı")

    @classmethod
    def ticket(cls, requester, title="Yazıcı çalışmıyor", *, category=None, priority="P3"):
        return create_ticket(
            requester=requester,
            title=title,
            description="Ayrıntılı açıklama",
            category=category or cls.hardware,
            priority=priority,
        )


class TicketCreateTests(TicketFixtures, TestCase):
    def test_requester_creates_ticket(self):
        """TC-TKT-01: Talep Sahibi geçerli formla talep açar: INC-000NNN numarası, Open durumu, talep sahibi kendisi, UTC oluşturma zamanı; ayrıntıya yönlendirilir."""
        self.client.force_login(self.requester)
        data = {
            "title": "VPN bağlantısı kopuyor",
            "description": "Her 10 dakikada bir.",
            "category": self.network.pk,
            "priority": "P2",
        }
        response = self.client.post(CREATE, data)
        ticket = Ticket.objects.get(title="VPN bağlantısı kopuyor")
        self.assertRedirects(response, detail(ticket.pk))
        self.assertEqual(ticket.status, Ticket.Status.OPEN)
        self.assertEqual((ticket.requester, ticket.assignee, ticket.priority), (self.requester, None, "P2"))
        self.assertRegex(ticket.number, r"^INC-\d{6}$")
        self.assertEqual(ticket.number, f"INC-{ticket.pk:06d}")
        self.assertEqual(ticket.created_at.utcoffset().total_seconds(), 0)
        with connection.cursor() as cursor:
            cursor.execute("SELECT created_at FROM servicedesk_ticket WHERE id = %s", [ticket.pk])
            raw = str(cursor.fetchone()[0])
        self.assertTrue(raw.startswith(ticket.created_at.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S")), raw)
        notes = [str(m) for m in get_messages(response.wsgi_request)]
        self.assertIn(f"{ticket.number} numaralı talebiniz oluşturuldu. Durumu: Açık.", notes)
        self.assertNotEqual(self.ticket(self.requester, "İkinci talep").number, ticket.number)

    def test_invalid_ticket_input_is_rejected(self):
        """TC-TKT-02: Kısa/uzun başlık, boş açıklama, pasif veya olmayan kategori ve geçersiz öncelikle talep oluşmaz; forma eklenen durum, talep sahibi ve atanan alanları yok sayılır."""
        self.client.force_login(self.requester)
        inactive = Category.objects.create(name="Eski sistem", is_active=False)
        valid = {"title": "Geçerli başlık", "description": "Açıklama", "category": self.hardware.pk, "priority": "P3"}
        cases = {
            "4 karakterlik başlık": ({"title": "Kısa"}, "title"),
            "201 karakterlik başlık": ({"title": "x" * 201}, "title"),
            "boş açıklama": ({"description": "   "}, "description"),
            "pasif kategori": ({"category": inactive.pk}, "category"),
            "olmayan kategori": ({"category": 999999}, "category"),
            "geçersiz öncelik": ({"priority": "P9"}, "priority"),
        }
        for name, (change, field) in cases.items():
            with self.subTest(name):
                response = self.client.post(CREATE, {**valid, **change})
                self.assertEqual(response.status_code, 200)
                self.assertIn(field, response.context["form"].errors)
                self.assertContains(response, 'aria-invalid="true"')
        self.assertFalse(Ticket.objects.exists())

        extra = {"status": "CLOSED", "requester": self.other_requester.pk, "assignee": self.agent.pk}
        self.client.post(CREATE, {**valid, **extra})
        ticket = Ticket.objects.get()
        self.assertEqual((ticket.status, ticket.requester, ticket.assignee), (Ticket.Status.OPEN, self.requester, None))
        with self.assertRaises(ValidationError):
            create_ticket(
                requester=self.requester, title="Servis denemesi", description="x", category=inactive, priority="P3"
            )

    def test_users_without_ticket_permission_are_refused(self):
        """TC-TKT-03: Rolsüz kullanıcı talep listesi, yeni talep ve ayrıntı adreslerine GET ve POST ile 403 alır; oturumsuz istek giriş sayfasına yönlenir."""
        ticket = self.ticket(self.requester)
        urls = (LIST, CREATE, detail(ticket.pk))
        self.client.force_login(self.no_role)
        for url in urls:
            for method in ("get", "post"):
                with self.subTest(user="rolsuz", url=url, method=method):
                    self.assertEqual(getattr(self.client, method)(url).status_code, 403)
        self.assertEqual(Ticket.objects.count(), 1)
        self.client.logout()
        for url in urls:
            with self.subTest(user="oturumsuz", url=url):
                response = self.client.get(url)
                self.assertRedirects(response, f"{reverse('login')}?next={url}", fetch_redirect_response=False)


class TicketListTests(TicketFixtures, TestCase):
    def _ids(self, user, **params) -> set[int]:
        self.client.force_login(user)
        response = self.client.get(LIST, params)
        self.assertEqual(response.status_code, 200)
        return {t.pk for t in response.context["tickets"]}

    def test_list_shows_only_visible_tickets(self):
        """TC-TKT-04: Talep Sahibi listede yalnız kendi taleplerini görür; Destek Personeli ve Yönetici tüm talepleri görür."""
        own = self.ticket(self.requester, "Kendi talebim")
        other = self.ticket(self.other_requester, "Başkasının talebi")
        expectations = (
            (self.requester, {own.pk}),
            (self.other_requester, {other.pk}),
            (self.agent, {own.pk, other.pk}),
            (self.manager, {own.pk, other.pk}),
        )
        for user, expected in expectations:
            with self.subTest(user=user.username):
                self.assertEqual(self._ids(user), expected)
                self.assertEqual(set(visible_tickets_for(user).values_list("pk", flat=True)), expected)
        self.client.force_login(self.requester)
        response = self.client.get(LIST)
        self.assertNotContains(response, "Başkasının talebi")
        self.assertNotContains(response, other.number)
        self.assertEqual(set(visible_tickets_for(self.no_role)), set())

    def test_filters_narrow_the_visible_set(self):
        """TC-TKT-05: Durum, öncelik, kategori ve atanan filtreleri sonucu daraltır; geçersiz değer yok sayılır; filtre görünürlüğü genişletmez."""
        a = self.ticket(self.requester, "Ağ sorunu", category=self.network, priority="P1")
        b = self.ticket(self.requester, "Donanım sorunu", category=self.hardware, priority="P3")
        c = self.ticket(self.other_requester, "Başkasının ağ sorunu", category=self.network, priority="P1")
        # Durum geçişleri Hafta 5'te eklenecek; test verisi için durum ve atama doğrudan yazılır.
        Ticket.objects.filter(pk=b.pk).update(status=Ticket.Status.IN_PROGRESS, assignee=self.agent)
        self.assertEqual(self._ids(self.manager, priority="P1"), {a.pk, c.pk})
        self.assertEqual(self._ids(self.manager, category=self.network.pk), {a.pk, c.pk})
        self.assertEqual(self._ids(self.manager, status="IN_PROGRESS"), {b.pk})
        self.assertEqual(self._ids(self.manager, assignee="none"), {a.pk, c.pk})
        self.assertEqual(self._ids(self.manager, assignee=str(self.agent.pk)), {b.pk})
        self.assertEqual(self._ids(self.manager, status="OPEN", priority="P1", category=self.network.pk), {a.pk, c.pk})
        self.assertEqual(self._ids(self.requester, priority="P1"), {a.pk})
        self.assertEqual(self._ids(self.requester, status="HACKED", priority="P1"), {a.pk})
        self.assertEqual(self._ids(self.requester, category="abc"), {a.pk, b.pk})

    def test_list_is_paginated_by_25(self):
        """TC-TKT-06: Liste sayfa başına 25 talep gösterir, en yeni talep önce gelir; filtre parametreleri sayfa bağlantılarında korunur; aralık dışı sayfa 404 döner."""
        for i in range(30):
            self.ticket(self.requester, f"Toplu talep {i:02d}", priority="P4")
        self.client.force_login(self.requester)
        first = self.client.get(LIST)
        self.assertEqual(len(first.context["tickets"]), 25)
        self.assertEqual(first.context["paginator"].count, 30)
        self.assertEqual(first.context["tickets"][0].title, "Toplu talep 29")
        self.assertContains(first, "30 talep, sayfa 1 / 2")
        self.assertEqual(len(self.client.get(LIST, {"page": 2}).context["tickets"]), 5)
        self.assertContains(self.client.get(LIST, {"priority": "P4"}), "?priority=P4&amp;page=2")
        self.assertEqual(self.client.get(LIST, {"page": 3}).status_code, 404)


class TicketDetailTests(TicketFixtures, TestCase):
    def test_other_users_ticket_is_not_revealed(self):
        """TC-TKT-07: Talep Sahibi başkasının talebinin ayrıntı adresine 404 alır; yanıt var olmayan numarayla aynıdır ve kaydın varlığını açığa vurmaz."""
        other = self.ticket(self.other_requester, "Gizli kalması gereken talep")
        missing_pk = other.pk + 1000
        self.client.force_login(self.requester)
        r_other = self.client.get(detail(other.pk))
        r_missing = self.client.get(detail(missing_pk))
        self.assertEqual((r_other.status_code, r_missing.status_code), (404, 404))
        self.assertTemplateUsed(r_other, "404.html")
        self.assertNotContains(r_other, "Gizli kalması gereken", status_code=404)
        self.assertNotContains(r_other, other.number, status_code=404)
        self.assertEqual(CSRF_VALUE.sub(b"", r_other.content), CSRF_VALUE.sub(b"", r_missing.content))
        # Ayrıntı adresi POST kabul etmez; yanıt kaydın varlığına göre değişmez (405).
        self.assertEqual(self.client.post(detail(other.pk)).status_code, 405)
        self.assertEqual(self.client.post(detail(missing_pk)).status_code, 405)

    def test_staff_see_any_ticket_detail(self):
        """TC-TKT-08: Destek Personeli, Yönetici ve talebin sahibi ayrıntıyı görür; sayfa numara, durum, öncelik, kategori, talep sahibi ve İstanbul saatiyle oluşturma zamanını gösterir."""
        ticket = self.ticket(self.requester, "Ekran titriyor", priority="P2")
        Ticket.objects.filter(pk=ticket.pk).update(created_at=datetime(2026, 3, 1, 9, 5, tzinfo=UTC))
        for user in (self.agent, self.manager, self.requester):
            with self.subTest(user=user.username):
                self.client.force_login(user)
                response = self.client.get(detail(ticket.pk))
                self.assertEqual(response.status_code, 200)
                for text in (ticket.number, "Ekran titriyor", "P2 (Yüksek)", "Donanım", "Ayşe Demir", "Henüz atanmadı"):
                    self.assertContains(response, text)
                self.assertContains(response, "01.03.2026 12:05")
                self.assertContains(response, '<span class="sd-status" data-status="OPEN">Açık</span>', html=False)
                self.assertContains(response, 'aria-current="step"')
