"""Formlar: MOD-AUTH (giriş) ve MOD-TICKET (talep, filtre, kategori).

Giriş için Django'nun hazır AuthenticationForm sınıfı kullanılır; yalnız Bootstrap
sınıfları ve erişilebilirlik öznitelikleri eklenir. Talep formları yalnız kullanıcının
girebileceği alanları içerir: durum, talep sahibi ve atanan kişi formda yoktur, bu yüzden
POST isteğine eklense bile yok sayılır (FR-12).
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Category, Ticket
from .models.ticket import TITLE_MAX_LENGTH, TITLE_MIN_LENGTH
from .services.tickets import TicketFilters, active_categories, all_categories, assignee_choices

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


class StyledForm(forms.Form):
    """Bootstrap sınıflarını ekler; hatalı alanı ekran okuyucuya bildirir (NFR-08)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
            field.widget.attrs.setdefault("class", css)

    def add_error(self, field, error):
        super().add_error(field, error)
        for name in self.errors:
            if name in self.fields:
                self.fields[name].widget.attrs["aria-invalid"] = "true"
                self.fields[name].widget.attrs["aria-describedby"] = f"{name}-hata"


class TicketForm(StyledForm):
    """Yeni talep formu (FR-12). Kategori yalnız etkin kategorilerden seçilir (FR-15)."""

    title = forms.CharField(
        label="Başlık",
        min_length=TITLE_MIN_LENGTH,
        max_length=TITLE_MAX_LENGTH,
        help_text=f"{TITLE_MIN_LENGTH}-{TITLE_MAX_LENGTH} karakter. Sorunu kısaca adlandırın.",
        error_messages={
            "min_length": f"Başlık en az {TITLE_MIN_LENGTH} karakter olmalıdır.",
            "max_length": f"Başlık en fazla {TITLE_MAX_LENGTH} karakter olabilir.",
        },
    )
    description = forms.CharField(
        label="Açıklama",
        widget=forms.Textarea(attrs={"rows": 6}),
        help_text="Ne oldu, ne zamandan beri oluyor, hangi cihaz veya uygulamada?",
    )
    category = forms.ModelChoiceField(
        label="Kategori",
        queryset=Category.objects.none(),
        empty_label="Seçin",
        error_messages={"invalid_choice": "Seçilen kategori kullanılamıyor."},
    )
    priority = forms.ChoiceField(
        label="Öncelik",
        choices=Ticket.Priority.choices,
        initial=Ticket.Priority.P3,
        help_text="P1: hizmet tamamen durdu. P4: acil olmayan istek.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = active_categories()


class TicketFilterForm(StyledForm):
    """Talep listesi filtresi (FR-13). GET ile gelir; geçersiz değer yok sayılır, görünürlüğü genişletmez."""

    status = forms.ChoiceField(label="Durum", required=False, choices=[("", "Tümü"), *Ticket.Status.choices])
    priority = forms.ChoiceField(label="Öncelik", required=False, choices=[("", "Tümü"), *Ticket.Priority.choices])
    category = forms.ModelChoiceField(
        label="Kategori", required=False, queryset=Category.objects.none(), empty_label="Tümü"
    )
    assignee = forms.ChoiceField(label="Atanan", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = all_categories()
        self.fields["assignee"].choices = [("", "Tümü"), *assignee_choices()]

    def to_filters(self) -> TicketFilters:
        """Geçerli alanlardan filtre üretir. Django geçersiz alanı cleaned_data'dan çıkarır."""
        self.is_valid()
        data = getattr(self, "cleaned_data", {})
        return TicketFilters(
            status=data.get("status") or "",
            priority=data.get("priority") or "",
            category=data.get("category"),
            assignee=data.get("assignee") or "",
        )


class CategoryForm(StyledForm):
    """Kategori ekleme formu (FR-15). Aynı ad ikinci kez eklenemez (servis katmanında denetlenir)."""

    name = forms.CharField(label="Kategori adı", max_length=80)
    description = forms.CharField(label="Açıklama", max_length=200, required=False)
