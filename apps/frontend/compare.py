"""Davrlarni (oylarni) taqqoslash: tushum, rasxod, sof foyda, investitsiya
va ularning o'sish/kamayish ko'rsatkichlari."""

from datetime import date
from decimal import Decimal

from django.db.models import F, Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Taqqoslanadigan ko'rsatkichlar: (kalit, nomi, o'sish yaxshimi?)
METRIKALAR = [
    ('investitsiya', _('Investitsiya'), True),
    ('rasxod', _('Rasxod'), False),      # rasxod o'sishi — yomon
    ('tushum', _('Tushum'), True),
    ('sof_foyda', _('Sof foyda'), True),
]


def _oraliq(yil, oy):
    boshi = date(yil, oy, 1)
    oxiri = date(yil + 1, 1, 1) if oy == 12 else date(yil, oy + 1, 1)
    return boshi, oxiri


def _davr(filial, yil, oy):
    from apps.finance.models import Kirim, Maosh, Rasxod
    from apps.sales.models import Sotuv
    b, o = _oraliq(yil, oy)

    def scoped(model):
        qs = model.objects.filter(sana__gte=b, sana__lt=o)
        return qs if filial is None else qs.filter(filial=filial)

    inv = scoped(Kirim).aggregate(s=Sum('summa'))['s'] or Decimal('0')
    rasxod = ((scoped(Rasxod).aggregate(s=Sum('summa'))['s'] or Decimal('0'))
              + (scoped(Maosh).aggregate(s=Sum('summa'))['s'] or Decimal('0')))
    tushum = scoped(Sotuv).aggregate(s=Sum(F('soni') * F('birlik_narxi')))['s'] or Decimal('0')
    return {
        'investitsiya': inv, 'rasxod': rasxod, 'tushum': tushum,
        'sof_foyda': tushum - rasxod,
    }


def oylar_royxati(n=12):
    """Oxirgi n oy: har biri {'val': 'YYYY-MM', 'sana': date}."""
    bugun = timezone.localdate()
    y, m = bugun.year, bugun.month
    out = []
    for i in range(n):
        yy, mm = y, m - i
        while mm <= 0:
            mm += 12
            yy -= 1
        out.append({'val': f'{yy}-{mm:02d}', 'yil': yy, 'oy': mm, 'sana': date(yy, mm, 1)})
    return out


def _parse(val, default):
    try:
        y, m = val.split('-')
        return int(y), int(m)
    except (AttributeError, ValueError):
        return default


def taqqoslash(filial, d1_val=None, d2_val=None):
    """Ikki oyni taqqoslaydi. Standart: o'tgan oy (d1) vs bu oy (d2)."""
    oylar = oylar_royxati(12)
    bu_oy = (oylar[0]['yil'], oylar[0]['oy'])
    otgan = (oylar[1]['yil'], oylar[1]['oy']) if len(oylar) > 1 else bu_oy
    d1 = _parse(d1_val, otgan)
    d2 = _parse(d2_val, bu_oy)

    m1 = _davr(filial, *d1)
    m2 = _davr(filial, *d2)

    satrlar = []
    for kalit, nom, yaxshi_osish in METRIKALAR:
        v1 = float(m1[kalit])
        v2 = float(m2[kalit])
        ozg = v2 - v1
        if v1:
            foiz = round(abs(ozg) / abs(v1) * 100)
        else:
            foiz = 100 if v2 else 0
        up = v2 > v1
        teng = abs(v2 - v1) < 0.005
        satrlar.append({
            'kalit': kalit, 'nom': nom,
            'v1': m1[kalit], 'v2': m2[kalit],
            'ozg': Decimal(str(ozg)), 'foiz': foiz,
            'up': up, 'teng': teng,
            # ijobiy = o'zgarish kompaniya uchun yaxshimi (rang uchun)
            'ijobiy': teng or (up == yaxshi_osish),
        })
    # Diagramma (tushum / rasxod / sof foyda uchun guruhli ustunlar)
    money = [s for s in satrlar if s['kalit'] in ('tushum', 'rasxod', 'sof_foyda')]
    qiymatlar = [abs(float(s['v1'])) for s in money] + [abs(float(s['v2'])) for s in money]
    maxv = max(qiymatlar + [1.0])
    chart = []
    for s in money:
        v1, v2 = float(s['v1']), float(s['v2'])
        chart.append({
            'nom': s['nom'], 'v1': s['v1'], 'v2': s['v2'],
            'h1': max(round(abs(v1) / maxv * 100), 1) if v1 else 0,
            'h2': max(round(abs(v2) / maxv * 100), 1) if v2 else 0,
        })

    return {
        'taqq_satrlar': satrlar,
        'taqq_chart': chart,
        'taqq_oylar': oylar,
        'd1': f'{d1[0]}-{d1[1]:02d}', 'd2': f'{d2[0]}-{d2[1]:02d}',
        'd1_sana': date(d1[0], d1[1], 1), 'd2_sana': date(d2[0], d2[1], 1),
    }
