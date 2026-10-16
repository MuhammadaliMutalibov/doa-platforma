"""Standart yem egri chizig'i (yoshga qarab) va real yem bilan solishtirish.

Tijorat tovuq zoti uchun o'rtacha kunlik yem iste'moli (g/bosh), yoshga (hafta) qarab.
"""

# Standart yem (hafta -> g/bosh/kun). Oraliqlar chiziqli interpolyatsiya.
_YEM = [
    (1, 13), (4, 30), (8, 45), (12, 58), (16, 68), (18, 75), (20, 85),
    (24, 100), (28, 110), (32, 115), (40, 113), (50, 112), (70, 110), (90, 108),
]


def _interp(pts, x):
    if x <= pts[0][0]:
        return pts[0][1]
    if x >= pts[-1][0]:
        return pts[-1][1]
    for i in range(1, len(pts)):
        x0, y0 = pts[i - 1]
        x1, y1 = pts[i]
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return pts[-1][1]


def standart_yem(hafta):
    """Standart kunlik yem (g/bosh) — berilgan yoshda."""
    if hafta is None:
        return None
    return round(_interp(_YEM, hafta), 1)


def yosh_hafta(partiya, sana):
    """Partiyaning berilgan sanadagi yoshi (hafta)."""
    if not partiya or not partiya.sana:
        return None
    return max(0, (sana - partiya.sana).days // 7)


def yem_grafik(partiya):
    """Hafta bo'yicha standart va real yem (g/bosh)."""
    from apps.inventory.models import KunlikLog
    real_map = {}
    oxiri = 40
    if partiya and partiya.sana:
        buckets = {}
        for log in KunlikLog.objects.filter(partiya=partiya):
            aw = max(0, (log.sana - partiya.sana).days // 7)
            buckets.setdefault(aw, []).append(log.yem_bosh)
            oxiri = max(oxiri, aw + 2)
        for aw, vals in buckets.items():
            real_map[aw] = round(sum(vals) / len(vals), 1)
    labels = list(range(1, oxiri + 1))
    return {
        'labels': labels,
        'standart': [standart_yem(w) for w in labels],
        'real': [real_map.get(w) for w in labels],
    }


def _nuqtalar(vals, W, H, pad, maxv):
    n = len(vals)
    if n < 2:
        return ''
    out = []
    for i, v in enumerate(vals):
        if v is None:
            continue
        x = pad + i / (n - 1) * (W - 2 * pad)
        y = H - pad - (v / maxv) * (H - 2 * pad)
        out.append(f'{x:.1f},{y:.1f}')
    return ' '.join(out)


def grafik_svg(grafik, W=720, H=240, pad=30, maxv=130):
    """Standart va real yem chiziqlari uchun SVG nuqtalari + o'q yorliqlari."""
    labels = grafik['labels']
    n = len(labels)
    x_labels = []
    step = max(1, round(n / 7))
    for i, w in enumerate(labels):
        if i % step == 0 or i == n - 1:
            x = pad + i / (n - 1) * (W - 2 * pad)
            x_labels.append({'x': round(x, 1), 'hafta': w})
    y_lines = []
    for frac in (0, 0.25, 0.5, 0.75, 1):
        y_lines.append({'y': round(H - pad - frac * (H - 2 * pad), 1), 'val': round(maxv * frac)})
    return {
        'W': W, 'H': H,
        'std_pts': _nuqtalar(grafik['standart'], W, H, pad, maxv),
        'real_pts': _nuqtalar(grafik['real'], W, H, pad, maxv),
        'x_labels': x_labels, 'y_lines': y_lines,
        'bor_real': any(v is not None for v in grafik['real']),
    }
