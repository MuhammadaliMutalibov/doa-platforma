from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from apps.common.models import BazaModel, Valyuta


class Kirim(BazaModel):
    """Investitsiya (partiyaga kiritilgan pul). UI'da 'Investitsiya' deb ko'rsatiladi."""

    sana = models.DateField(_('Sana'))
    partiya = models.ForeignKey(
        'inventory.Partiya', verbose_name=_('Partiya'),
        on_delete=models.PROTECT, null=True, blank=True, related_name='investitsiyalar',
    )
    summa = models.DecimalField(_('Summa'), max_digits=15, decimal_places=2)
    valyuta = models.CharField(
        _('Valyuta'), max_length=3, choices=Valyuta.choices, default=Valyuta.USD,
    )
    izoh = models.TextField(_('Izoh'), blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Investitsiya')
        verbose_name_plural = _('Investitsiyalar')
        ordering = ('-sana', '-id')

    def __str__(self):
        return f'{self.summa} — {self.partiya or ""}'


class RasxodKategoriya(models.Model):
    """Rasxod sababi (yem, dori, transport, kommunal, ...). UI'da 'Sabab'."""

    nomi = models.CharField(_('Sabab'), max_length=100, unique=True)

    class Meta:
        verbose_name = _('Sabab')
        verbose_name_plural = _('Sabablar')
        ordering = ('nomi',)

    def __str__(self):
        return self.nomi


class Rasxod(BazaModel):
    """Kunlik xarajat: sana, sabab (tanlanadi), summa."""

    sana = models.DateField(_('Sana'))
    kategoriya = models.ForeignKey(
        RasxodKategoriya, verbose_name=_('Sabab'),
        on_delete=models.PROTECT, related_name='rasxodlar',
    )
    summa = models.DecimalField(_('Summa'), max_digits=15, decimal_places=2)
    valyuta = models.CharField(
        _('Valyuta'), max_length=3, choices=Valyuta.choices, default=Valyuta.USD,
    )
    izoh = models.TextField(_('Izoh'), blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Rasxod')
        verbose_name_plural = _('Rasxodlar')
        ordering = ('-sana', '-id')

    def __str__(self):
        return f'{self.summa} — {self.kategoriya}'


class Maosh(BazaModel):
    """Hodim maoshi: hodim, sana, summa."""

    hodim = models.ForeignKey(
        'accounts.Xodim', verbose_name=_('Xodim'),
        on_delete=models.PROTECT, related_name='maoshlar',
    )
    sana = models.DateField(_('Sana'), default=timezone.localdate)
    summa = models.DecimalField(_('Summa'), max_digits=15, decimal_places=2)
    valyuta = models.CharField(
        _('Valyuta'), max_length=3, choices=Valyuta.choices, default=Valyuta.USD,
    )
    izoh = models.TextField(_('Izoh'), blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Maosh')
        verbose_name_plural = _('Maoshlar')
        ordering = ('-sana', '-id')

    def __str__(self):
        return f'{self.hodim} — {self.summa}'
