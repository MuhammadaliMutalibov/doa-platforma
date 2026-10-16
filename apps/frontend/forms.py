"""Frontend formalar — barchasi bir xil 'input' uslubida bo'ladi (faqat USD)."""

from decimal import Decimal

from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import Filial, User, Xodim
from apps.finance.models import Kirim, Maosh, Rasxod
from apps.inventory.models import (Emlash, JojaHarakat, JojaOchirish, JojaVazn, KunlikLog,
                                    Partiya, TuxumYigim)
from apps.sales.models import Sotuv

# Musbat (0 dan katta) bo'lishi shart bo'lgan pul/narx maydonlari
PUL_MAYDONLAR = {'summa', 'dona_narxi', 'birlik_narxi', 'ortacha_vazn'}
# Manfiy bo'lmasligi kerak (0 ga ruxsat)
NOMANFIY_MAYDONLAR = {'oylik', 'nobud', 'yem_berilgan', 'yem_kelgan', 'suv_berilgan',
                      'yoruglik_lux', 'yoruglik_soat', 'a_sifat'}
# Kamida 1 bo'lishi kerak bo'lgan son maydonlari
SON_MAYDONLAR = {'soni', 'tuxum_soni', 'tirik_soni'}


class StyledModelForm(forms.ModelForm):
    """Barcha maydonlarga CSS klass qo'shadi, sanalarni date-picker qiladi,
    pul/son maydonlariga musbatlik validatsiyasini biriktiradi."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            # Raqamli maydonlarga musbatlik cheklovi (manfiy/nol kiritib bo'lmaydi)
            if name in PUL_MAYDONLAR:
                field.validators.append(MinValueValidator(
                    Decimal('0.01'), message=_('Qiymat 0 dan katta bo‘lishi kerak.')))
                widget.attrs.setdefault('min', '0.01')
                widget.attrs.setdefault('step', '0.01')
            elif name in NOMANFIY_MAYDONLAR:
                field.validators.append(MinValueValidator(
                    Decimal('0'), message=_('Qiymat manfiy bo‘lishi mumkin emas.')))
                widget.attrs.setdefault('min', '0')
                widget.attrs.setdefault('step', '0.01')
            elif name in SON_MAYDONLAR:
                field.validators.append(MinValueValidator(
                    1, message=_('Soni kamida 1 bo‘lishi kerak.')))
                widget.attrs.setdefault('min', '1')

            if isinstance(field, forms.DateField):
                field.widget = forms.DateInput(
                    attrs={'type': 'date', 'class': 'input'}, format='%Y-%m-%d',
                )
                continue
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs['class'] = 'checkbox'
                continue
            if isinstance(widget, forms.Textarea):
                widget.attrs.setdefault('rows', 3)
            widget.attrs['class'] = (widget.attrs.get('class', '') + ' input').strip()


class KirimForm(StyledModelForm):
    """Investitsiya (faqat admin): sana, kimga (filial), summa, partiya."""

    class Meta:
        model = Kirim
        fields = ['sana', 'filial', 'summa', 'partiya']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['filial'].label = _('Kimga (filial)')
        self.fields['filial'].required = True


class RasxodForm(StyledModelForm):
    """Rasxod: sana, sabab (tanlanadi), summa."""

    class Meta:
        model = Rasxod
        fields = ['sana', 'kategoriya', 'summa']


class MaoshForm(StyledModelForm):
    """Maosh: hodim, sana, summa."""

    class Meta:
        model = Maosh
        fields = ['hodim', 'sana', 'summa']


class JojaHaridForm(StyledModelForm):
    """Joja haridi (sotib olish). tur avtomatik 'qoshildi'."""

    class Meta:
        model = JojaHarakat
        fields = ['sana', 'jins', 'soni', 'dona_narxi', 'partiya', 'izoh']


class JojaNobudForm(StyledModelForm):
    """Joja holati — nobud bo'ldi. Harakat turi faqat 'nobud bo'ldi'."""

    class Meta:
        model = JojaHarakat
        fields = ['sana', 'jins', 'tur', 'soni', 'partiya', 'izoh']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tur'].choices = [
            (JojaHarakat.Tur.KASAL.value, JojaHarakat.Tur.KASAL.label),
        ]
        if not self.initial.get('tur'):
            self.initial['tur'] = JojaHarakat.Tur.KASAL


class JojaVaznForm(StyledModelForm):
    class Meta:
        model = JojaVazn
        fields = ['sana', 'jins', 'ortacha_vazn', 'birlik', 'izoh']


class PartiyaForm(StyledModelForm):
    class Meta:
        model = Partiya
        fields = ['nomi', 'filial', 'sana', 'faol', 'izoh']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['filial'].required = True


class JojaOchirishForm(StyledModelForm):
    """Jojalar — tuxumdan ochirilgan jojalar: sana, tuxum soni, ochilgan."""

    class Meta:
        model = JojaOchirish
        fields = ['sana', 'tuxum_soni', 'ochilgan', 'izoh']

    def clean(self):
        c = super().clean()
        t, o = c.get('tuxum_soni'), c.get('ochilgan')
        if t is not None and o is not None and o > t:
            self.add_error('ochilgan',
                           _('Ochilgan joja soni tuxum sonidan ko‘p bo‘lishi mumkin emas.'))
        return c


class JojaSotuvForm(StyledModelForm):
    """Joja sotuvi (tur avtomatik 'joja'). Manba: jojalar yoki tovuqlar bazasi."""

    class Meta:
        model = Sotuv
        fields = ['sana', 'manba', 'jins', 'soni', 'birlik_narxi', 'izoh']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['manba'].required = True
        self.fields['jins'].required = False

    def clean(self):
        c = super().clean()
        if c.get('manba') == Sotuv.Manba.TOVUQBAZA and not c.get('jins'):
            self.add_error('jins', _('Tovuqlar bazasidan sotishda tovuq yoki xo‘rozni tanlang.'))
        if c.get('manba') == Sotuv.Manba.JOJA:
            c['jins'] = ''  # jojalar manbasida jins kerak emas
        return c


class TuxumSotuvForm(StyledModelForm):
    """Tuxum sotuvi (tur avtomatik 'tuxum', sifat bilan)."""

    class Meta:
        model = Sotuv
        fields = ['sana', 'tuxum_sifati', 'soni', 'birlik_narxi', 'izoh']


class TuxumYigimForm(StyledModelForm):
    """Kunlik tuxum yig'imi: sana, partiya, soni, A-sifat, o'rtacha og'irlik."""

    class Meta:
        model = TuxumYigim
        fields = ['sana', 'partiya', 'soni', 'a_sifat', 'ortacha_vazn', 'izoh']

    def clean(self):
        c = super().clean()
        soni, a = c.get('soni'), c.get('a_sifat')
        if soni is not None and a is not None and a > soni:
            self.add_error('a_sifat', _('A-sifat tuxum soni yig‘ilgan jami tuxumdan ko‘p bo‘lishi mumkin emas.'))
        return c


