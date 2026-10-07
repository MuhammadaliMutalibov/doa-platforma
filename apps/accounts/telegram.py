"""Telegram bot service: secure linking (one-time code), multilingual replies,
daily report and interactive queries (/balance, /eggs, ...).

Security: the bot only replies to super admins linked via a one-time code from
the site. The reply language follows each user's chosen language (/language).
"""

import json
import ssl
import time
import urllib.parse
import urllib.request

import certifi
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.translation import override

API = 'https://api.telegram.org/bot{token}/{method}'
_CTX = ssl.create_default_context(cafile=certifi.where())

# Til tanlash (reply keyboard) — yorliq -> kod
LANG_LABELS = {
    '🇺🇿 Oʻzbekcha': 'uz', '🇬🇧 English': 'en',
    '🇷🇺 Русский': 'ru', '🇹🇷 Türkçe': 'tr',
}
LANG_KB = [['🇺🇿 Oʻzbekcha', '🇬🇧 English'], ['🇷🇺 Русский', '🇹🇷 Türkçe']]
TILLAR = ('uz', 'en', 'ru', 'tr')

# Menyu tugmalari: (buyruq, emoji, tarjima qilinadigan yorliq)
MENU_ITEMS = [
    ('balance', '💰', 'Balans'),
    ('eggs', '🥚', 'Tuxumlar'),
    ('poultry', '🐔', 'Tovuqlar'),
    ('report', '📊', 'Hisobot'),
    ('language', '🌐', 'Til'),
    ('help', 'ℹ️', 'Yordam'),
]
# makemessages literal `_(...)` ni ko'radi — yorliqlar katalogga tushishi uchun:
_EXTRACT = (_('Balans'), _('Tuxumlar'), _('Tovuqlar'), _('Hisobot'), _('Til'), _('Yordam'))
_LABEL_MAP = None

# Ulanmagan chatlar uchun vaqtincha tanlangan til (bot jarayoni ichida)
_pending_lang = {}
_BOT_USERNAME = None

# --- Kodni taxmin qilishdan (brute-force) himoya ---
# Bitta chat 15 daqiqada 5 martadan ko'p noto'g'ri kod yubora olmaydi.
# Barcha chatlar bo'yicha 15 daqiqada 30 ta xato bo'lsa — barcha faol kodlar bekor qilinadi
# (hujumchi ko'p akkaunt ochib urinsa ham, 900 000 variantdan taxmin qilib ulgurmaydi).
URINISH_OYNA = 15 * 60
MAX_CHAT_XATO = 5
MAX_GLOBAL_XATO = 30
_chat_xatolar = {}    # chat_id -> [monotonic vaqtlar]
_global_xatolar = []  # [monotonic vaqtlar]


def _tozala(vaqtlar, endi):
    return [t for t in vaqtlar if endi - t < URINISH_OYNA]


def _chat_bloklangan(chat_id):
    endi = time.monotonic()
    v = _tozala(_chat_xatolar.get(chat_id, []), endi)
    _chat_xatolar[chat_id] = v
    return len(v) >= MAX_CHAT_XATO


def _xato_yoz(chat_id):
    """Noto'g'ri kod urinishini qayd etadi; global chegaradan oshsa kodlarni bekor qiladi."""
    global _global_xatolar
    endi = time.monotonic()
    _chat_xatolar.setdefault(chat_id, []).append(endi)
    _global_xatolar = _tozala(_global_xatolar, endi)
    _global_xatolar.append(endi)
    if len(_global_xatolar) >= MAX_GLOBAL_XATO:
        from apps.accounts.models import TelegramKod
        TelegramKod.objects.filter(ishlatilgan=False).update(ishlatilgan=True)
        _global_xatolar = []


def _token():
    return getattr(settings, 'TELEGRAM_BOT_TOKEN', '') or ''


def api(method, _timeout=25, **params):
    """Telegram API call (secure TLS). Returns None on error."""
    token = _token()
    if not token:
        return None
    url = API.format(token=token, method=method)
    data = urllib.parse.urlencode(
        {k: (json.dumps(v) if isinstance(v, (dict, list)) else v)
         for k, v in params.items() if v is not None}
    ).encode()
    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=_timeout, context=_CTX) as r:
            return json.load(r)
    except Exception:
        return None


