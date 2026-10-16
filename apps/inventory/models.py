from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from apps.common.models import BazaModel


class Jins(models.TextChoices):
    """Joja jinsi: tovuq (mokiyon) yoki xo'roz."""
    TOVUQ = 'tovuq', _('Tovuq')
    XOROZ = 'xoroz', _('Xo‘roz')


class Ogirlik(models.TextChoices):
    """Vazn birligi."""
    GRAM = 'g', _('gram')
    KG = 'kg', _('kg')


class Partiya(models.Model):
    """Joja partiyasi (guruh). Har partiya alohida hisoblanadi (filial kabi)."""

    nomi = models.CharField(_('Partiya nomi'), max_length=100)
    filial = models.ForeignKey(
        'accounts.Filial', verbose_name=_('Filial'),
        on_delete=models.PROTECT, null=True, blank=True, related_name='partiyalar',
    )
    sana = models.DateField(_('Boshlangan sana'), null=True, blank=True)
    faol = models.BooleanField(_('Faol'), default=True)
    izoh = models.CharField(_('Izoh'), max_length=255, blank=True)

    class Meta:
        verbose_name = _('Partiya')
        verbose_name_plural = _('Partiyalar')
        ordering = ('-id',)

    def __str__(self):
        return self.nomi


# ============================================================
#  JOJA (tovuq / xo'roz) — harid (+) va nobud (−)
# ============================================================
class JojaHarakat(BazaModel):
    """Joja harakati: sotib olindi (+) yoki nobud bo'ldi (−). Partiyaga bog'lanadi."""

    class Tur(models.TextChoices):
        QOSHILDI = 'qoshildi', _('Sotib olindi')
        KASAL = 'kasal', _('Nobud bo‘ldi')

    sana = models.DateField(_('Sana'))
    jins = models.CharField(_('Joja turi'), max_length=6, choices=Jins.choices, default=Jins.TOVUQ)
    tur = models.CharField(_('Harakat turi'), max_length=10, choices=Tur.choices, default=Tur.QOSHILDI)
    soni = models.PositiveIntegerField(_('Soni (dona)'))
    dona_narxi = models.DecimalField(
        _('Dona narxi'), max_digits=15, decimal_places=2,
        null=True, blank=True, help_text=_('Faqat sotib olishda (harid)'),
    )
    partiya = models.ForeignKey(
        Partiya, verbose_name=_('Partiya'),
        on_delete=models.PROTECT, null=True, blank=True, related_name='harakatlar',
    )
    izoh = models.TextField(_('Izoh'), blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Joja harakati')
        verbose_name_plural = _('Joja harakatlari')
        ordering = ('-sana', '-id')

    def __str__(self):
        return f'{self.get_jins_display()} · {self.get_tur_display()} — {self.soni} dona'

    @property
    def jami(self):
        if self.dona_narxi:
            return self.soni * self.dona_narxi
        return 0

    @staticmethod
    def _yigindi(jins, tur, filial=None):
        qs = JojaHarakat.objects.filter(jins=jins, tur=tur)
        if filial is not None:
            qs = qs.filter(filial=filial)
        return qs.aggregate(s=Sum('soni'))['s'] or 0

    @staticmethod
    def qoldiq(jins, filial=None):
        """Qoldiq = sotib olingan − nobud bo'lgan."""
        return (JojaHarakat._yigindi(jins, JojaHarakat.Tur.QOSHILDI, filial)
                - JojaHarakat._yigindi(jins, JojaHarakat.Tur.KASAL, filial))


class JojaVazn(models.Model):
    """Haftalik o'rtacha vazn (tovuq/xo'roz alohida)."""

    filial = models.ForeignKey(
        'accounts.Filial', verbose_name=_('Filial'),
        on_delete=models.PROTECT, null=True, blank=True, related_name='+',
    )
    sana = models.DateField(_('Sana (hafta)'))
    jins = models.CharField(_('Joja turi'), max_length=6, choices=Jins.choices, default=Jins.TOVUQ)
    ortacha_vazn = models.DecimalField(_('O‘rtacha vazn'), max_digits=10, decimal_places=3)
    birlik = models.CharField(_('Birlik'), max_length=2, choices=Ogirlik.choices, default=Ogirlik.KG)
    izoh = models.CharField(_('Izoh'), max_length=255, blank=True)
    kiritgan = models.ForeignKey(
        'accounts.User', verbose_name=_('Kiritgan hodim'),
        on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
    )
    yaratilgan = models.DateTimeField(_('Yaratilgan vaqt'), auto_now_add=True, null=True)

    class Meta:
        verbose_name = _('Joja vazni')
        verbose_name_plural = _('Joja vaznlari')
        ordering = ('-sana',)

    def __str__(self):
        return f'{self.get_jins_display()} — {self.sana}: {self.ortacha_vazn} {self.birlik}'


# ============================================================
#  TUXUM — faqat brak (tuxum kirimi yo'q, tuxum faqat sotiladi)
# ============================================================
class TuxumBrak(BazaModel):
    """Brak (yaroqsiz) tuxum — sababi bilan."""

    sana = models.DateField(_('Sana'))
    soni = models.PositiveIntegerField(_('Soni (dona)'))
    sabab = models.CharField(_('Sabab'), max_length=255)
    izoh = models.TextField(_('Izoh'), blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Brak tuxum')
        verbose_name_plural = _('Brak tuxumlar')
        ordering = ('-sana', '-id')

    def __str__(self):
        return f'{self.sana}: {self.soni} dona brak'

    @staticmethod
    def jami_brak():
        return TuxumBrak.objects.aggregate(s=Sum('soni'))['s'] or 0


class TuxumYigim(BazaModel):
    """Kunlik tuxum yig'imi (real ishlab chiqarish) — partiya bo'yicha.
    HDEP (tug'uvchanlik) samaradorligini hisoblash uchun ishlatiladi."""

    sana = models.DateField(_('Sana'))
    partiya = models.ForeignKey(
        Partiya, verbose_name=_('Partiya'),
        on_delete=models.PROTECT, null=True, blank=True, related_name='tuxum_yigimlari',
    )
    soni = models.PositiveIntegerField(_('Yig‘ilgan tuxum (dona)'))
    a_sifat = models.PositiveIntegerField(_('A-sifat tuxum (dona)'), default=0)
    ortacha_vazn = models.DecimalField(
        _('O‘rtacha tuxum og‘irligi (g)'), max_digits=5, decimal_places=1, null=True, blank=True)
    izoh = models.CharField(_('Izoh'), max_length=255, blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Tuxum yig‘imi')
        verbose_name_plural = _('Tuxum yig‘imlari')
        ordering = ('-sana', '-id')

    @property
    def randiman(self):
        """Randıman (chiqim) = A-sifat / jami yig'ilgan × 100."""
        if self.soni:
            return self.a_sifat / self.soni * 100
        return 0

    def __str__(self):
        return f'{self.sana}: {self.soni} dona'


class JojaOchirish(BazaModel):
    """Jojalar — tuxumdan ochirilgan jojalar (tovuqlar bazasiga qo'shilmaydi).
    Tuxum sonidan ochilgan soni ayrilsa, nobud bo'lgani chiqadi.
    Masalan: 200 ta tuxum, 190 ta ochildi → 10 tasi nobud."""

    sana = models.DateField(_('Sana'))
    tuxum_soni = models.PositiveIntegerField(_('Tuxum soni (dona)'))
    ochilgan = models.PositiveIntegerField(_('Ochilgan joja (dona)'))
    izoh = models.CharField(_('Izoh'), max_length=255, blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Joja')
        verbose_name_plural = _('Jojalar')
        ordering = ('-sana', '-id')

    @property
    def nobud(self):
        return max(0, self.tuxum_soni - self.ochilgan)

    def __str__(self):
        return f'{self.sana}: {self.ochilgan}/{self.tuxum_soni}'

    @staticmethod
    def jami_ochilgan(filial=None):
        qs = JojaOchirish.objects.all()
        if filial is not None:
            qs = qs.filter(filial=filial)
        return qs.aggregate(s=Sum('ochilgan'))['s'] or 0


class KunlikLog(BazaModel):
    """Partiya kunlik kuzatuvi: yem, suv, o'lim, tirik soni, og'irlik.
    Har partiya uchun kuniga bitta yozuv."""

    partiya = models.ForeignKey(
        Partiya, verbose_name=_('Partiya'),
        on_delete=models.PROTECT, related_name='kunlik_loglar',
    )
    sana = models.DateField(_('Sana'))
    tirik_soni = models.PositiveIntegerField(_('Tirik qush soni'))
    nobud = models.PositiveIntegerField(_('Nobud (dona)'), default=0)
    yem_berilgan = models.DecimalField(_('Berilgan yem (kg)'), max_digits=12, decimal_places=2, default=0)
    yem_kelgan = models.DecimalField(
        _('Omborga kelgan yem (kg)'), max_digits=12, decimal_places=2, default=0,
        help_text=_('Faqat yem yetkazib berilgan kunda'),
    )
    suv_berilgan = models.DecimalField(_('Berilgan suv (litr)'), max_digits=12, decimal_places=2, default=0)
    ortacha_vazn = models.DecimalField(
        _('O‘rtacha og‘irlik (g)'), max_digits=10, decimal_places=2, null=True, blank=True)
    harorat = models.DecimalField(
        _('Harorat (°C)'), max_digits=5, decimal_places=1, null=True, blank=True)
    yoruglik_lux = models.PositiveIntegerField(_('Yorug‘lik kuchi (lk)'), null=True, blank=True)
    yoruglik_soat = models.DecimalField(
        _('Yorug‘lik davomiyligi (soat)'), max_digits=4, decimal_places=1, null=True, blank=True)
    izoh = models.CharField(_('Izoh'), max_length=255, blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Kunlik log')
        verbose_name_plural = _('Kunlik loglar')
        ordering = ('-sana', '-id')
        constraints = [
            models.UniqueConstraint(fields=['partiya', 'sana'], name='kunlik_log_partiya_sana_uniq'),
        ]

    def __str__(self):
        return f'{self.partiya} · {self.sana}'

    @property
    def yem_bosh(self):
        """Bosh boshiga yem (gramm)."""
        if self.tirik_soni:
            return float(self.yem_berilgan) * 1000 / self.tirik_soni
        return 0

    @property
    def suv_bosh(self):
        """Bosh boshiga suv (litr)."""
        if self.tirik_soni:
            return float(self.suv_berilgan) / self.tirik_soni
        return 0

    @property
    def olim_foiz(self):
        if self.tirik_soni:
            return self.nobud / self.tirik_soni * 100
        return 0

    @staticmethod
    def yem_silo_qoldiq(filial=None):
        """Omborda qolgan yem = jami kelgan − jami berilgan (kg)."""
        qs = KunlikLog.objects.all()
        if filial is not None:
            qs = qs.filter(filial=filial)
        agg = qs.aggregate(k=Sum('yem_kelgan'), b=Sum('yem_berilgan'))
        return (agg['k'] or 0) - (agg['b'] or 0)


class Emlash(BazaModel):
    """Emlash / dori / muolaja jurnali — partiya salomatlik tarixi."""

    class Tur(models.TextChoices):
        EMLASH = 'emlash', _('Emlash (vaksina)')
        DORI = 'dori', _('Dori')
        VITAMIN = 'vitamin', _('Vitamin')
        DEZINFEKSIYA = 'dezinfeksiya', _('Dezinfeksiya')
        BOSHQA = 'boshqa', _('Boshqa')

    class Usul(models.TextChoices):
        SUV = 'suv', _('Suv orqali')
        PURKASH = 'purkash', _('Purkash')
        INEKSIYA = 'ineksiya', _('In’ektsiya')
        YEM = 'yem', _('Yem orqali')
        KOZ = 'koz', _('Ko‘zga tomizish')
        BOSHQA = 'boshqa', _('Boshqa')

    partiya = models.ForeignKey(
        Partiya, verbose_name=_('Partiya'),
        on_delete=models.PROTECT, related_name='emlashlar',
    )
    sana = models.DateField(_('Sana'))
    tur = models.CharField(_('Turi'), max_length=12, choices=Tur.choices, default=Tur.EMLASH)
    nomi = models.CharField(_('Nomi (vaksina/dori)'), max_length=150)
    usul = models.CharField(_('Usuli'), max_length=10, choices=Usul.choices, blank=True)
    doza = models.CharField(_('Doza'), max_length=100, blank=True)
    izoh = models.CharField(_('Izoh'), max_length=255, blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Emlash/dori')
        verbose_name_plural = _('Salomatlik jurnali')
        ordering = ('-sana', '-id')

    def __str__(self):
        return f'{self.sana} · {self.get_tur_display()}: {self.nomi}'
