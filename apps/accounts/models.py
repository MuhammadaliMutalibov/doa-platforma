from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class Filial(models.Model):
    """Kompaniya filiali (davlat bo'yicha). Masalan: O'zbekiston, Tojikiston."""

    class Davlat(models.TextChoices):
        UZ = 'UZ', _('Oʻzbekiston')
        TJ = 'TJ', _('Tojikiston')
        TM = 'TM', _('Turkmaniston')
        TR = 'TR', _('Turkiya')

    nomi = models.CharField(_('Filial nomi'), max_length=120)
    davlat = models.CharField(_('Davlat'), max_length=2, choices=Davlat.choices, default=Davlat.UZ)
    manzil = models.CharField(_('Manzil'), max_length=255, blank=True)
    faol = models.BooleanField(_('Faol'), default=True)
    yaratilgan = models.DateTimeField(_('Yaratilgan'), auto_now_add=True)

    class Meta:
        verbose_name = _('Filial')
        verbose_name_plural = _('Filiallar')
        ordering = ('nomi',)

    def __str__(self):
        return f'{self.nomi} · {self.get_davlat_display()}'


class User(AbstractUser):
    """Kompaniya hodimi. Filialga biriktiriladi; filialsiz = super admin."""

    class Rol(models.TextChoices):
        ADMIN = 'admin', _('Administrator')
        BUXGALTER = 'buxgalter', _('Buxgalter')
        HODIM = 'hodim', _('Hodim')

    rol = models.CharField(_('Rol'), max_length=20, choices=Rol.choices, default=Rol.HODIM)
    telefon = models.CharField(_('Telefon'), max_length=20, blank=True)
    rasm = models.ImageField(_('Rasm'), upload_to='avatarlar/', null=True, blank=True)
    filial = models.ForeignKey(
        Filial, verbose_name=_('Filial'),
        on_delete=models.PROTECT, null=True, blank=True, related_name='hodimlar',
        help_text=_('Bo‘sh qoldirilsa — super admin (barcha filiallarni ko‘radi)'),
    )

    class Meta:
        verbose_name = _('Hodim')
        verbose_name_plural = _('Hodimlar')

    def __str__(self):
        ism = self.get_full_name() or self.username
        return f'{ism} ({self.get_rol_display()})'

    @property
    def super_admin(self):
        """Filialga bog'lanmagan foydalanuvchi — super admin (hammasini ko'radi)."""
        return self.filial_id is None


class Faoliyat(models.Model):
    """Tizim aktivligi: kim, qachon, qaysi IP, nima qildi."""

    class Amal(models.TextChoices):
        KIRISH = 'kirish', _('Tizimga kirdi')
        CHIQISH = 'chiqish', _('Tizimdan chiqdi')
        QOSHISH = 'qoshish', _('Qo‘shdi')
        TAHRIRLASH = 'tahrirlash', _('Tahrirladi')
        OCHIRISH = 'ochirish', _('O‘chirdi')

    user = models.ForeignKey(
        'accounts.User', verbose_name=_('Foydalanuvchi'),
        on_delete=models.SET_NULL, null=True, blank=True, related_name='faoliyatlar',
    )
    amal = models.CharField(_('Amal'), max_length=20, choices=Amal.choices)
    tavsif = models.CharField(_('Tavsif'), max_length=255, blank=True)
    ip = models.CharField(_('IP manzil'), max_length=45, blank=True)
    vaqt = models.DateTimeField(_('Vaqt'), auto_now_add=True)

    class Meta:
        verbose_name = _('Faoliyat')
        verbose_name_plural = _('Faoliyat')
        ordering = ('-vaqt',)

    def __str__(self):
        return f'{self.user} · {self.get_amal_display()} · {self.vaqt:%Y-%m-%d %H:%M}'


