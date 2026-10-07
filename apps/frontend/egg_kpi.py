"""Tuxum tug'uvchanlik (HDEP) prognozi va samaradorlik algoritmlari.

Har bir partiyaning yoshi (hafta) va tovuqlar sonidan kelib chiqib kunlik
kutilayotgan tuxum miqdorini hisoblaydi hamda real yig'im bilan solishtiradi.
Zot standarti — tijorat tuxum zotining (brown layer) o'rtacha HDEP egri chizig'i.
"""

from datetime import timedelta

from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Standart HDEP egri chizig'i (hafta -> tug'uvchanlik %). Oraliqlar chiziqli interpolyatsiya.
_HDEP_NUQTALAR = [
    (0, 0), (17, 0), (18, 5), (19, 25), (20, 55), (21, 75), (22, 85),
    (23, 90), (24, 93), (25, 94), (30, 95), (40, 91), (50, 87),
    (60, 82), (70, 76), (80, 70), (90, 64),
]
# Standart tana vazni (hafta -> kg)
_VAZN_NUQTALAR = [
    (18, 1.45), (20, 1.55), (22, 1.65), (25, 1.75), (30, 1.90),
    (40, 1.95), (50, 1.98), (70, 2.00),
]


def _interp(nuqtalar, x):
    if x <= nuqtalar[0][0]:
        return nuqtalar[0][1]
    if x >= nuqtalar[-1][0]:
        return nuqtalar[-1][1]
    for i in range(1, len(nuqtalar)):
        x0, y0 = nuqtalar[i - 1]
        x1, y1 = nuqtalar[i]
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return nuqtalar[-1][1]


def standart_hdep(hafta):
    """Zot standarti bo'yicha kutilayotgan HDEP (%) — berilgan yoshda."""
    return round(_interp(_HDEP_NUQTALAR, hafta), 1)


def maqsad_vazn(hafta):
    """Standart tana vazni (kg) — berilgan yoshda."""
    return round(_interp(_VAZN_NUQTALAR, hafta), 2)


def tirik_tovuq(partiya):
    """Partiyadagi tirik tovuqlar soni = qo'shilgan − nobud bo'lgan."""
    from django.db.models import Sum

    from apps.inventory.models import Jins, JojaHarakat
    q = JojaHarakat.objects.filter(partiya=partiya, jins=Jins.TOVUQ)
    plus = q.filter(tur=JojaHarakat.Tur.QOSHILDI).aggregate(s=Sum('soni'))['s'] or 0
    minus = q.filter(tur=JojaHarakat.Tur.KASAL).aggregate(s=Sum('soni'))['s'] or 0
    return plus - minus


def oxirgi_vazn_kg(filial):
    """Filialdagi tovuqning oxirgi o'rtacha vazni (kg), bo'lmasa None."""
    from apps.inventory.models import Jins, JojaVazn, Ogirlik
    qs = JojaVazn.objects.filter(jins=Jins.TOVUQ)
    if filial is not None:
        qs = qs.filter(filial=filial)
    v = qs.order_by('-sana').first()
    if not v:
        return None
    w = float(v.ortacha_vazn)
    return round(w / 1000, 3) if v.birlik == Ogirlik.GRAM else w


