"""Telegram botni long-polling rejimida ishga tushiradi.

- Kelgan xabarlarni qayta ishlaydi (/start, kod, /balans, ...)
- Yangi bildirishnomalarni ulangan adminlarga yuboradi
- Har kuni belgilangan soatda (TELEGRAM_HISOBOT_SOATI) kunlik hisobot yuboradi

Ishga tushirish:  python manage.py telegrambot
"""

import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts import telegram


class Command(BaseCommand):
    help = 'Telegram botni long-polling rejimida ishga tushiradi'

    def handle(self, *args, **opts):
        if not telegram._token():
            self.stderr.write('TELEGRAM_BOT_TOKEN topilmadi (.env).')
            return
        me = telegram.api('getMe')
        if not me or not me.get('ok'):
            self.stderr.write('Telegram API ulanmadi. Token/tarmoqni tekshiring.')
            return
        bot = me['result'].get('username')
        self.stdout.write(self.style.SUCCESS(f'@{bot} ishga tushdi. Ctrl+C — to‘xtatish.'))

        offset = None
        soat = getattr(settings, 'TELEGRAM_HISOBOT_SOATI', 21)
        oxirgi_hisobot = None

        while True:
            try:
                res = telegram.api('getUpdates', _timeout=35, offset=offset, timeout=30)
                if res and res.get('ok'):
                    for upd in res['result']:
                        offset = upd['update_id'] + 1
                        try:
                            telegram.process_update(upd)
                        except Exception as e:
                            self.stderr.write(f'update xato: {e}')
                # Yangi bildirishnomalarni yuborish
                try:
                    telegram.yangi_bildirishnomalarni_yubor()
                except Exception as e:
                    self.stderr.write(f'bildirishnoma xato: {e}')
                # Kunlik hisobot (bir kunda bir marta, belgilangan soatdan keyin)
                endi = timezone.localtime()
                if endi.hour >= soat and oxirgi_hisobot != endi.date():
                    try:
                        telegram.hisobotni_hammaga_yubor()
                        oxirgi_hisobot = endi.date()
                        self.stdout.write(f'Kunlik hisobot yuborildi: {endi.date()}')
                    except Exception as e:
                        self.stderr.write(f'hisobot xato: {e}')
            except KeyboardInterrupt:
                self.stdout.write('To‘xtatildi.')
                break
            except Exception as e:
                self.stderr.write(f'tsikl xato: {e}')
                time.sleep(3)
