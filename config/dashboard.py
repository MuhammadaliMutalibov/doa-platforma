"""Unfold admin boshqaruv paneli — statistikani frontend.stats dan oladi."""

from apps.frontend.stats import dashboard_stats


def dashboard_callback(request, context):
    filial = None if request.user.super_admin else request.user.filial
    s = dashboard_stats(filial)
    context.update({
        'doa_kirim': s['kirim'],
        'doa_rasxod': s['rasxod'],
        'doa_balans': s['balans'],
        'doa_hodimlar_soni': s['hodimlar_soni'],
        'doa_tovuq_qoldiq': s['tovuq_qoldiq'],
        'doa_xoroz_qoldiq': s['xoroz_qoldiq'],
        'doa_joja_sotuv': s['joja_sotuv_soni'],
        'doa_tuxum_sotuv': s['tuxum_sotuv_soni'],
    })
    return context
