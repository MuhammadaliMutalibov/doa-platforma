from django import template

from apps.common.utils import pul as _pul

register = template.Library()

FLAGS = {'uz': '🇺🇿', 'tr': '🇹🇷', 'ru': '🇷🇺', 'en': '🇬🇧'}
ENDONYMS = {'uz': 'Oʻzbekcha', 'tr': 'Türkçe', 'ru': 'Русский', 'en': 'English'}


@register.filter
def flag(code):
    """Til kodiga mos bayroq (emoji)."""
    return FLAGS.get(code, '🏳️')


@register.filter
def endonym(code):
    """Tilning o'z nomi (masalan 'ru' -> 'Русский')."""
    return ENDONYMS.get(code, code.upper())


@register.filter
def pul(qiymat):
    """Pulni $ va 2 kasr bilan ko'rsatadi: 0.15 -> $0.15, 50000 -> $50,000.00"""
    return _pul(qiymat)
