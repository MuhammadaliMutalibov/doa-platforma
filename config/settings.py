"""
DOA Nutrition — Django sozlamalari.
Maxfiy qiymatlar `.env` faylidan olinadi (django-environ).
"""

from pathlib import Path

import environ
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Muhit (.env) o'qish ---
env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_ALLOWED_HOSTS=(list, ['127.0.0.1', 'localhost']),
    SECURE_SSL=(bool, False),
)
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('DJANGO_SECRET_KEY')
DEBUG = env('DJANGO_DEBUG')
ALLOWED_HOSTS = env('DJANGO_ALLOWED_HOSTS')

# Tashqi tunnel (ngrok/cloudflared) orqali namoyish uchun — POST formalar ishlashi uchun kerak
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[
    'https://*.trycloudflare.com',
    'https://*.ngrok-free.app',
    'https://*.ngrok.io',
])

# --- Telegram bot ---
TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN', default='')
TELEGRAM_HISOBOT_SOATI = env.int('TELEGRAM_HISOBOT_SOATI', default=21)


# --- Ilovalar ---
INSTALLED_APPS = [
    # Unfold admin (django.contrib.admin dan OLDIN turishi shart)
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.simple_history',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Uchinchi tomon
    'axes',              # login bruteforce himoyasi
    'simple_history',    # o'zgarishlar tarixi (audit)

    # Loyiha ilovalari
    'apps.accounts',
    'apps.finance',
    'apps.inventory',
    'apps.sales',
    'apps.frontend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # production static
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    # AxesMiddleware eng oxirida turishi kerak
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.frontend.context.tenancy',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# --- Baza ---
# .env da DATABASE_URL bo'lsa (masalan PostgreSQL) o'sha ishlatiladi,
# bo'lmasa SQLite (ishlab chiqish uchun).
DATABASES = {
    'default': env.db_url(
        'DATABASE_URL',
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
    )
}


# --- Autentifikatsiya ---
AUTH_USER_MODEL = 'accounts.User'

# django-axes birinchi, keyin Django'ning odatiy backend'i
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'


# --- django-axes (bruteforce himoyasi) ---
AXES_FAILURE_LIMIT = 5          # 5 marta xato login → bloklash
AXES_COOLOFF_TIME = 1           # 1 soat bloklanadi
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_PARAMETERS = ['username', 'ip_address']


# --- Til va vaqt ---
LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# Platforma 4 tilda: o'zbek, turk, rus, ingliz
LANGUAGES = [
    ('uz', _('O‘zbekcha')),
    ('tr', _('Türkçe')),
    ('ru', _('Русский')),
    ('en', _('English')),
]
LOCALE_PATHS = [BASE_DIR / 'locale']


# --- Statik va media fayllar ---
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Productionда WhiteNoise (siqilgan + kesh-buster). Devда oddiy.
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {
        'BACKEND': (
            'django.contrib.staticfiles.storage.StaticFilesStorage'
            if DEBUG else
            'whitenoise.storage.CompressedManifestStaticFilesStorage'
        ),
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- Xavfsizlik (production) ---
SESSION_COOKIE_AGE = 60 * 60 * 8        # 8 soat
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

if env('SECURE_SSL'):
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# --- Unfold admin tema ---
UNFOLD = {
    'SITE_TITLE': 'DOA Nutrition',
    'SITE_HEADER': 'DOA Nutrition',
    'SITE_SUBHEADER': _('Boshqaruv paneli'),
    'SITE_SYMBOL': 'egg',
    'SHOW_HISTORY': True,
    'SHOW_LANGUAGES': True,
    'DASHBOARD_CALLBACK': 'config.dashboard.dashboard_callback',
    'COLORS': {
        'primary': {
            '50': '236 253 245', '100': '209 250 229', '200': '167 243 208',
            '300': '110 231 183', '400': '52 211 153', '500': '16 185 129',
            '600': '5 150 105', '700': '4 120 87', '800': '6 95 70',
            '900': '6 78 59', '950': '2 44 34',
        },
    },
    'SIDEBAR': {
        'show_search': True,
        'show_all_applications': False,
        'navigation': [
            {
                'title': _('Asosiy'),
                'separator': True,
                'items': [
                    {
                        'title': _('Boshqaruv paneli'),
                        'icon': 'dashboard',
                        'link': reverse_lazy('admin:index'),
                    },
                ],
            },
            {
                'title': _('Moliya'),
                'separator': True,
                'items': [
                    {
                        'title': _('Kirimlar'),
                        'icon': 'trending_up',
                        'link': reverse_lazy('admin:finance_kirim_changelist'),
                    },
                    {
                        'title': _('Rasxodlar'),
                        'icon': 'trending_down',
                        'link': reverse_lazy('admin:finance_rasxod_changelist'),
                    },
                    {
                        'title': _('Maoshlar'),
                        'icon': 'payments',
                        'link': reverse_lazy('admin:finance_maosh_changelist'),
                    },
                    {
                        'title': _('Rasxod kategoriyalari'),
                        'icon': 'category',
                        'link': reverse_lazy('admin:finance_rasxodkategoriya_changelist'),
                    },
                ],
            },
            {
                'title': _('Joja'),
                'separator': True,
                'items': [
                    {
                        'title': _('Partiyalar'),
                        'icon': 'inventory_2',
                        'link': reverse_lazy('admin:inventory_partiya_changelist'),
                    },
                    {
                        'title': _('Joja harakatlari'),
                        'icon': 'raven',
                        'link': reverse_lazy('admin:inventory_jojaharakat_changelist'),
                    },
                    {
                        'title': _('Joja vaznlari'),
                        'icon': 'monitor_weight',
                        'link': reverse_lazy('admin:inventory_jojavazn_changelist'),
                    },
                ],
            },
            {
                'title': _('Sotuv'),
                'separator': True,
                'items': [
                    {
                        'title': _('Sotuvlar'),
                        'icon': 'shopping_cart',
                        'link': reverse_lazy('admin:sales_sotuv_changelist'),
                    },
                ],
            },
            {
                'title': _('Boshqaruv'),
                'separator': True,
                'items': [
                    {
                        'title': _('Filiallar'),
                        'icon': 'apartment',
                        'link': reverse_lazy('admin:accounts_filial_changelist'),
                    },
                    {
                        'title': _('Hodimlar'),
                        'icon': 'group',
                        'link': reverse_lazy('admin:accounts_user_changelist'),
                    },
                ],
            },
        ],
    },
}
