"""Barcha modullar uchun umumiy: valyuta va asosiy (abstract) modellar."""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Valyuta(models.TextChoices):
    USD = 'USD', _('Dollar (USD)')


class BazaModel(models.Model):
    """Har bir yozuv uchun: filial, yaratilgan/o'zgartirilgan vaqt va kim kiritgani."""

    filial = models.ForeignKey(
        'accounts.Filial',
        verbose_name=_('Filial'),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='+',
    )
    yaratilgan = models.DateTimeField(_('Yaratilgan vaqt'), auto_now_add=True)
    ozgartirilgan = models.DateTimeField(_('O‘zgartirilgan vaqt'), auto_now=True)
    kiritgan = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Kiritgan hodim'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_yozuvlari',
    )

    class Meta:
        abstract = True