def bot_username():
    # Qisqa timeout — tarmoq sekin bo'lsa ham sahifa qotib qolmaydi.
    # Faqat muvaffaqiyatli natija keshlanadi (vaqtinchalik xato bo'lsa keyin qayta urinadi).
    global _BOT_USERNAME
    if not _BOT_USERNAME:
        me = api('getMe', _timeout=4)
        if me and me.get('ok'):
            _BOT_USERNAME = me['result'].get('username', '')
    return _BOT_USERNAME or ''


def send_message(chat_id, text, keyboard=None):
    params = {'chat_id': chat_id, 'text': text,
              'parse_mode': 'HTML', 'disable_web_page_preview': True}
    if keyboard:
        params['reply_markup'] = {'keyboard': keyboard, 'resize_keyboard': True}
    return api('sendMessage', **params)


# ----------------------------------------------------------------------
#  Message builders (gettext — follow the active language)
# ----------------------------------------------------------------------
from apps.common.utils import pul as _pul  # noqa: E402


def menu():
    """Faol tildagi menyu tugmalari (yorliqlar tarjimada chiqadi)."""
    b = {cmd: f'{emoji} {_(word)}' for cmd, emoji, word in MENU_ITEMS}
    return [[b['balance'], b['eggs']], [b['poultry'], b['report']], [b['language'], b['help']]]


def _menu_label_map():
    """Barcha tillardagi tugma yorliqlari -> buyruq (bir marta hisoblanadi)."""
    global _LABEL_MAP
    if _LABEL_MAP is None:
        m = {}
        for lang in TILLAR:
            with override(lang):
                for cmd, emoji, word in MENU_ITEMS:
                    m[f'{emoji} {_(word)}'] = cmd
        _LABEL_MAP = m
    return _LABEL_MAP


def help_text():
    return (
        f'ℹ️ <b>{_("Buyruqlar")}</b>\n\n'
        f'/balance — {_("moliyaviy holat")}\n'
        f'/eggs — {_("tuxum qoldig‘i")}\n'
        f'/poultry — {_("tovuq/xo‘roz soni")}\n'
        f'/report — {_("to‘liq kunlik hisobot")}\n'
        f'/language — {_("tilni o‘zgartirish")}\n'
        f'/unlink — {_("botni akkauntdan uzish")}'
    )


def balance_text():
    from apps.frontend.stats import dashboard_stats
    st = dashboard_stats(None)
    return (
        f'💰 <b>{_("Moliyaviy holat")}</b>\n\n'
        f'📈 {_("Investitsiya")}: <b>{_pul(st["kirim"])}</b>\n'
        f'📉 {_("Rasxod")}: <b>{_pul(st["rasxod"])}</b>\n'
        f'🛒 {_("Tushum")}: <b>{_pul(st["jami_tushum"])}</b>\n'
        f'💵 {_("Sof foyda")}: <b>{_pul(st["sof_foyda"])}</b>\n'
        f'━━━━━━━━━━━━━━\n'
        f'⚖️ {_("Balans")}: <b>{_pul(st["balans"])}</b>'
    )


def egg_stock_text():
    from django.db.models import Sum

    from apps.inventory.models import TuxumYigim
    from apps.sales.models import Sotuv

    def s(qs):
        return qs.aggregate(x=Sum('soni'))['x'] or 0
    yig = s(TuxumYigim.objects.all())
    sot = s(Sotuv.objects.filter(tur=Sotuv.Tur.TUXUM))
    qoldiq = max(0, yig - sot)
    dona = _('dona')
    return (
        f'🥚 <b>{_("Tuxum holati")}</b>\n\n'
        f'{_("Yig‘ilgan")}: <b>{yig:,}</b> {dona}\n'
        f'{_("Sotilgan")}: <b>{sot:,}</b> {dona}\n'
        f'━━━━━━━━━━━━━━\n'
        f'📦 {_("Qoldiq")}: <b>{qoldiq:,}</b> {dona}'
    )


