"""MOD-TICKET ve MOD-AUDIT veri modeli: yorumlar ve işlem geçmişi (Hafta 4).

Kurallar:
* Yorum bir talebe ve yazarına bağlıdır; talep silinmediği için yorum da silinmez (FR-17).
* İşlem geçmişi yalnız eklenir (FR-20): kaydedilmiş bir olay güncellenemez ve silinemez.
  Model `save()` ikinci kayıtta, `delete()` her zaman hata verir; yönetim sitesinde
  kayıtlar salt okunurdur. Toplu sorgu (`QuerySet.update/delete`) uygulama kodunda
  kullanılmaz; veritabanı düzeyindeki koruma kapsam dışıdır (SDD KRR-16).
* Zaman damgaları UTC saklanır (NFR-05).
"""

from django.conf import settings
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models

from .ticket import Ticket

COMMENT_MAX_LENGTH = 2000


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.PROTECT, related_name="comments", verbose_name="talep")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="ticket_comments", verbose_name="yazan"
    )
    body = models.TextField("yorum", validators=[MinLengthValidator(1), MaxLengthValidator(COMMENT_MAX_LENGTH)])
    created_at = models.DateTimeField("oluşturulma zamanı", auto_now_add=True)

    class Meta:
        ordering = ["created_at", "pk"]
        verbose_name = "yorum"
        verbose_name_plural = "yorumlar"

    def __str__(self) -> str:
        return f"{self.ticket.number} yorumu ({self.author})"


class ImmutableEventError(Exception):
    """İşlem geçmişi kaydı değiştirilmeye veya silinmeye çalışıldı (FR-20)."""


class TicketEvent(models.Model):
    class Kind(models.TextChoices):
        CREATED = "CREATED", "Talep oluşturuldu"
        ASSIGNED = "ASSIGNED", "Atama"
        PRIORITY_CHANGED = "PRIORITY_CHANGED", "Öncelik değişikliği"

    ticket = models.ForeignKey(Ticket, on_delete=models.PROTECT, related_name="events", verbose_name="talep")
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="ticket_events", verbose_name="işlemi yapan"
    )
    kind = models.CharField("işlem", max_length=20, choices=Kind.choices)
    old_value = models.CharField("eski değer", max_length=200, blank=True)
    new_value = models.CharField("yeni değer", max_length=200, blank=True)
    created_at = models.DateTimeField("zaman", auto_now_add=True)

    class Meta:
        ordering = ["created_at", "pk"]
        verbose_name = "işlem geçmişi kaydı"
        verbose_name_plural = "işlem geçmişi"

    def __str__(self) -> str:
        return f"{self.ticket.number} {self.get_kind_display()}"

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise ImmutableEventError("İşlem geçmişi kaydı değiştirilemez.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ImmutableEventError("İşlem geçmişi kaydı silinemez.")
