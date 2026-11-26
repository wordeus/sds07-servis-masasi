"""MOD-TICKET testleri: yorumlar (FR-17, FR-14; Hafta 4)."""

import re

from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase
from django.urls import reverse

from servicedesk.models import Comment, Ticket
from servicedesk.services.comments import add_comment

from .test_tickets import TicketFixtures, detail

CSRF_VALUE = re.compile(rb'name="csrfmiddlewaretoken" value="[^"]+"')


def comment_url(pk: int) -> str:
    return reverse("servicedesk:ticket_comment", args=[pk])


class CommentTests(TicketFixtures, TestCase):
    def test_roles_add_comments(self):
        """TC-CMT-01: Talep Sahibi kendi talebine, Destek Personeli ve Yönetici herhangi bir talebe yorum ekler; yorumlar eskiden yeniye, yazan adı ve İstanbul saatiyle gösterilir; HTML kaçışlanır."""
        ticket = self.ticket(self.requester)
        for user, body in (
            (self.requester, "Sabah yine oldu."),
            (self.agent, "Sürücüyü güncelledim, deneyin."),
            (self.manager, "<b>Takipteyim</b>"),
        ):
            self.client.force_login(user)
            response = self.client.post(comment_url(ticket.pk), {"body": body})
            self.assertRedirects(response, detail(ticket.pk))
        self.assertEqual(
            list(Comment.objects.filter(ticket=ticket).values_list("author__username", flat=True)),
            ["ayse", "can", "elif"],
        )
        self.client.force_login(self.requester)
        page = self.client.get(detail(ticket.pk))
        self.assertContains(page, 'Yorumlar <span class="sd-muted">(3)</span>', html=False)
        self.assertContains(page, "&lt;b&gt;Takipteyim&lt;/b&gt;")
        self.assertNotContains(page, "<b>Takipteyim</b>")
        content = page.content.decode()
        self.assertLess(content.index("Sabah yine oldu."), content.index("Sürücüyü güncelledim"))
        self.assertContains(page, "Ayşe Demir")

    def test_invalid_comment_is_rejected(self):
        """TC-CMT-02: Boş ya da yalnız boşluktan oluşan yorum ve 2.000 karakterden uzun yorum reddedilir; hata alanla ilişkilendirilir (aria-invalid); kayıt oluşmaz."""
        ticket = self.ticket(self.requester)
        self.client.force_login(self.requester)
        for body, message in (("", "Yorum boş olamaz."), ("   ", "Yorum boş olamaz."), ("x" * 2001, "en fazla 2000")):
            with self.subTest(length=len(body)):
                response = self.client.post(comment_url(ticket.pk), {"body": body})
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, message)
                self.assertContains(response, 'aria-invalid="true"')
        self.assertFalse(Comment.objects.exists())

    def test_comment_url_of_other_users_ticket_is_404(self):
        """TC-CMT-03: Talep Sahibi başkasının talebinin yorum adresine POST gönderdiğinde 404 alır; yanıt var olmayan numarayla aynıdır; yorum oluşmaz; servis fonksiyonu da reddeder."""
        other = self.ticket(self.other_requester, "Başkasının talebi")
        self.client.force_login(self.requester)
        r_other = self.client.post(comment_url(other.pk), {"body": "Merhaba"})
        r_missing = self.client.post(comment_url(other.pk + 1000), {"body": "Merhaba"})
        self.assertEqual((r_other.status_code, r_missing.status_code), (404, 404))
        self.assertNotContains(r_other, "Başkasının talebi", status_code=404)
        self.assertEqual(CSRF_VALUE.sub(b"", r_other.content), CSRF_VALUE.sub(b"", r_missing.content))
        with self.assertRaises(PermissionDenied):
            add_comment(other, self.requester, "Merhaba")
        self.assertFalse(Comment.objects.exists())

    def test_closed_ticket_rejects_comments(self):
        """TC-CMT-04: Kapanmış talebe yorum eklenemez: form gösterilmez, açıklama görünür, doğrudan POST ve servis çağrısı reddedilir."""
        ticket = self.ticket(self.requester)
        # Durum geçişleri Hafta 5'te eklenecek; test verisi için durum doğrudan yazılır.
        Ticket.objects.filter(pk=ticket.pk).update(status=Ticket.Status.CLOSED)
        ticket.refresh_from_db()
        for user in (self.requester, self.agent, self.manager):
            with self.subTest(user=user.username):
                self.client.force_login(user)
                page = self.client.get(detail(ticket.pk))
                self.assertNotContains(page, 'data-testid="comment-form"')
                self.assertContains(page, "Talep kapandığı için yorum eklenemez.")
                rejected = self.client.post(comment_url(ticket.pk), {"body": "Geç kalan yorum"}, follow=True)
                self.assertContains(rejected, "Kapanmış talebe yorum eklenemez.")
        with self.assertRaises(ValidationError):
            add_comment(ticket, self.agent, "Geç kalan yorum")
        self.assertFalse(Comment.objects.exists())
