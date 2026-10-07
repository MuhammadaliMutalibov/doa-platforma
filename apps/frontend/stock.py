"""Ombor qoldiqlari — sotuvlarni hisobga olgan holda.

- Tovuqlar bazasi (tovuq/xo'roz): QOSHILDI − KASAL − (tovuqlar bazasidan joja sotuvi)
- Jojalar (ochirilgan): jami ochilgan − (jojalardan joja sotuvi)
"""

from django.db.models import Sum


def _joja_sotuv(filial=None, manba=None, jins=None):
    """Joja sotuvidan sotilgan dona (manba/jins bo'yicha)."""
    from apps.sales.models import Sotuv
    qs = Sotuv.objects.filter(tur=Sotuv.Tur.JOJA)
    if filial is not None:
        qs = qs.filter(filial=filial)
    if manba:
        qs = qs.filter(manba=manba)
    if jins:
        qs = qs.filter(jins=jins)
    return qs.aggregate(s=Sum('soni'))['s'] or 0


def tovuq_qoldiq(filial=None):
    from apps.inventory.models import Jins, JojaHarakat
    base = JojaHarakat.qoldiq(Jins.TOVUQ, filial)
    return base - _joja_sotuv(filial, 'tovuqbaza', 'tovuq')


def xoroz_qoldiq(filial=None):
    from apps.inventory.models import Jins, JojaHarakat
    base = JojaHarakat.qoldiq(Jins.XOROZ, filial)
    return base - _joja_sotuv(filial, 'tovuqbaza', 'xoroz')


def joja_qoldiq(filial=None):
    """Ochirilgan jojalar qoldig'i = jami ochilgan − jojalardan sotilgan."""
    from apps.inventory.models import JojaOchirish
    ochilgan = JojaOchirish.jami_ochilgan(filial)
    return ochilgan - _joja_sotuv(filial, 'joja')


def mavjud_qoldiq(filial, manba, jins=None):
    """Tanlangan manba bo'yicha hozirgi mavjud qoldiq (sotuvdan oldin tekshirish uchun)."""
    if manba == 'joja':
        return joja_qoldiq(filial)
    if manba == 'tovuqbaza':
        if jins == 'xoroz':
            return xoroz_qoldiq(filial)
        return tovuq_qoldiq(filial)
    return 0

def tuxum_qoldiq(filial=None):
    from apps.inventory.models import TuxumYigim
    from apps.sales.models import Sotuv
    qs_yigim = TuxumYigim.objects.all()
    qs_sotuv = Sotuv.objects.filter(tur=Sotuv.Tur.TUXUM)
    if filial is not None:
        qs_yigim = qs_yigim.filter(partiya__filial=filial)
        qs_sotuv = qs_sotuv.filter(filial=filial)
    yigim = qs_yigim.aggregate(s=Sum('soni'))['s'] or 0
    sotuv = qs_sotuv.aggregate(s=Sum('soni'))['s'] or 0
    return yigim - sotuv

