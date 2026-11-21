"""Kategori yönetimi testleri: FR-15 (Hafta 3)."""

from django.db.models import ProtectedError
from django.test import Client, TestCase
from django.urls import reverse

from servicedesk.models import Category
from servicedesk.roles import AGENT, MANAGER, REQUESTER
from servicedesk.services.tickets import create_ticket

from .helpers import make_user

CATEGORIES = reverse("servicedesk:category_list")
CREATE = reverse("servicedesk:ticket_create")


def toggle_url(category: Category) -> str:
    return reverse("servicedesk:category_toggle", args=[category.pk])


class CategoryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.requester = make_user("ayse", REQUESTER)
        cls.agent = make_user("can", AGENT)
        cls.manager = make_user("elif", MANAGER)
        cls.no_role = make_user("deniz")

    def test_manager_adds_category(self):
        """TC-CAT-01: Yönetici kategori ekler; aynı ad büyük/küçük harf farkıyla da (Türkçe I/ı, İ/i dahil) ikinci kez eklenemez; boş ad reddedilir."""
        self.assertEqual(Category.objects.count(), 5)
        self.client.force_login(self.manager)
        response = self.client.post(CATEGORIES, {"name": "Yazıcı ve tarayıcı", "description": "Çevre birimleri"})
        self.assertRedirects(response, CATEGORIES)
        self.assertTrue(Category.objects.filter(name="Yazıcı ve tarayıcı", is_active=True).exists())
        listing = self.client.get(CATEGORIES)
        self.assertContains(listing, "Yazıcı ve tarayıcı")
        for name in ("Donanım", "donanım", "DONANIM", "AĞ VE BAĞLANTI", "HESAP VE ERİŞİM", "  "):
            with self.subTest(name=name):
                response = self.client.post(CATEGORIES, {"name": name})
                self.assertEqual(response.status_code, 200)
                self.assertIn("name", response.context["form"].errors)
        self.assertEqual(Category.objects.count(), 6)

    def test_inactive_category_is_hidden_from_new_tickets(self):
        """TC-CAT-02: Yönetici kategoriyi POST ile pasifleştirir; pasif kategori yeni talep formunda listelenmez ve doğrudan POST ile seçilemez; eski talepler korunur; kategori silinemez; GET ile ve CSRF belirteçsiz değiştirilemez."""
        category = Category.objects.get(name="Yazılım")
        old = create_ticket(
            requester=self.requester, title="Lisans süresi doldu", description="x", category=category, priority="P3"
        )
        self.client.force_login(self.manager)
        self.assertEqual(self.client.get(toggle_url(category)).status_code, 405)
        self.assertRedirects(self.client.post(toggle_url(category), {"active": "0"}), CATEGORIES)
        category.refresh_from_db()
        self.assertFalse(category.is_active)

        self.client.force_login(self.requester)
        form_page = self.client.get(CREATE)
        self.assertNotIn(category, form_page.context["form"].fields["category"].queryset)
        self.assertNotContains(form_page, ">Yazılım<")
        data = {"title": "Pasif kategori denemesi", "description": "x", "category": category.pk, "priority": "P3"}
        response = self.client.post(CREATE, data)
        self.assertIn("category", response.context["form"].errors)
        old.refresh_from_db()
        self.assertEqual(old.category, category)
        self.assertEqual(self.client.get(reverse("servicedesk:ticket_detail", args=[old.pk])).status_code, 200)
        with self.assertRaises(ProtectedError):
            category.delete()

        self.client.force_login(self.manager)
        self.client.post(toggle_url(category), {"active": "1"})
        category.refresh_from_db()
        self.assertTrue(category.is_active)
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.manager)
        self.assertEqual(csrf_client.post(toggle_url(category), {"active": "0"}).status_code, 403)
        category.refresh_from_db()
        self.assertTrue(category.is_active)

    def test_category_management_is_manager_only(self):
        """TC-CAT-03: Talep Sahibi, Destek Personeli ve rolsüz kullanıcı kategori sayfasına ve durum adresine GET ve POST ile 403 alır."""
        category = Category.objects.get(name="Diğer")
        for user in (self.requester, self.agent, self.no_role):
            self.client.force_login(user)
            for url in (CATEGORIES, toggle_url(category)):
                for method in ("get", "post"):
                    with self.subTest(user=user.username, url=url, method=method):
                        response = getattr(self.client, method)(url, {"name": "Sızma", "active": "0"})
                        self.assertEqual(response.status_code, 403)
        category.refresh_from_db()
        self.assertTrue(category.is_active)
        self.assertFalse(Category.objects.filter(name="Sızma").exists())