def poultry_text():
    from apps.frontend import stock
    tovuq = stock.tovuq_qoldiq(None)
    xoroz = stock.xoroz_qoldiq(None)
    joja = stock.joja_qoldiq(None)
    dona = _('dona')
    return (
        f'🐔 <b>{_("Parranda qoldig‘i")}</b>\n\n'
        f'{_("Tovuq")}: <b>{tovuq:,}</b> {dona}\n'
        f'{_("Xo‘roz")}: <b>{xoroz:,}</b> {dona}\n'
        f'{_("Jo‘ja")}: <b>{joja:,}</b> {dona}\n'
        f'━━━━━━━━━━━━━━\n'
        f'{_("Jami")}: <b>{tovuq + xoroz + joja:,}</b> {dona}'
    )


def daily_report_text():
    from apps.frontend import egg_kpi
    sana = timezone.localdate().strftime('%d.%m.%Y')
    kpi = egg_kpi.umumiy_kpi(None)
    samaradorlik = f'{kpi["ort_samaradorlik"]}%' if kpi['ort_samaradorlik'] is not None else '—'
    return '\n'.join([
        f'📊 <b>DOA Nutrition — {_("kunlik hisobot")}</b>\n<i>{sana}</i>\n',
        balance_text(), '',
        poultry_text(), '',
        egg_stock_text(), '',
        f'🥚 <b>{_("Tug‘uvchanlik")}</b>\n'
        f'{_("Bugun kutilayotgan tuxum")}: <b>{kpi["kutilgan_bugun"]:,}</b> {_("dona")}\n'
        f'{_("O‘rtacha samaradorlik")}: <b>{samaradorlik}</b>',
    ])


# ----------------------------------------------------------------------
#  Linking and update handling
# ----------------------------------------------------------------------
def _command(text):
    t = (text or '').strip()
    # Tarjima qilingan menyu tugmalari (har qanday tildagi)
    cmd = _menu_label_map().get(t)
    if cmd:
        return cmd
    # /buyruq ko'rinishi
    tl = t.lower().lstrip('/')
    for b in ('balance', 'eggs', 'poultry', 'report', 'help', 'start', 'unlink', 'language'):
        if tl == b or tl.startswith(b + ' ') or tl.startswith(b + '@'):
            return b
    return None


def _detect(frm):
    lc = (frm.get('language_code') or '')[:2]
    return lc if lc in TILLAR else 'uz'


def _ulangan_user(chat_id):
    from apps.accounts.models import TelegramUlanish
    return (TelegramUlanish.objects.filter(chat_id=chat_id, faol=True)
            .select_related('user').first())


def _link_attempt(chat_id, kod, frm, til):
    from apps.accounts.models import TelegramKod, TelegramUlanish
    rec = (TelegramKod.objects.filter(kod=(kod or '').strip(), ishlatilgan=False)
           .select_related('user').order_by('-yaratilgan').first())
    if not rec or not rec.yaroqli() or not rec.user.super_admin:
        return None
    rec.ishlatilgan = True
    rec.save(update_fields=['ishlatilgan'])
    ul, _c = TelegramUlanish.objects.update_or_create(
        chat_id=chat_id,
        defaults={'user': rec.user, 'faol': True, 'til': til,
                  'username': frm.get('username', ''), 'ism': frm.get('first_name', '')},
    )
    return ul


def process_update(update):
    """Handle one Telegram update (from long-polling)."""
    msg = update.get('message') or update.get('edited_message')
    if not msg:
        return
    chat_id = msg.get('chat', {}).get('id')
    frm = msg.get('from', {})
    text = msg.get('text', '') or ''
    if chat_id is None:
        return

    ul = _ulangan_user(chat_id)

    # Til tanlash (yorliq bosilganda)
    if text in LANG_LABELS:
        lang = LANG_LABELS[text]
        if ul:
            ul.til = lang
            ul.save(update_fields=['til'])
            with override(lang):
                send_message(chat_id, _('Til o‘zgartirildi.'), keyboard=menu())
        else:
            _pending_lang[chat_id] = lang
            with override(lang):
                send_message(chat_id, _('Davom etish uchun saytdan olingan bir martalik kodni yuboring.'))
        return

    lang = ul.til if ul else (_pending_lang.get(chat_id) or _detect(frm))
    with override(lang):
        _handle(chat_id, frm, text, ul)


