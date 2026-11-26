"""MOD-ROLE testleri: FR-06..FR-10."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group, Permission
from django.test import TestCase
from django.urls import reverse

from servicedesk.roles import (
    AGENT,
    MANAGER,
    REQUESTER,
    ROLE_PERMISSIONS,
    ROLES,
    get_role,
    sync_role_groups,
)

from .helpers import make_user

DASHBOARD = reverse("servicedesk:dashboard")
SUPPORT = reverse("servicedesk:support_workspace")
MANAGER_PANEL = reverse("servicedesk:manager_panel")


class RoleUsersMixin:
    """Her rolden ve rolsüz birer kullanıcı."""

    @classmethod
    def setUpTestData(cls):
        cls.requester = make_user("talep", REQUESTER, first_name="Ayşe")
        cls.agent = make_user("destek", AGENT, first_name="Can")
        cls.manager = make_user("yonetici", MANAGER, first_name="Elif")
        cls.no_role = make_user("rolsuz", first_name="Deniz")


class RoleGroupSyncTests(TestCase):
    def test_role_groups_exist_after_migrate(self):
        """TC-ROLE-01: `migrate` sonrasında üç rol grubu (Talep Sahibi, Destek Personeli, Yönetici) bulunur."""
        names = set(Group.objects.values_list("name", flat=True))
        self.assertLessEqual({"Talep Sahibi", "Destek Personeli", "Yönetici"}, names)

    def test_group_permissions_match_matrix(self):
        """TC-ROLE-02: Her rol grubunun izinleri koddaki rol-yetki matrisiyle birebir aynıdır."""
        for role in ROLES:
            with self.subTest(role=role.key):
                group = Group.objects.get(name=role.group_name)
                actual = {
                    f"{perm.content_type.app_label}.{perm.codename}"
                    for perm in group.permissions.select_related("content_type")
                }
                self.assertEqual(actual, set(ROLE_PERMISSIONS[role.key]))

    def test_sync_is_idempotent_and_repairs_drift(self):
        """TC-ROLE-03: Senkronizasyon tekrarlandığında kopya üretmez ve elle yapılan izin sapmasını düzeltir."""
        first = sync_role_groups()
        self.assertTrue(all(not r.created and r.added == 0 and r.removed == 0 for r in first))
        self.assertEqual(Group.objects.filter(name__in=[r.group_name for r in ROLES]).count(), 3)

        manager_perm = Permission.objects.get(codename="access_manager_panel")
        requester_group = Group.objects.get(name=REQUESTER.group_name)
        manager_group = Group.objects.get(name=MANAGER.group_name)
        requester_group.permissions.add(manager_perm)  # yetki yükseltme sapması
        manager_group.permissions.remove(manager_perm)  # eksik yetki sapması

        repaired = {r.role.key: r for r in sync_role_groups()}
        self.assertEqual(repaired[REQUESTER.key].removed, 1)
        self.assertEqual(repaired[MANAGER.key].added, 1)
        self.assertFalse(requester_group.permissions.filter(pk=manager_perm.pk).exists())
        self.assertTrue(manager_group.permissions.filter(pk=manager_perm.pk).exists())


class AdminRoleAssignmentTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = get_user_model().objects.create_superuser("sysadmin", email=None, password=None)
        cls.target = make_user("yeni.personel", first_name="Yeni")
        cls.requester = make_user("talep", REQUESTER)

    def test_superuser_assigns_role_in_admin(self):
        """TC-ROLE-04: Sistem yöneticisi yönetim sitesinden kullanıcıya rol grubu atar; diğer roller yönetim sitesine giremez."""
        agent_group = Group.objects.get(name=AGENT.group_name)
        change_url = reverse("admin:servicedesk_user_change", args=[self.target.pk])

        self.client.force_login(self.superuser)
        page = self.client.get(change_url)
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'name="groups"')

        response = self.client.post(
            change_url,
            {
                "username": "yeni.personel",
                "first_name": "Yeni",
                "last_name": "",
                "email": "",
                "is_active": "on",
                "groups": [str(agent_group.pk)],
                "last_login_0": "",
                "last_login_1": "",
                "date_joined_0": "2026-10-30",
                "date_joined_1": "09:00:00",
            },
        )
        if response.status_code != 302:  # Hata ayıklamayı kolaylaştırmak için form hatalarını göster
            self.fail(f"Yönetim formu kaydedilmedi: {response.context['adminform'].form.errors}")
        self.target.refresh_from_db()
        self.assertEqual(get_role(self.target), AGENT)

        self.client.force_login(self.requester)
        denied = self.client.get(reverse("admin:index"))
        self.assertRedirects(denied, f"{reverse('admin:login')}?next={reverse('admin:index')}")


class RoleResolutionTests(RoleUsersMixin, TestCase):
    def test_role_precedence(self):
        """TC-ROLE-05: Rol çözümlemesi Yönetici > Destek Personeli > Talep Sahibi önceliğini uygular; grupsuz kullanıcının rolü yoktur."""
        multi = make_user("cok.rollu", REQUESTER)
        multi.groups.add(Group.objects.get(name=AGENT.group_name))
        self.assertEqual(get_role(multi), AGENT)
        multi.groups.add(Group.objects.get(name=MANAGER.group_name))
        self.assertEqual(get_role(multi), MANAGER)
        self.assertEqual(get_role(self.requester), REQUESTER)
        self.assertIsNone(get_role(self.no_role))
        self.assertIsNone(get_role(AnonymousUser()))

    def test_dashboard_shows_role_and_capabilities(self):
        """TC-ROLE-06: Panel kullanıcının rolünü ve yalnız o role açık yetkileri gösterir; rolsüz kullanıcı uyarı görür."""
        cases = (
            (self.requester, REQUESTER, "Memnuniyet puanı verme", "KPI paneli"),
            (self.agent, AGENT, "Destek kuyruğu çalışma alanı", "Memnuniyet puanı verme"),
            (self.manager, MANAGER, "KPI paneli", "Memnuniyet puanı verme"),
        )
        for user, role, visible, hidden in cases:
            with self.subTest(role=role.key):
                self.client.force_login(user)
                response = self.client.get(DASHBOARD)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context["role_label"], role.label)
                self.assertContains(response, f"<strong>{role.label}</strong>", html=False)
                self.assertContains(response, visible)
                self.assertNotContains(response, hidden)

        self.client.force_login(self.no_role)
        response = self.client.get(DASHBOARD)
        self.assertIsNone(response.context["role_label"])
        self.assertContains(response, 'data-testid="no-role"')
        self.assertContains(response, "Rol atanmamış")
        self.assertNotContains(response, 'data-testid="capability-table"')


class ServerSideAuthorizationTests(RoleUsersMixin, TestCase):
    def _status(self, user, url, method="get"):
        self.client.force_login(user)
        return getattr(self.client, method)(url).status_code

    def test_requester_and_no_role_are_forbidden(self):
        """TC-ROLE-07: Talep Sahibi ve rolsüz kullanıcı destek kuyruğu ile yönetim paneline doğrudan adresle erişemez (403)."""
        for user in (self.requester, self.no_role):
            for url in (SUPPORT, MANAGER_PANEL):
                with self.subTest(user=user.username, url=url):
                    self.assertEqual(self._status(user, url), 403)
            with self.subTest(user=user.username, url=DASHBOARD):
                self.assertEqual(self._status(user, DASHBOARD), 200)

    def test_agent_access(self):
        """TC-ROLE-08: Destek Personeli destek kuyruğuna erişir (200), yönetim paneline erişemez (403)."""
        self.assertEqual(self._status(self.agent, SUPPORT), 200)
        self.assertEqual(self._status(self.agent, MANAGER_PANEL), 403)

    def test_manager_access(self):
        """TC-ROLE-09: Yönetici destek kuyruğuna ve yönetim paneline erişir (200)."""
        self.assertEqual(self._status(self.manager, SUPPORT), 200)
        self.assertEqual(self._status(self.manager, MANAGER_PANEL), 200)

    def test_forbidden_post_requests(self):
        """TC-ROLE-10: Yetkisiz POST istekleri de 403 alır; yetki denetimi istek yönteminden önce yapılır."""
        cases = (
            (self.requester, SUPPORT, 403),
            (self.requester, MANAGER_PANEL, 403),
            (self.agent, MANAGER_PANEL, 403),
            (self.no_role, SUPPORT, 403),
            # Yetkili kullanıcıda yöntem desteklenmediği için 405 döner (yetki geçildi).
            (self.manager, MANAGER_PANEL, 405),
        )
        for user, url, expected in cases:
            with self.subTest(user=user.username, url=url):
                self.assertEqual(self._status(user, url, method="post"), expected)

    def test_forbidden_page_is_explanatory(self):
        """TC-ROLE-11: 403 yanıtı Türkçe, rolü ve istenen adresi belirten özel hata sayfasıyla döner; teknik ayrıntı sızdırmaz."""
        self.client.force_login(self.requester)
        response = self.client.get(MANAGER_PANEL)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "403.html")
        self.assertContains(response, "Bu sayfa rolünüze kapalı", status_code=403)
        self.assertContains(response, "<strong>Talep Sahibi</strong>", status_code=403)
        self.assertContains(response, MANAGER_PANEL, status_code=403)
        self.assertNotContains(response, "Traceback", status_code=403)


class NavigationTests(RoleUsersMixin, TestCase):
    def test_navigation_links_follow_permissions(self):
        """TC-ROLE-12: Menü yalnız kullanıcının yetkili olduğu bölümlerin bağlantılarını gösterir."""
        superuser = get_user_model().objects.create_superuser("kok", email=None, password=None)
        expectations = (
            (self.requester, set()),
            (self.no_role, set()),
            (self.agent, {"support"}),
            (self.manager, {"support", "manager"}),
            (superuser, {"support", "manager", "admin"}),
        )
        all_links = {"support", "manager", "admin"}
        for user, visible in expectations:
            with self.subTest(user=user.username):
                self.client.force_login(user)
                response = self.client.get(DASHBOARD)
                for link in all_links:
                    marker = f'data-nav="{link}"'
                    if link in visible:
                        self.assertContains(response, marker)
                    else:
                        self.assertNotContains(response, marker)

    def test_ticket_navigation_links_follow_permissions(self):
        """TC-ROLE-13: Menüde "Talepler" bağlantısı talep izni olan rollere, "Kategoriler" bağlantısı yalnız Yönetici ve sistem yöneticisine görünür."""
        superuser = get_user_model().objects.create_superuser("kok.hafta3", email=None, password=None)
        expectations = (
            (self.requester, {"tickets"}),
            (self.no_role, set()),
            (self.agent, {"tickets"}),
            (self.manager, {"tickets", "categories"}),
            (superuser, {"tickets", "categories"}),
        )
        for user, visible in expectations:
            with self.subTest(user=user.username):
                self.client.force_login(user)
                response = self.client.get(DASHBOARD)
                for link in ("tickets", "categories"):
                    marker = f'data-nav="{link}"'
                    if link in visible:
                        self.assertContains(response, marker)
                    else:
                        self.assertNotContains(response, marker)


class Week4PermissionTests(RoleUsersMixin, TestCase):
    def test_week4_permissions_follow_matrix(self):
        """TC-ROLE-14: Hafta 4 izinleri: Talep Sahibi yalnız yorum ekler; Destek Personeli yorum, üzerine alma ve öncelik değiştirme; Yönetici bunlara ek olarak atama yapar; panelde Hafta 4 yetenekleri kullanılabilir, Hafta 5 yetenekleri "Hafta 5", kapsam dışı yetenekler "Kapsam dışı" görünür."""
        perms = (
            "servicedesk.add_comment",
            "servicedesk.take_ticket",
            "servicedesk.change_ticket_priority",
            "servicedesk.assign_ticket",
        )
        expected = {
            self.requester: (True, False, False, False),
            self.agent: (True, True, True, False),
            self.manager: (True, True, True, True),
            self.no_role: (False, False, False, False),
        }
        for user, flags in expected.items():
            with self.subTest(user=user.username):
                user = get_user_model().objects.get(pk=user.pk)  # izin önbelleğini temizle
                self.assertEqual(tuple(user.has_perm(p) for p in perms), flags)
        self.client.force_login(self.manager)
        rows = {row["label"]: row for row in self.client.get(DASHBOARD).context["capabilities"]}
        for label in ("Talebe yorum ekleme", "Talebi üzerine alma", "Talebi destek personeline atama"):
            self.assertTrue(rows[label]["available"], label)
        self.assertFalse(rows["Durum ilerletme (Açık → İşlemde → Çözüldü)"]["available"])
        self.assertTrue(rows["KPI paneli"]["out_of_scope"])
        self.assertContains(self.client.get(DASHBOARD), '<span class="sd-chip">Kapsam dışı</span>', html=False)
        self.assertContains(self.client.get(DASHBOARD), '<span class="sd-chip">Hafta 5</span>', html=False)