class KunlikLogForm(StyledModelForm):
    """Partiya kunlik kuzatuvi: yem, suv, o'lim, tirik soni, og'irlik."""

    class Meta:
        model = KunlikLog
        fields = ['partiya', 'sana', 'tirik_soni', 'nobud',
                  'yem_berilgan', 'yem_kelgan', 'suv_berilgan', 'ortacha_vazn',
                  'harorat', 'yoruglik_lux', 'yoruglik_soat', 'izoh']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['partiya'].queryset = Partiya.objects.filter(faol=True)

    def clean(self):
        c = super().clean()
        tirik, nobud = c.get('tirik_soni'), c.get('nobud')
        if tirik is not None and nobud is not None and nobud > tirik:
            self.add_error('nobud', _('Nobud soni tirik qush sonidan ko‘p bo‘lishi mumkin emas.'))
        return c


class EmlashForm(StyledModelForm):
    """Emlash / dori / muolaja jurnali."""

    class Meta:
        model = Emlash
        fields = ['partiya', 'sana', 'tur', 'nomi', 'usul', 'doza', 'izoh']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['partiya'].queryset = Partiya.objects.filter(faol=True)


class FilialForm(StyledModelForm):
    class Meta:
        model = Filial
        fields = ['nomi', 'davlat', 'manzil', 'faol']


class XodimForm(StyledModelForm):
    """Filial xodimi (login/parolsiz): ism, lavozim, oylik."""

    class Meta:
        model = Xodim
        fields = ['ism', 'lavozim', 'oylik', 'telefon', 'filial', 'faol']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['filial'].required = True


class ProfilForm(StyledModelForm):
    """Foydalanuvchi o'z shaxsiy ma'lumotini tahrirlaydi (parolsiz)."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'telefon', 'rasm']


class ParolForm(PasswordChangeForm):
    """Parolni o'zgartirish (faqat super admin) — o'zbekcha matnlar, 'input' uslubida."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = _('Joriy parol')
        self.fields['new_password1'].label = _('Yangi parol')
        self.fields['new_password2'].label = _('Yangi parolni tasdiqlang')
        self.fields['new_password1'].help_text = _(
            'Kamida 8 ta belgi; faqat raqamlardan yoki juda oddiy so‘zdan iborat bo‘lmasin.')
        self.fields['new_password2'].help_text = ''
        for field in self.fields.values():
            field.widget.attrs['class'] = (
                field.widget.attrs.get('class', '') + ' input').strip()
