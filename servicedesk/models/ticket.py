"""MOD-TICKET veri modeli: kategori ve talep (Hafta 3).

Kurallar:
* Talep numarası birincil anahtardan türetilir (`INC-000123`); ayrı bir sayaç
  tutulmaz, böylece eşzamanlı kayıtta numara çakışması olamaz (KRR-12).
* Durum alanı formlarda düzenlenemez (`editable=False`). Yeni talep her zaman
  "Open" durumunda başlar; geçişler Hafta 5'te durum makinesiyle eklenecek (FR-18).
* Kategori silinmez, pasifleştirilir; talebi olan kategori veritabanı düzeyinde
  korunur (`on_delete=PROTECT`, FR-15).
* Zaman damgaları UTC saklanır (`USE_TZ=True`, NFR-05).
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models

from ..text import turkish_key

TITLE_MIN_LENGTH = 5
TITLE_MAX_LENGTH = 200


class Category(models.Model):
    name = models.CharField("ad", max_length=80, unique=True)
    description = models.CharField("açıklama", max_length=200, blank=True)
    is_active = models.BooleanField("etkin", default=True)
    created_at = models.DateTimeField("oluşturulma zamanı", auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "kategori"
        verbose_name_plural = "kategoriler"

    def __str__(self) -> str:
        return self.name if self.is_active else f"{self.name} (pasif)"

    def clean(self):
        """Aynı ad, Türkçe büyük/küçük harf farkı gözetmeden ikinci kez kullanılamaz (FR-15, RSK-21)."""
        super().clean()
        key = turkish_key(self.name)
        others = Category.objects.exclude(pk=self.pk).values_list("name", flat=True)
        if any(turkish_key(name) == key for name in others):
            raise ValidationError({"name": "Bu adla bir kategori zaten var."})


class Ticket(models.Model):
    class Priority(models.TextChoices):
        P1 = "P1", "P1 (Kritik)"
        P2 = "P2", "P2 (Yüksek)"
        P3 = "P3", "P3 (Orta)"
        P4 = "P4", "P4 (Düşük)"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Açık"
        IN_PROGRESS = "IN_PROGRESS", "İşlemde"
        RESOLVED = "RESOLVED", "Çözüldü"
        CLOSED = "CLOSED", "Kapandı"

    title = models.CharField("başlık", max_length=TITLE_MAX_LENGTH, validators=[MinLengthValidator(TITLE_MIN_LENGTH)])
    description = models.TextField("açıklama")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="tickets", verbose_name="kategori")
    priority = models.CharField("öncelik", max_length=2, choices=Priority.choices, default=Priority.P3)
    status = models.CharField("durum", max_length=12, choices=Status.choices, default=Status.OPEN, editable=False)
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="requested_tickets",
        verbose_name="talep sahibi",
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
        verbose_name="atanan destek personeli",
    )
    created_at = models.DateTimeField("oluşturulma zamanı", auto_now_add=True)
    updated_at = models.DateTimeField("güncellenme zamanı", auto_now=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        verbose_name = "talep"
        verbose_name_plural = "talepler"
        permissions = [("view_all_tickets", "Tüm talepleri görüntüleyebilir")]

    def __str__(self) -> str:
        return f"{self.number} {self.title}"

    @property
    def number(self) -> str:
        """Kullanıcıya gösterilen benzersiz talep numarası (FR-12)."""
        return f"INC-{self.pk:06d}" if self.pk else "INC-(kaydedilmedi)"
