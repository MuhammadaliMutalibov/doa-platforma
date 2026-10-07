from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from apps.common.models import BazaModel, Valyuta


class Sotuv(BazaModel):
    """Sotuv: tovuq yoki tuxum. Qanchadan (birlik narxi) va qancha (soni) sotildi."""

    class Tur(models.TextChoices):
        TUXUM = 'tuxum', _('Tuxum')
        JOJA = 'joja', _('Joja')

    class TuxumSifati(models.TextChoices):
        SIFATLI = 'sifatli', _('Sifatli tuxum')
        SIFATSIZ = 'sifatsiz', _('Sifatsiz tuxum')

    class Manba(models.TextChoices):
        JOJA = 'joja', _('Jojalar (ochirilgan)')
        TOVUQBAZA = 'tovuqbaza', _('Tovuqlar bazasi')

    class Jins(models.TextChoices):
        TOVUQ = 'tovuq', _('Tovuq')
        XOROZ = 'xoroz', _('Xo‘roz')

    sana = models.DateField(_('Sana'))
    tur = models.CharField(_('Sotuv turi'), max_length=10, choices=Tur.choices)
    tuxum_sifati = models.CharField(
        _('Tuxum sifati'), max_length=10, choices=TuxumSifati.choices, blank=True,
        help_text=_('Faqat tuxum sotuvida tanlanadi'),
    )
    manba = models.CharField(
        _('Manba'), max_length=10, choices=Manba.choices, blank=True,
        help_text=_('Joja sotuvida: jojalar yoki tovuqlar bazasidan'),
    )
    jins = models.CharField(
        _('Joja turi'), max_length=6, choices=Jins.choices, blank=True,
        help_text=_('Tovuqlar bazasidan sotilganda: tovuq yoki xo‘roz'),
    )
    soni = models.PositiveIntegerField(_('Soni (dona)'))
    birlik_narxi = models.DecimalField(_('Birlik narxi'), max_digits=15, decimal_places=2)
    valyuta = models.CharField(
        _('Valyuta'), max_length=3, choices=Valyuta.choices, default=Valyuta.USD,
    )
    izoh = models.TextField(_('Izoh'), blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Sotuv')
        verbose_name_plural = _('Sotuvlar')
        ordering = ('-sana', '-id')

    def __str__(self):
        return f'{self.get_tur_display()} — {self.soni} × {self.birlik_narxi} {self.valyuta}'

    @property
    def jami(self):
        """Jami summa = soni × birlik narxi."""
        return self.soni * self.birlik_narxi

    @staticmethod
    def sotilgan_soni(tur):
        """Berilgan tur bo'yicha sotilgan umumiy dona."""
        return Sotuv.objects.filter(tur=tur).aggregate(s=Sum('soni'))['s'] or 0
