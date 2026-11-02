"""MOD-AUTH formları.

Django'nun hazır AuthenticationForm sınıfı kullanılır; yalnız Bootstrap sınıfları ve
erişilebilirlik öznitelikleri eklenir. Doğrulama mantığı (parola kontrolü, pasif hesap
reddi, genel hata mesajı) Django'dadır.
"""

from django.contrib.auth.forms import AuthenticationForm

LOGIN_ERROR_ID = "giris-hatasi"  # login.html'deki hata kutusunun kimliği


class LoginForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control form-control-lg"

    def full_clean(self):
        super().full_clean()
        # NFR-08: Hatalı girişte ekran okuyucular alanları hata mesajıyla ilişkilendirir.
        if self.non_field_errors():
            for field in self.fields.values():
                field.widget.attrs["aria-invalid"] = "true"
                field.widget.attrs["aria-describedby"] = LOGIN_ERROR_ID
