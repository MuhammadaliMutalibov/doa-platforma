"""Shablonlarga faol filial va filiallar ro'yxatini uzatadi."""

from apps.accounts.models import Filial

from .tenancy import active_filial


def tenancy(request):
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        return {}
    ctx = {
        'active_filial': active_filial(request),
        'is_super_admin': request.user.super_admin,
    }
    if request.user.super_admin:
        ctx['filiallar'] = Filial.objects.filter(faol=True)
    # Bildirishnomalar (qo'ng'iroq)
    qs = request.user.bildirishnomalar.all()
    ctx['bildirishnoma_soni'] = qs.filter(oqilgan=False).count()
    ctx['bildirishnomalar'] = qs[:8]
    return ctx