def _handle(chat_id, frm, text, ul):
    cmd = _command(text)

    if cmd == 'language':
        send_message(chat_id, _('Tilni tanlang:'), keyboard=LANG_KB)
        return

    # Ulanmagan chat
    if ul is None:
        if cmd == 'start':
            send_message(chat_id,
                         f'👋 <b>DOA Nutrition</b>\n\n{_("Tilni tanlang:")}',
                         keyboard=LANG_KB)
            send_message(chat_id, _('Davom etish uchun saytdan olingan bir martalik kodni yuboring.'))
            return
        if _chat_bloklangan(chat_id):
            send_message(chat_id, _('Juda ko‘p noto‘g‘ri urinish. 15 daqiqadan keyin qayta urinib ko‘ring.'))
            return
        linked = _link_attempt(chat_id, text, frm, _pending_lang.get(chat_id, 'uz'))
        if linked:
            _chat_xatolar.pop(chat_id, None)
            with override(linked.til):
                send_message(chat_id,
                             f'✅ <b>{linked.user.get_full_name() or linked.user.username}</b> — '
                             + _('muvaffaqiyatli ulandingiz!'), keyboard=menu())
                send_message(chat_id, help_text())
        else:
            _xato_yoz(chat_id)
            send_message(chat_id, _('❌ Kod noto‘g‘ri yoki muddati o‘tgan. Saytdan yangi kod oling.'))
        return

    # Ulangan super admin — buyruqlar
    if cmd == 'unlink':
        ul.faol = False
        ul.save(update_fields=['faol'])
        send_message(chat_id, _('🔌 Bot akkauntingizdan uzildi. Qayta ulanish uchun /start.'))
    elif cmd == 'balance':
        send_message(chat_id, balance_text(), keyboard=menu())
    elif cmd == 'eggs':
        send_message(chat_id, egg_stock_text(), keyboard=menu())
    elif cmd == 'poultry':
        send_message(chat_id, poultry_text(), keyboard=menu())
    elif cmd == 'report':
        send_message(chat_id, daily_report_text(), keyboard=menu())
    elif cmd in ('start', 'help'):
        send_message(chat_id, help_text(), keyboard=menu())
    else:
        send_message(chat_id, _('Tushunarsiz buyruq. /help — yordam.'), keyboard=menu())


def _html(s):
    return (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def yangi_bildirishnomalarni_yubor():
    """Yuborilmagan bildirishnomalarni ulangan adminlarga (ularning tilida) yuboradi."""
    from apps.accounts.models import Notification, TelegramUlanish
    # Ulanishlarni bir marta olib, foydalanuvchi bo'yicha guruhlaymiz (N+1 yo'q)
    by_user = {}
    for ul in TelegramUlanish.objects.filter(faol=True):
        by_user.setdefault(ul.user_id, []).append(ul)
    if not by_user:
        return 0
    qs = (Notification.objects.filter(telegram_yuborildi=False, oluvchi_id__in=by_user.keys())
          .order_by('vaqt')[:50])
    n = 0
    for note in qs:
        for ul in by_user.get(note.oluvchi_id, []):
            with override(ul.til):
                send_message(ul.chat_id, f'🔔 <b>{_("Yangilik")}</b>\n{_html(note.xabar)}')
        note.telegram_yuborildi = True
        note.save(update_fields=['telegram_yuborildi'])
        n += 1
    return n


def hisobotni_hammaga_yubor():
    """Kunlik hisobotni barcha faol ulangan adminlarga (tilida) yuboradi."""
    from apps.accounts.models import TelegramUlanish
    n = 0
    for ul in TelegramUlanish.objects.filter(faol=True):
        with override(ul.til):
            send_message(ul.chat_id, daily_report_text())
        n += 1
    return n
