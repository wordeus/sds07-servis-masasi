"""MOD-AUTH testleri: FR-01..FR-05."""

from django.test import TestCase
from django.urls import reverse

from servicedesk.roles import REQUESTER

from .helpers import TEST_PASSWORD, make_user

LOGIN = reverse("login")
LOGOUT = reverse("logout")
DASHBOARD = reverse("servicedesk:dashboard")


class LoginTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = make_user("ayse", REQUESTER, password=TEST_PASSWORD, first_name="Ayşe")
        cls.inactive = make_user("pasif", REQUESTER, password=TEST_PASSWORD, is_active=False)

    def _invalid_login_code(self, response):
        return response.context["form"].errors.as_data()["__all__"][0].code

    def test_login_page_renders(self):
        """TC-AUTH-01: Giriş sayfası 200 döner; kullanıcı adı, parola ve CSRF alanlarını içerir."""
        response = self.client.get(LOGIN)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')

    def test_valid_login_redirects_to_dashboard(self):
        """TC-AUTH-02: Geçerli kimlik bilgisiyle giriş oturum açar ve kullanıcıyı paneline yönlendirir."""
        response = self.client.post(LOGIN, {"username": "ayse", "password": TEST_PASSWORD})
        self.assertRedirects(response, DASHBOARD)
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

    def test_authenticated_user_is_redirected_from_login(self):
        """TC-AUTH-03: Oturumu açık kullanıcı giriş sayfasını açtığında paneline yönlendirilir."""
        self.client.force_login(self.user)
        response = self.client.get(LOGIN)
        self.assertRedirects(response, DASHBOARD)

    def test_wrong_credentials_show_generic_error(self):
        """TC-AUTH-04: Hatalı parola veya bilinmeyen kullanıcı oturum açmaz; ikisinde de aynı genel hata gösterilir."""
        wrong_password = self.client.post(LOGIN, {"username": "ayse", "password": "yanlis-parola-123"})
        unknown_user = self.client.post(LOGIN, {"username": "olmayan", "password": "yanlis-parola-123"})
        for response in (wrong_password, unknown_user):
            self.assertEqual(response.status_code, 200)
            self.assertEqual(self._invalid_login_code(response), "invalid_login")
            self.assertContains(response, 'data-testid="login-error"')
            self.assertContains(response, 'aria-invalid="true"')
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertEqual(
            wrong_password.context["form"].non_field_errors(),
            unknown_user.context["form"].non_field_errors(),
        )

    def test_inactive_user_cannot_login(self):
        """TC-AUTH-05: Pasif hesap doğru parolayla da giriş yapamaz; hesabın durumu açığa vurulmaz."""
        response = self.client.post(LOGIN, {"username": "pasif", "password": TEST_PASSWORD})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertEqual(self._invalid_login_code(response), "invalid_login")

    def test_external_next_is_ignored(self):
        """TC-AUTH-09: Dış alan adına işaret eden `next` yok sayılır; kullanıcı kendi paneline yönlendirilir."""
        for target in ("https://kotu.example/", "//kotu.example/giris"):
            with self.subTest(next=target):
                self.client.logout()
                response = self.client.post(LOGIN, {"username": "ayse", "password": TEST_PASSWORD, "next": target})
                self.assertRedirects(response, DASHBOARD)

    def test_internal_next_is_followed(self):
        """TC-AUTH-10: Site içi `next` adresi korunur ve girişten sonra o adrese yönlendirilir."""
        response = self.client.post(LOGIN, {"username": "ayse", "password": TEST_PASSWORD, "next": "/destek/"})
        self.assertRedirects(response, "/destek/", fetch_redirect_response=False)


class LogoutTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = make_user("mehmet", REQUESTER)

    def test_logout_post_ends_session(self):
        """TC-AUTH-06: POST ile çıkış oturumu sonlandırır ve giriş sayfasına yönlendirir."""
        self.client.force_login(self.user)
        response = self.client.post(LOGOUT)
        self.assertRedirects(response, LOGIN)
        self.assertNotIn("_auth_user_id", self.client.session)
        follow_up = self.client.get(DASHBOARD)
        self.assertRedirects(follow_up, f"{LOGIN}?next={DASHBOARD}")

    def test_logout_get_is_rejected(self):
        """TC-AUTH-07: GET ile çıkış isteği HTTP 405 ile reddedilir ve oturum açık kalır."""
        self.client.force_login(self.user)
        response = self.client.get(LOGOUT)
        self.assertEqual(response.status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)


class AuthenticationRequiredTests(TestCase):
    def test_anonymous_requests_redirect_to_login(self):
        """TC-AUTH-08: Oturumsuz GET ve POST istekleri `next` korunarak giriş sayfasına yönlendirilir."""
        for name in ("servicedesk:dashboard", "servicedesk:support_workspace", "servicedesk:manager_panel"):
            url = reverse(name)
            for method in ("get", "post"):
                with self.subTest(url=url, method=method):
                    response = getattr(self.client, method)(url)
                    self.assertRedirects(response, f"{LOGIN}?next={url}", fetch_redirect_response=False)
