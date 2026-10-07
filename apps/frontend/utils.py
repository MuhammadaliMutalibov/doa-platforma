"""Yordamchi funksiyalar: IP, 24 soat qulfi, aktivlik jurnali."""

from datetime import timedelta

from django.utils import timezone

from apps.accounts.models import Faoliyat, Notification, User

TAHRIR_OYNA = timedelta(hours=24)


def client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def tahrirlash_mumkin(user, obj):
    """Super admin doim; filial hodimi faqat 24 soat ichida tahrirlay/o'chira oladi.
    Vaqt qulfiga ega bo'lmagan modellar (masalan Xodim) doim tahrirlanadi."""
    if not user.is_authenticated:
        return False
    if user.super_admin:
        return True
    if not hasattr(obj, 'yaratilgan'):
        return True
    yaratilgan = obj.yaratilgan
    if not yaratilgan:
        return False
    return timezone.now() - yaratilgan <= TAHRIR_OYNA


def notify(request, amal, xabar, havola='', filial=None):
    """Bildirishnoma yaratadi. O'zgarish qilgan odamga kelmaydi — boshqalarga boradi.
    - Super adminlar har qanday yangilikni oladi.
    - Filial foydalanuvchilari faqat o'z filialidagi yangilikni oladi.
    """
    from django.db.models import Q
    actor = request.user if request.user.is_authenticated else None
    oluvchilar = User.objects.filter(is_active=True)
    if actor is not None:
        oluvchilar = oluvchilar.exclude(pk=actor.pk)
    if filial is not None:
        oluvchilar = oluvchilar.filter(Q(filial__isnull=True) | Q(filial=filial))
    else:
        oluvchilar = oluvchilar.filter(filial__isnull=True)  # faqat super adminlar
    try:
        Notification.objects.bulk_create([
            Notification(oluvchi=u, actor=actor, amal=amal, xabar=xabar[:255], havola=havola)
            for u in oluvchilar
        ])
    except Exception:
        pass


def log_faoliyat(request, amal, tavsif=''):
    """Aktivlik jurnaliga yozuv qo'shadi."""
    try:
        Faoliyat.objects.create(
            user=request.user if request.user.is_authenticated else None,
            amal=amal,
            tavsif=tavsif[:255],
            ip=client_ip(request),
        )
    except Exception:
        pass
