"""Kunlik hisobotni hoziroq barcha ulangan adminlarga yuboradi (cron uchun).

Masalan crontab: 0 21 * * *  cd /path && venv/bin/python manage.py telegram_hisobot
"""

from django.core.management.base import BaseCommand

from apps.accounts import telegram


class Command(BaseCommand):
    help = 'Kunlik Telegram hisobotini yuboradi'

    def handle(self, *args, **opts):
        n = telegram.hisobotni_hammaga_yubor()
        self.stdout.write(self.style.SUCCESS(f'{n} ta adminga hisobot yuborildi.'))