class Notification(models.Model):
    """Bildirishnoma: tizimda kimdir yangilik qilsa boshqalarga keladi
    (o'zi qilgan odamga kelmaydi)."""

    oluvchi = models.ForeignKey(
        'accounts.User', verbose_name=_('Oluvchi'),
        on_delete=models.CASCADE, related_name='bildirishnomalar',
    )
    actor = models.ForeignKey(
        'accounts.User', verbose_name=_('Kim qildi'),
        on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
    )
    amal = models.CharField(_('Amal'), max_length=20, choices=Faoliyat.Amal.choices)
    xabar = models.CharField(_('Xabar'), max_length=255)
    havola = models.CharField(_('Havola'), max_length=255, blank=True)
    oqilgan = models.BooleanField(_('O‘qilgan'), default=False)
    telegram_yuborildi = models.BooleanField(_('Telegramga yuborildi'), default=False)
    vaqt = models.DateTimeField(_('Vaqt'), auto_now_add=True)

    class Meta:
        verbose_name = _('Bildirishnoma')
        verbose_name_plural = _('Bildirishnomalar')
        ordering = ('-vaqt',)

    def __str__(self):
        return f'{self.oluvchi} · {self.xabar[:40]}'


class TelegramUlanish(models.Model):
    """Super adminning Telegram akkaunti bilan bog'lanishi (chat_id orqali)."""

    user = models.ForeignKey(
        'accounts.User', verbose_name=_('Foydalanuvchi'),
        on_delete=models.CASCADE, related_name='telegram_ulanishlari',
    )
    chat_id = models.BigIntegerField(_('Telegram chat ID'), unique=True)
    username = models.CharField(_('Telegram username'), max_length=64, blank=True)
    ism = models.CharField(_('Ism'), max_length=120, blank=True)
    til = models.CharField(_('Til'), max_length=2, default='uz')
    faol = models.BooleanField(_('Faol'), default=True)
    ulangan = models.DateTimeField(_('Ulangan vaqt'), auto_now_add=True)

    class Meta:
        verbose_name = _('Telegram ulanish')
        verbose_name_plural = _('Telegram ulanishlar')
        ordering = ('-ulangan',)

    def __str__(self):
        return f'{self.user} · {self.username or self.chat_id}'


class TelegramKod(models.Model):
    """Telegramga ulanish uchun bir martalik kod (saytdan olinadi)."""

    user = models.ForeignKey(
        'accounts.User', verbose_name=_('Foydalanuvchi'),
        on_delete=models.CASCADE, related_name='telegram_kodlari',
    )
    kod = models.CharField(_('Kod'), max_length=12, db_index=True)
    yaratilgan = models.DateTimeField(_('Yaratilgan'), auto_now_add=True)
    amal_qiladi = models.DateTimeField(_('Amal qilish muddati'))
    ishlatilgan = models.BooleanField(_('Ishlatilgan'), default=False)

    class Meta:
        verbose_name = _('Telegram kod')
        verbose_name_plural = _('Telegram kodlar')
        ordering = ('-yaratilgan',)

    def yaroqli(self):
        from django.utils import timezone
        return (not self.ishlatilgan) and timezone.now() <= self.amal_qiladi

    def __str__(self):
        return f'{self.kod} ({self.user})'


class Xodim(models.Model):
    """Filial xodimi (login/parolsiz). Maosh shu xodimlarga yoziladi."""

    filial = models.ForeignKey(
        Filial, verbose_name=_('Filial'),
        on_delete=models.PROTECT, related_name='xodimlar',
    )
    ism = models.CharField(_('Ism familiya'), max_length=150)
    lavozim = models.CharField(_('Lavozim'), max_length=100)
    oylik = models.DecimalField(_('Oylik maosh'), max_digits=15, decimal_places=2, default=0)
    telefon = models.CharField(_('Telefon'), max_length=20, blank=True)
    faol = models.BooleanField(_('Faol'), default=True)

    class Meta:
        verbose_name = _('Xodim')
        verbose_name_plural = _('Xodimlar')
        ordering = ('ism',)

    def __str__(self):
        return f'{self.ism} — {self.lavozim}'
