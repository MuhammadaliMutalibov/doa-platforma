"""Dashboard statistikasi — USD, filialga qarab. Grafik/trend/donut ma'lumotlari ham."""

import datetime
from decimal import Decimal

from django.db.models import F, Sum
from django.utils import timezone

from apps.accounts.models import User
from apps.finance.models import Kirim, Maosh, Rasxod
from apps.sales.models import Sotuv

OY_NOM = ['Yan', 'Fev', 'Mar', 'Apr', 'May', 'Iyn', 'Iyl', 'Avg', 'Sen', 'Okt', 'Noy', 'Dek']


def _oy_boshi(yil, oy):
    return datetime.date(yil, oy, 1)


def _keyingi_oy(d):
    return _oy_boshi(d.year + 1, 1) if d.month == 12 else _oy_boshi(d.year, d.month + 1)


def _trend(hozir, oldin):
    """Foiz o'zgarish va yo'nalish (up/down)."""
    hozir = float(hozir or 0)
    oldin = float(oldin or 0)
    if oldin == 0:
        foiz = 100 if hozir > 0 else 0
    else:
        foiz = (hozir - oldin) / oldin * 100
    return {'foiz': abs(round(foiz)), 'up': hozir >= oldin, 'bor': (hozir or oldin)}


def dashboard_stats(filial=None):
    def scoped(model):
        qs = model.objects.all()
        return qs if filial is None else qs.filter(filial=filial)

    def summa(model, **flt):
        return scoped(model).filter(**flt).aggregate(s=Sum('summa'))['s'] or Decimal('0')

    def soni(model, **flt):
        return scoped(model).filter(**flt).aggregate(s=Sum('soni'))['s'] or 0

    def oy_summa(model, boshi, oxiri):
        return scoped(model).filter(sana__gte=boshi, sana__lt=oxiri).aggregate(s=Sum('summa'))['s'] or Decimal('0')

    kirim = summa(Kirim)
    rasxod = summa(Rasxod) + summa(Maosh)

    def tushum(tur=None, boshi=None, oxiri=None):
        qs = scoped(Sotuv)
        if tur is not None:
            qs = qs.filter(tur=tur)
        if boshi is not None:
            qs = qs.filter(sana__gte=boshi, sana__lt=oxiri)
        v = qs.aggregate(s=Sum(F('soni') * F('birlik_narxi')))['s']
        return float(v or 0)

    joja_tushum = tushum(Sotuv.Tur.JOJA)
    tuxum_tushum = tushum(Sotuv.Tur.TUXUM)
    jami_tushum = joja_tushum + tuxum_tushum
    joja_pct = round(joja_tushum / jami_tushum * 100) if jami_tushum else 0
    tuxum_pct = 100 - joja_pct if jami_tushum else 0

    # Sof foyda = Tushum − Rasxod (sotuvdan haqiqiy foyda)
    sof_foyda = Decimal(str(jami_tushum)) - rasxod
    # Balans = Investitsiya − Rasxod + Tushum
    balans = kirim - rasxod + Decimal(str(jami_tushum))

    from . import stock

    # --- Oxirgi 6 oy (bar chart) ---
    bugun = timezone.localdate()
    y, m = bugun.year, bugun.month
    seq = []
    for i in range(5, -1, -1):
        yy, mm = y, m - i
        while mm <= 0:
            mm += 12
            yy -= 1
        seq.append((yy, mm))
    maxv = 1.0
    oraliq = []
    for (yy, mm) in seq:
        b = _oy_boshi(yy, mm)
        o = _keyingi_oy(b)
        inv = float(oy_summa(Kirim, b, o))
        rx = float(oy_summa(Rasxod, b, o) + oy_summa(Maosh, b, o))
        tsh = tushum(None, b, o)
        oraliq.append((mm, inv, rx, tsh))
        maxv = max(maxv, inv, rx)
    oylik = []
    for (mm, inv, rx, tsh) in oraliq:
        oylik.append({
            'nom': OY_NOM[mm - 1],
            'inv': inv, 'rasxod': rx,
            'inv_h': max(round(inv / maxv * 100), 2) if inv else 0,
            'rasxod_h': max(round(rx / maxv * 100), 2) if rx else 0,
        })

    # --- Trend (shu oy / o'tgan oy) ---
    inv_bu, rx_bu, tsh_bu = oraliq[-1][1], oraliq[-1][2], oraliq[-1][3]
    inv_ol, rx_ol, tsh_ol = oraliq[-2][1], oraliq[-2][2], oraliq[-2][3]

    hodimlar = User.objects.filter(is_active=True)
    if filial is not None:
        hodimlar = hodimlar.filter(filial=filial)

    return {
        'kirim': kirim,
        'rasxod': rasxod,
        'tushum': jami_tushum,
        'sof_foyda': sof_foyda,
        'balans': balans,
        'inv_trend': _trend(inv_bu, inv_ol),
        'rasxod_trend': _trend(rx_bu, rx_ol),
        'tushum_trend': _trend(tsh_bu, tsh_ol),
        'sof_foyda_trend': _trend(tsh_bu - rx_bu, tsh_ol - rx_ol),
        'balans_trend': _trend(inv_bu - rx_bu + tsh_bu, inv_ol - rx_ol + tsh_ol),
        'oylik': oylik,
        'joja_tushum': joja_tushum,
        'tuxum_tushum': tuxum_tushum,
        'jami_tushum': jami_tushum,
        'joja_pct': joja_pct,
        'tuxum_pct': tuxum_pct,
        'hodimlar_soni': hodimlar.count(),
        'tovuq_qoldiq': stock.tovuq_qoldiq(filial),
        'xoroz_qoldiq': stock.xoroz_qoldiq(filial),
        'joja_qoldiq': stock.joja_qoldiq(filial),
        'joja_sotuv_soni': scoped(Sotuv).filter(tur=Sotuv.Tur.JOJA).count(),
        'tuxum_sotuv_soni': scoped(Sotuv).filter(tur=Sotuv.Tur.TUXUM).count(),
        'oxirgi_sotuvlar': scoped(Sotuv).select_related('kiritgan')[:6],
        'oxirgi_rasxodlar': scoped(Rasxod).select_related('kategoriya')[:6],
    }
