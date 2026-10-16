"""
Super admin yaratish (deploy paytida ishlatiladi).
Qiymatlar DJANGO_SUPERUSER_* muhit o'zgaruvchilaridan olinadi.
Idempotent: admin allaqachon bo'lsa, qayta yaratmaydi va parolni o'zgartirmaydi.
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "DJANGO_SUPERUSER_* muhit o'zgaruvchilaridan super admin yaratadi."

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')

        if not password:
            self.stdout.write(self.style.WARNING(
                'DJANGO_SUPERUSER_PASSWORD berilmagan — admin yaratilmadi.'
            ))
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'rol': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'filial': None,  # filialsiz = super admin
            },
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Super admin yaratildi: {username}'))
        else:
            self.stdout.write(f'Super admin allaqachon mavjud: {username}')
