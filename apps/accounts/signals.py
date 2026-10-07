"""Tizimga kirish/chiqishni aktivlik jurnaliga yozadi."""

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from .models import Faoliyat


def _ip(request):
    if request is None:
        return ''
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR', '')


@receiver(user_logged_in)
def _kirish(sender, request, user, **kwargs):
    Faoliyat.objects.create(user=user, amal=Faoliyat.Amal.KIRISH, ip=_ip(request))


@receiver(user_logged_out)
def _chiqish(sender, request, user, **kwargs):
    if user is not None:
        Faoliyat.objects.create(user=user, amal=Faoliyat.Amal.CHIQISH, ip=_ip(request))