def _yosh_hafta(partiya):
    if not partiya.sana:
        return None
    return max(0, (timezone.localdate() - partiya.sana).days // 7)


def _real_hdep_oxirgi(partiya, tirik):
    """Oxirgi 7 kundagi o'rtacha real HDEP (%), ma'lumot bo'lmasa None."""
    from django.db.models import Sum

    from apps.inventory.models import TuxumYigim
    if tirik <= 0:
        return None
    bugun = timezone.localdate()
    qs = TuxumYigim.objects.filter(partiya=partiya, sana__gte=bugun - timedelta(days=7))
    jami = qs.aggregate(s=Sum('soni'))['s']
    kunlar = qs.values('sana').distinct().count()
    if not jami or kunlar == 0:
        return None
    return round((jami / kunlar) / tirik * 100, 1)


def _signal(std_hdep, real_hdep):
    """Samaradorlik signali + tavsiya."""
    if real_hdep is None:
        return ('kutilmoqda', _('Real yig‘im kiritilmagan'))
    if std_hdep <= 0:
        return ('kutilmoqda', _('Hali tug‘ish yoshida emas'))
    nisbat = real_hdep / std_hdep
    if nisbat >= 0.95:
        return ('yaxshi', _('A’lo — standartga mos'))
    if nisbat >= 0.85:
        return ('etibor', _('E’tibor bering — yem/yorug‘likni tekshiring'))
    return ('past', _('Past — rasion, yorug‘lik yoki yoshni ko‘rib chiqing'))


def partiya_tahlili(filial=None):
    """Har bir faol partiya uchun prognoz va samaradorlik ko'rsatkichlari.
    N+1 oldini olish uchun tirik tovuq va oxirgi yig'im guruhli (bitta) so'rovda olinadi."""
    from django.db.models import Count, Q, Sum

    from apps.inventory.models import Jins, JojaHarakat, Partiya, TuxumYigim
    qs = Partiya.objects.filter(faol=True)
    if filial is not None:
        qs = qs.filter(filial=filial)
    partiyalar = list(qs)
    ids = [p.pk for p in partiyalar]
    vazn = oxirgi_vazn_kg(filial)
    bugun = timezone.localdate()

    # Tirik tovuq — bitta so'rov (barcha partiyalar bo'yicha)
    tirik_map = {}
    if ids:
        for row in (JojaHarakat.objects.filter(jins=Jins.TOVUQ, partiya_id__in=ids)
                    .values('partiya_id')
                    .annotate(plus=Sum('soni', filter=Q(tur=JojaHarakat.Tur.QOSHILDI)),
                              minus=Sum('soni', filter=Q(tur=JojaHarakat.Tur.KASAL)))):
            tirik_map[row['partiya_id']] = (row['plus'] or 0) - (row['minus'] or 0)

    # Oxirgi 7 kun yig'imi — bitta so'rov
    yigim_map = {}
    if ids:
        for row in (TuxumYigim.objects
                    .filter(partiya_id__in=ids, sana__gte=bugun - timedelta(days=7))
                    .values('partiya_id')
                    .annotate(jami=Sum('soni'), kunlar=Count('sana', distinct=True))):
            yigim_map[row['partiya_id']] = (row['jami'] or 0, row['kunlar'] or 0)

    natija = []
    for p in partiyalar:
        yosh = _yosh_hafta(p)
        tirik = tirik_map.get(p.pk, 0)
        std = standart_hdep(yosh) if yosh is not None else None
        # vazn faktori: kam vaznli bo'lsa kutilayotgan kamayadi
        vf = 1.0
        if vazn and yosh is not None:
            vf = max(0.85, min(1.0, vazn / (maqsad_vazn(yosh) or 1)))
        kutilgan = int(round(tirik * (std or 0) / 100 * vf)) if (std and tirik > 0) else 0
        real = None
        yg = yigim_map.get(p.pk)
        if yg and tirik > 0 and yg[1] > 0 and yg[0]:
            real = round((yg[0] / yg[1]) / tirik * 100, 1)
        samaradorlik = round(real / std * 100) if (real is not None and std) else None
        sig, tavsiya = _signal(std or 0, real)
        natija.append({
            'partiya': p, 'yosh': yosh, 'tirik': tirik, 'vazn': vazn,
            'std_hdep': std, 'real_hdep': real, 'kutilgan': kutilgan,
            'samaradorlik': samaradorlik, 'signal': sig, 'tavsiya': tavsiya,
        })
    return natija


def hdep_grafik(partiya):
    """Chiziqli grafik uchun: hafta bo'yicha standart va real HDEP (%)."""
    boshi = 16
    real_map = {}
    if partiya and partiya.sana:
        yosh = _yosh_hafta(partiya)
        oxiri = max(30, (yosh or 0) + 2)
        tirik = tirik_tovuq(partiya)
        if tirik > 0:
            from apps.inventory.models import TuxumYigim
            buckets = {}
            for y in TuxumYigim.objects.filter(partiya=partiya):
                aw = (y.sana - partiya.sana).days // 7
                buckets.setdefault(aw, []).append(y.soni)
            for aw, vals in buckets.items():
                real_map[aw] = round((sum(vals) / len(vals)) / tirik * 100, 1)
    else:
        oxiri = 80
    labels, std, real = [], [], []
    for w in range(boshi, oxiri + 1):
        labels.append(w)
        std.append(standart_hdep(w))
        real.append(real_map.get(w))
    return {'labels': labels, 'standart': std, 'real': real}


def _nuqtalar(qiymatlar, W, H, pad):
    """Qiymatlarni (0..100%) SVG koordinatalariga aylantiradi."""
    n = len(qiymatlar)
    if n < 2:
        return ''
    pts = []
    for i, v in enumerate(qiymatlar):
        if v is None:
            continue
        x = pad + i / (n - 1) * (W - 2 * pad)
        y = H - pad - (v / 100) * (H - 2 * pad)
        pts.append(f'{x:.1f},{y:.1f}')
    return ' '.join(pts)


def grafik_svg(grafik, W=720, H=240, pad=30):
    """Standart va real chiziqlar uchun SVG polyline nuqtalari + o'q yorliqlari."""
    std_pts = _nuqtalar(grafik['standart'], W, H, pad)
    real_pts = _nuqtalar(grafik['real'], W, H, pad)
    labels = grafik['labels']
    n = len(labels)
    # x o'qi yorliqlari (har 4-haftada)
    x_labels = []
    step = max(1, round(n / 7))
    for i, w in enumerate(labels):
        if i % step == 0 or i == n - 1:
            x = pad + i / (n - 1) * (W - 2 * pad)
            x_labels.append({'x': round(x, 1), 'hafta': w})
    # y o'qi chiziqlari (0,25,50,75,100%)
    y_lines = []
    for v in (0, 25, 50, 75, 100):
        y = H - pad - (v / 100) * (H - 2 * pad)
        y_lines.append({'y': round(y, 1), 'val': v})
    bor_real = any(v is not None for v in grafik['real'])
    return {'W': W, 'H': H, 'std_pts': std_pts, 'real_pts': real_pts,
            'x_labels': x_labels, 'y_lines': y_lines, 'bor_real': bor_real}


def umumiy_kpi(filial=None, tahlil=None):
    """Umumiy ko'rsatkichlar: bugun kutilayotgan tuxum, o'rtacha samaradorlik, eng yaxshi/past.
    `tahlil` berilsa qayta hisoblamaydi (ikki marta so'rov yubormaslik uchun)."""
    if tahlil is None:
        tahlil = partiya_tahlili(filial)
    kutilgan_bugun = sum(t['kutilgan'] for t in tahlil)
    samaralar = [t['samaradorlik'] for t in tahlil if t['samaradorlik'] is not None]
    ort_samaradorlik = round(sum(samaralar) / len(samaralar)) if samaralar else None
    bahobor = [t for t in tahlil if t['samaradorlik'] is not None]
    eng_yaxshi = max(bahobor, key=lambda t: t['samaradorlik']) if bahobor else None
    eng_past = min(bahobor, key=lambda t: t['samaradorlik']) if bahobor else None
    return {
        'kutilgan_bugun': kutilgan_bugun,
        'ort_samaradorlik': ort_samaradorlik,
        'eng_yaxshi': eng_yaxshi, 'eng_past': eng_past,
        'partiya_soni': len(tahlil),
    }
