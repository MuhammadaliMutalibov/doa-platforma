"""Ko'p-filiallilik: qaysi filial faol va ma'lumotni filialga qarab filtrlash.

- Oddiy hodim: doim o'z filiali (o'zgartira olmaydi).
- Super admin: yuqoridagi almashtirgichdan filial tanlaydi (yoki "Barcha filiallar").
"""

from apps.accounts.models import Filial

SESSION_KEY = 'active_filial_id'


def active_filial(request):
    """Hozir faol filial (yoki super admin uchun None = barcha filiallar)."""
    user = request.user
    if not user.is_authenticated:
        return None
    if not user.super_admin:
        return user.filial
    fid = request.session.get(SESSION_KEY)
    if fid:
        return Filial.objects.filter(pk=fid, faol=True).first()
    return None  # barcha filiallar


def scope_qs(request, qs):
    """QuerySet'ni faol filialga qarab cheklaydi."""
    user = request.user
    if not user.super_admin:
        return qs.filter(filial=user.filial)
    f = active_filial(request)
    return qs.filter(filial=f) if f else qs
