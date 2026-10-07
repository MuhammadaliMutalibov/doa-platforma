from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import F, Sum
from django.http import Http404, HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from apps.accounts.models import Faoliyat, Filial, Xodim
from apps.common.utils import pul as _pul
from apps.finance.models import Kirim, Maosh, Rasxod
from apps.inventory.models import (Jins, JojaHarakat, JojaOchirish, JojaVazn,
                                    Partiya, TuxumYigim)
from apps.sales.models import Sotuv

from . import compare, egg_kpi, forms
from .stats import dashboard_stats
from .tenancy import SESSION_KEY, active_filial, scope_qs
from .utils import log_faoliyat, notify, tahrirlash_mumkin


# ============================================================
#  Auth
# ============================================================
class LoginView(auth_views.LoginView):
    template_name = 'frontend/login.html'
    redirect_authenticated_user = True


class LogoutView(auth_views.LogoutView):
    pass


@login_required
def dashboard(request):
    # Birinchi ishga tushirish: super adminda hali filial bo'lmasa — ko'rsatma beramiz
    filial_yoq = request.user.super_admin and not Filial.objects.exists()
    return render(request, 'frontend/dashboard.html', {
        'stats': dashboard_stats(active_filial(request)),
        'sahifa': 'dashboard',
        'filial_yoq': filial_yoq,
    })


@login_required
def set_filial(request):
    """Super admin yuqoridan filialni almashtiradi (sessiyada saqlanadi)."""
    if request.method == 'POST' and request.user.super_admin:
        val = request.POST.get('filial')
        if val and val != 'all':
            request.session[SESSION_KEY] = int(val)
        else:
            request.session.pop(SESSION_KEY, None)
    return redirect(request.META.get('HTTP_REFERER') or '/')


class ProfilView(LoginRequiredMixin, UpdateView):
    """Foydalanuvchi o'z shaxsiy ma'lumotini tahrirlaydi (parol emas)."""

    form_class = forms.ProfilForm
    template_name = 'frontend/object_form.html'
    success_url = reverse_lazy('profil')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, _('Shaxsiy ma’lumotlaringiz saqlandi.'))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({'page_title': _('Shaxsiy ma\'lumotlar'), 'sahifa': 'profil', 'cancel_url': '/'})
        return ctx


# ============================================================
#  Umumiy asoslar
# ============================================================
class FrontListView(LoginRequiredMixin, ListView):
    template_name = 'frontend/object_list.html'
    paginate_by = 25
    headers = []
    page_title = ''
    sahifa = ''
    add_url = None
    edit_url = None
    del_model = None   # o'chirish uchun model nomi (masalan 'kirim')
    select_related = ()
    eksport = False    # True bo'lsa — Excel eksport tugmasi ko'rinadi

    def cells(self, obj):
        raise NotImplementedError

    # --- Excel (.xlsx) eksport: jadvaldagidek rangli, filter yoki hammasi ---
    _TAG_RANG = [
        ('tag-in', 'green'), ('sig-yaxshi', 'green'),
        ('tag-out', 'red'), ('sig-past', 'red'),
        ('tag-egg', 'amber'), ('sig-etibor', 'amber'),
        ('tag-chick', 'orange'),
    ]

    def _hujayra(self, cell):
        """Hujayra qiymatini (matn, rang) ko'rinishiga keltiradi — saytdagidek."""
        import datetime

        from django.utils.formats import date_format
        from django.utils.html import strip_tags
        if cell is None:
            return ('', None)
        if isinstance(cell, (datetime.date, datetime.datetime)):
            return (date_format(cell, 'DATE_FORMAT', use_l10n=True), None)
        html = str(cell)
        rang = None
        for cls, c in self._TAG_RANG:
            if cls in html:
                rang = c
                break
        return (strip_tags(html).strip(), rang)

    def post(self, request, *args, **kwargs):
        if not self.eksport:
            return HttpResponseNotAllowed(['GET'])
        import json

        from .export_xlsx import qil_xlsx
        try:
            body = json.loads(request.body or b'{}')
        except (ValueError, TypeError):
            body = {}
        if not isinstance(body, dict):
            body = {}
        mode = body.get('mode', 'all')
        fil = {}
        if mode == 'filter':
            raw = body.get('filters')
            if isinstance(raw, dict):
                for k, v in raw.items():
                    try:
                        if isinstance(v, (list, tuple)):
                            fil[int(k)] = {str(x) for x in v}
                    except (ValueError, TypeError):
                        continue
        rows = []
        for o in self.get_queryset():
            cells = [self._hujayra(c) for c in self.cells(o)]
            if fil:
                mos = all((ci >= len(cells)) or (cells[ci][0] in allowed)
                          for ci, allowed in fil.items())
                if not mos:
                    continue
            rows.append(cells)
        headers = [str(h) for h in self.headers]
        data = qil_xlsx(str(self.page_title), headers, rows)
        resp = HttpResponse(
            data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = f'attachment; filename="DOA-{self.sahifa or "hisobot"}.xlsx"'
        log_faoliyat(request, Faoliyat.Amal.QOSHISH, f'Excel eksport: {self.page_title}')
        return resp

    def get_queryset(self):
        qs = self.model._default_manager.all()
        if self.select_related:
            qs = qs.select_related(*self.select_related)
        return scope_qs(self.request, qs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['headers'] = self.headers
        rows = []
        for o in ctx['object_list']:
            ok = tahrirlash_mumkin(self.request.user, o)
            rows.append({
                'cells': self.cells(o),
                'edit_url': reverse(self.edit_url, args=[o.pk]) if (self.edit_url and ok) else None,
                'del_url': reverse('ochirish', args=[self.del_model, o.pk]) if (self.del_model and ok) else None,
            })
        ctx['rows'] = rows
        ctx['page_title'] = self.page_title
        ctx['sahifa'] = self.sahifa
        ctx['add_url'] = reverse(self.add_url) if self.add_url else None
        ctx['eksport'] = self.eksport
        return ctx


class FrontFormMixin(LoginRequiredMixin):
    template_name = 'frontend/object_form.html'
    page_title = ''
    sahifa = ''
    cancel_url = None
    explicit_filial = False  # True: filial formada tanlanadi (avto-belgilanmaydi)

    def dispatch(self, request, *args, **kwargs):
        # Tahrirlash: 24 soat qulfi (filial hodimi uchun)
        if 'pk' in kwargs and request.user.is_authenticated:
            obj = self.get_object()
            if not tahrirlash_mumkin(request.user, obj):
                messages.warning(request, _('Bu yozuvni o‘zgartirish muddati (24 soat) tugagan.'))
                return redirect(reverse(self.cancel_url) if self.cancel_url else '/')
        # Super admin "Barcha filiallar"da turib yozuv qo'sha olmaydi — filial tanlashi kerak
        if (not self.explicit_filial and request.user.is_authenticated
                and request.user.super_admin and active_filial(request) is None):
            messages.warning(request, _('Yozuv qo‘shish uchun avval yuqoridan filial tanlang.'))
            return redirect(reverse(self.cancel_url) if self.cancel_url else '/')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.explicit_filial:
            return super().get_queryset()
        # Faqat o'z filialidagi yozuvni tahrirlash mumkin
        return scope_qs(self.request, super().get_queryset())

    def get_form(self, form_class=None):
        from apps.accounts.models import Filial
        form = super().get_form(form_class)
        if 'filial' in form.fields:
            form.fields['filial'].queryset = Filial.objects.filter(faol=True)
        f = active_filial(self.request)
        if f is not None and not self.explicit_filial:
            if 'hodim' in form.fields:
                form.fields['hodim'].queryset = form.fields['hodim'].queryset.filter(filial=f)
            if 'partiya' in form.fields:
                form.fields['partiya'].queryset = form.fields['partiya'].queryset.filter(filial=f, faol=True)
        return form

    def form_valid(self, form):
        yangi = self.object is None
        inst = form.instance
        if hasattr(inst, 'kiritgan') and getattr(inst, 'kiritgan_id', None) is None:
            inst.kiritgan = self.request.user
        # filial_id orqali tekshiramiz: majburiy (null=False) FK da hasattr(inst,'filial')
        # yozuv hali bo'sh bo'lsa False qaytaradi, shuning uchun filial_id ishlatiladi.
        if not self.explicit_filial and getattr(inst, 'filial_id', False) is None:
            inst.filial = active_filial(self.request)
        resp = super().form_valid(form)
        amal = Faoliyat.Amal.QOSHISH if yangi else Faoliyat.Amal.TAHRIRLASH
        vn = self.object._meta.verbose_name
        log_faoliyat(self.request, amal, f'{vn}: {self.object}')
        # Bildirishnoma — boshqa foydalanuvchilarga
        fil = self.object.filial if getattr(self.object, 'filial_id', None) else None
        kim = self.request.user.get_full_name() or self.request.user.username
        soz = _('qo‘shdi') if yangi else _('tahrirladi')
        notify(self.request, amal, f'{kim} — {vn} {soz}: {self.object}',
               havola=str(self.success_url), filial=fil)
        return resp

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = self.page_title
        ctx['sahifa'] = self.sahifa
        ctx['cancel_url'] = reverse(self.cancel_url) if self.cancel_url else '/'
        return ctx


class SuperAdminRequiredMixin(LoginRequiredMixin):
    """Faqat super admin kira oladi."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.super_admin:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class ParolView(SuperAdminRequiredMixin, auth_views.PasswordChangeView):
    """Parolni o'zgartirish — faqat super admin (eski parol + yangi parol 2 marta)."""

    form_class = forms.ParolForm
    template_name = 'frontend/password_change.html'
    success_url = reverse_lazy('profil')

    def form_valid(self, form):
        messages.success(self.request, _('Parol muvaffaqiyatli o‘zgartirildi.'))
        resp = super().form_valid(form)
        log_faoliyat(self.request, Faoliyat.Amal.TAHRIRLASH, 'Parol o‘zgartirildi')
        return resp

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({'page_title': _('Parolni o‘zgartirish'),
                    'sahifa': 'profil', 'cancel_url': reverse('profil')})
        return ctx


# ============================================================
#  O'CHIRISH — umumiy (modal tasdiq bilan)
# ============================================================
def _delete_registry():
    # model nomi -> (model, faqat_super_admin)
    return {
        'kirim': (Kirim, True),       # investitsiya — faqat super admin
        'rasxod': (Rasxod, False),
        'maosh': (Maosh, False),
        'jojaharakat': (JojaHarakat, False),
        'jojavazn': (JojaVazn, False),
        'jojaochirish': (JojaOchirish, False),
        'tuxumyigim': (TuxumYigim, False),
        'sotuv': (Sotuv, False),
        'xodim': (Xodim, False),      # filial admini o'z xodimini o'chira oladi (scope_qs cheklaydi)
        'partiya': (Partiya, True),
        'filial': (Filial, True),
    }


@login_required
def ochirish(request, model, pk):
    """Yozuvni o'chiradi (faqat POST). 24 soat qulfi va filial doirasi tekshiriladi."""
    reg = _delete_registry()
    if model not in reg:
        raise Http404
    Model, faqat_super = reg[model]
    if faqat_super and not request.user.super_admin:
        raise PermissionDenied
    qs = Model._default_manager.all()
    if not request.user.super_admin and hasattr(Model, 'filial'):
        qs = scope_qs(request, qs)
    obj = get_object_or_404(qs, pk=pk)
    if request.method == 'POST':
        if not tahrirlash_mumkin(request.user, obj):
            messages.warning(request, _('Bu yozuvni o‘chirish muddati (24 soat) tugagan.'))
        else:
            vn = obj._meta.verbose_name
            nom = f'{vn}: {obj}'
            fil = obj.filial if getattr(obj, 'filial_id', None) else None
            kim = request.user.get_full_name() or request.user.username
            obj.delete()
            log_faoliyat(request, Faoliyat.Amal.OCHIRISH, nom)
            notify(request, Faoliyat.Amal.OCHIRISH,
                   f'{kim} — {vn} o‘chirdi: {nom.split(": ",1)[-1]}',
                   havola=request.META.get('HTTP_REFERER', '') or '', filial=fil)
            messages.success(request, _('Yozuv o‘chirildi.'))
    return redirect(request.META.get('HTTP_REFERER') or '/')


# ============================================================
#  INVESTITSIYA (ichki nomi: Kirim)
# ============================================================
class KirimList(FrontListView):
    model = Kirim
    sahifa = 'kirim'
    page_title = _('Investitsiyalar')
    add_url = 'kirim_add'
    edit_url = 'kirim_edit'
    del_model = 'kirim'
    select_related = ('filial', 'partiya')

    @property
    def headers(self):
        # Super admin uchun "Kimga (filial)" ustuni ham ko'rinadi
        if self.request.user.super_admin:
            return [_('Sana'), _('Kimga (filial)'), _('Partiya'), _('Summa')]
        return [_('Sana'), _('Partiya'), _('Summa')]

    def cells(self, o):
        if self.request.user.super_admin:
            return [o.sana, o.filial or '—', o.partiya or '—', _pul(o.summa)]
        return [o.sana, o.partiya or '—', _pul(o.summa)]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Filial hodimlari faqat ko'radi (qo'shish/tahrirlash yo'q)
        if not self.request.user.super_admin:
            ctx['add_url'] = None
            for row in ctx['rows']:
                row['edit_url'] = None
        return ctx


class KirimCreate(SuperAdminRequiredMixin, FrontFormMixin, CreateView):
    model = Kirim
    form_class = forms.KirimForm
    success_url = reverse_lazy('kirim_list')
    cancel_url = 'kirim_list'
    sahifa = 'kirim'
    page_title = _('Yangi investitsiya')
    explicit_filial = True


class KirimUpdate(SuperAdminRequiredMixin, FrontFormMixin, UpdateView):
    model = Kirim
    form_class = forms.KirimForm
    success_url = reverse_lazy('kirim_list')
    cancel_url = 'kirim_list'
    sahifa = 'kirim'
    page_title = _('Investitsiyani tahrirlash')
    explicit_filial = True


# ============================================================
#  RASXOD
# ============================================================
class RasxodList(FrontListView):
    model = Rasxod
    sahifa = 'rasxod'
    page_title = _('Rasxodlar')
    headers = [_('Sana'), _('Sabab'), _('Summa'), _('Kiritgan')]
    add_url = 'rasxod_add'
    eksport = True
    edit_url = 'rasxod_edit'
    del_model = 'rasxod'
    select_related = ('kategoriya',)

    def cells(self, o):
        return [o.sana, o.kategoriya.nomi, _pul(o.summa), o.kiritgan or '—']


class RasxodCreate(FrontFormMixin, CreateView):
    model = Rasxod
    form_class = forms.RasxodForm
    success_url = reverse_lazy('rasxod_list')
    cancel_url = 'rasxod_list'
    sahifa = 'rasxod'
    page_title = _('Yangi rasxod')


class RasxodUpdate(FrontFormMixin, UpdateView):
    model = Rasxod
    form_class = forms.RasxodForm
    success_url = reverse_lazy('rasxod_list')
    cancel_url = 'rasxod_list'
    sahifa = 'rasxod'
    page_title = _('Rasxodni tahrirlash')


@login_required
def sabab_qoshish(request):
    """Rasxod formasidan yangi sabab (kategoriya) qo'shish (inline, JSON)."""
    from apps.finance.models import RasxodKategoriya
    if request.method == 'POST':
        nomi = (request.POST.get('nomi') or '').strip()
        if nomi:
            obj, _created = RasxodKategoriya.objects.get_or_create(nomi=nomi)
            return JsonResponse({'id': obj.id, 'nomi': obj.nomi})
    return JsonResponse({'xato': 'nomi kerak'}, status=400)


# ============================================================
#  MAOSH
# ============================================================
class MaoshList(FrontListView):
    model = Maosh
    sahifa = 'maosh'
    page_title = _('Maoshlar')
    headers = [_('Hodim'), _('Sana'), _('Summa'), _('Kiritgan')]
    add_url = 'maosh_add'
    eksport = True
    edit_url = 'maosh_edit'
    del_model = 'maosh'
    select_related = ('hodim',)

    def cells(self, o):
        return [str(o.hodim), o.sana, _pul(o.summa), o.kiritgan or '—']


class MaoshCreate(FrontFormMixin, CreateView):
    model = Maosh
    form_class = forms.MaoshForm
    success_url = reverse_lazy('maosh_list')
    cancel_url = 'maosh_list'
    sahifa = 'maosh'
    page_title = _('Yangi maosh')


class MaoshUpdate(FrontFormMixin, UpdateView):
    model = Maosh
    form_class = forms.MaoshForm
    success_url = reverse_lazy('maosh_list')
    cancel_url = 'maosh_list'
    sahifa = 'maosh'
    page_title = _('Maoshni tahrirlash')


def _jins_tag(o):
    jtag = 'tag-egg' if o.jins == 'tovuq' else 'tag-chick'
    return format_html('<span class="tag {}">{}</span>', jtag, o.get_jins_display())


# ============================================================
#  JOJALAR — 3 bo'lim: joja holati / haftalik vazn / joja haridi
# ============================================================
class JojalarView(LoginRequiredMixin, TemplateView):
    template_name = 'frontend/poultry.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        req = self.request
        bolim = req.GET.get('bolim')
        if bolim not in ('holati', 'vazn', 'harid'):
            bolim = 'holati'
        f = active_filial(req)
        ctx['sahifa'] = 'jojalar'
        ctx['bolim'] = bolim

        if bolim == 'holati':
            from . import stock
            holat = []
            for kod, nom in Jins.choices:
                olingan = JojaHarakat._yigindi(kod, JojaHarakat.Tur.QOSHILDI, f)
                nobud = JojaHarakat._yigindi(kod, JojaHarakat.Tur.KASAL, f)
                qoldiq = (stock.tovuq_qoldiq(f) if kod == Jins.TOVUQ else stock.xoroz_qoldiq(f))
                holat.append({'jins': nom, 'olingan': olingan, 'nobud': nobud, 'qoldiq': qoldiq})
            ctx['holat'] = holat
            nobud_qs = scope_qs(req, JojaHarakat.objects.filter(tur=JojaHarakat.Tur.KASAL)).select_related('partiya')
            ctx['nobud_headers'] = [_('Sana'), _('Joja turi'), _('Harakat turi'), _('Soni'), _('Partiya')]
            ctx['nobud_rows'] = [{
                'edit_url': reverse('joja_nobud_edit', args=[o.pk]) if tahrirlash_mumkin(req.user, o) else None,
                'del_url': reverse('ochirish', args=['jojaharakat', o.pk]) if tahrirlash_mumkin(req.user, o) else None,
                'cells': [o.sana, _jins_tag(o),
                          format_html('<span class="tag tag-out">{}</span>', o.get_tur_display()),
                          f'{o.soni:,}', o.partiya or '—'],
            } for o in nobud_qs[:100]]
            ctx['nobud_add_url'] = reverse('joja_nobud_add')

        elif bolim == 'vazn':
            vazn_qs = scope_qs(req, JojaVazn.objects.all())
            ctx['vazn_headers'] = [_('Sana (hafta)'), _('Joja turi'), _('O‘rtacha vazn'), _('Izoh')]
            ctx['vazn_rows'] = [{
                'edit_url': reverse('vazn_edit', args=[o.pk]) if tahrirlash_mumkin(req.user, o) else None,
                'del_url': reverse('ochirish', args=['jojavazn', o.pk]) if tahrirlash_mumkin(req.user, o) else None,
                'cells': [o.sana, _jins_tag(o), f'{o.ortacha_vazn} {o.birlik}', o.izoh or '—'],
            } for o in vazn_qs[:100]]
            ctx['vazn_add_url'] = reverse('vazn_add')

        else:  # harid
            harid_qs = scope_qs(req, JojaHarakat.objects.filter(tur=JojaHarakat.Tur.QOSHILDI)).select_related('partiya')
            ctx['harid_headers'] = [_('Sana'), _('Joja turi'), _('Soni'), _('Dona narxi'), _('Jami'), _('Partiya')]
            ctx['harid_rows'] = [{
                'edit_url': reverse('joja_harid_edit', args=[o.pk]) if tahrirlash_mumkin(req.user, o) else None,
                'del_url': reverse('ochirish', args=['jojaharakat', o.pk]) if tahrirlash_mumkin(req.user, o) else None,
                'cells': [o.sana, _jins_tag(o), f'{o.soni:,}',
                          _pul(o.dona_narxi) if o.dona_narxi else '—', _pul(o.jami), o.partiya or '—'],
            } for o in harid_qs[:100]]
            ctx['harid_add_url'] = reverse('joja_harid_add')

        return ctx


class JojaFormMixin(FrontFormMixin):
    """Joja formalari — jojalar sahifasining tegishli bo'limiga qaytaradi."""
    sahifa = 'jojalar'
    joja_bolim = 'holati'
    cancel_url = None

    def get_success_url(self):
        return f"{reverse('jojalar')}?bolim={self.joja_bolim}"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cancel_url'] = f"{reverse('jojalar')}?bolim={self.joja_bolim}"
        return ctx


# --- Joja haridi (sotib olish) ---
class JojaHaridCreate(JojaFormMixin, CreateView):
    model = JojaHarakat
    form_class = forms.JojaHaridForm
    joja_bolim = 'harid'
    page_title = _('Yangi joja haridi')

    def form_valid(self, form):
        form.instance.tur = JojaHarakat.Tur.QOSHILDI
        return super().form_valid(form)


class JojaHaridUpdate(JojaFormMixin, UpdateView):
    model = JojaHarakat
    form_class = forms.JojaHaridForm
    joja_bolim = 'harid'
    page_title = _('Joja haridini tahrirlash')

    def get_queryset(self):
        return super().get_queryset().filter(tur=JojaHarakat.Tur.QOSHILDI)


# --- Joja holati (nobud bo'ldi) ---
class JojaNobudCreate(JojaFormMixin, CreateView):
    model = JojaHarakat
    form_class = forms.JojaNobudForm
    joja_bolim = 'holati'
    page_title = _('Nobud bo‘lganini qo‘shish')

    def form_valid(self, form):
        form.instance.tur = JojaHarakat.Tur.KASAL
        return super().form_valid(form)


class JojaNobudUpdate(JojaFormMixin, UpdateView):
    model = JojaHarakat
    form_class = forms.JojaNobudForm
    joja_bolim = 'holati'
    page_title = _('Nobud yozuvini tahrirlash')

    def get_queryset(self):
        return super().get_queryset().filter(tur=JojaHarakat.Tur.KASAL)


# --- Haftalik vazn ---
class VaznCreate(JojaFormMixin, CreateView):
    model = JojaVazn
    form_class = forms.JojaVaznForm
    joja_bolim = 'vazn'
    page_title = _('Yangi vazn yozuvi')


class VaznUpdate(JojaFormMixin, UpdateView):
    model = JojaVazn
    form_class = forms.JojaVaznForm
    joja_bolim = 'vazn'
    page_title = _('Vazn yozuvini tahrirlash')


# ============================================================
#  JOJALAR — tuxumdan ochirilgan jojalar (jins yo'q)
# ============================================================
class JojaOchirishList(FrontListView):
    model = JojaOchirish
    sahifa = 'joja_ochirish'
    page_title = _('Jojalar')
    template_name = 'frontend/jojalar.html'
    headers = [_('Sana'), _('Tuxum soni'), _('Ochilgan'), _('Nobud'), _('Kiritgan')]
    add_url = 'joja_add'
    edit_url = 'joja_edit'
    del_model = 'jojaochirish'
    eksport = True
    select_related = ('kiritgan',)

    def cells(self, o):
        nobud = format_html('<span class="tag {}">{}</span>',
                            'tag-out' if o.nobud else 'tag-in', f'{o.nobud:,}')
        return [o.sana, f'{o.tuxum_soni:,}', f'{o.ochilgan:,}', nobud, o.kiritgan or '—']

    def get_context_data(self, **kwargs):
        from . import stock
        ctx = super().get_context_data(**kwargs)
        ctx['joja_qoldiq'] = stock.joja_qoldiq(active_filial(self.request))
        return ctx


class JojaOchirishCreate(FrontFormMixin, CreateView):
    model = JojaOchirish
    form_class = forms.JojaOchirishForm
    success_url = reverse_lazy('joja_list')
    cancel_url = 'joja_list'
    sahifa = 'joja_ochirish'
    page_title = _('Yangi joja (ochirish)')


class JojaOchirishUpdate(FrontFormMixin, UpdateView):
    model = JojaOchirish
    form_class = forms.JojaOchirishForm
    success_url = reverse_lazy('joja_list')
    cancel_url = 'joja_list'
    sahifa = 'joja_ochirish'
    page_title = _('Jojani tahrirlash')


# ============================================================
#  PARTIYALAR
# ============================================================
class PartiyaList(SuperAdminRequiredMixin, FrontListView):
    model = Partiya
    sahifa = 'partiya'
    page_title = _('Partiyalar')
    headers = [_('Partiya nomi'), _('Filial'), _('Boshlangan sana'), _('Holat')]
    add_url = 'partiya_add'
    edit_url = 'partiya_edit'
    del_model = 'partiya'
    select_related = ('filial',)

    def cells(self, o):
        holat = format_html('<span class="tag {}">{}</span>',
                            'tag-in' if o.faol else 'tag-out',
                            _('Faol') if o.faol else _('Nofaol'))
        return [o.nomi, o.filial or '—', o.sana or '—', holat]


class PartiyaCreate(SuperAdminRequiredMixin, FrontFormMixin, CreateView):
    model = Partiya
    form_class = forms.PartiyaForm
    success_url = reverse_lazy('partiya_list')
    cancel_url = 'partiya_list'
    sahifa = 'partiya'
    page_title = _('Yangi partiya')
    explicit_filial = True


class PartiyaUpdate(SuperAdminRequiredMixin, FrontFormMixin, UpdateView):
    model = Partiya
    form_class = forms.PartiyaForm
    success_url = reverse_lazy('partiya_list')
    cancel_url = 'partiya_list'
    sahifa = 'partiya'
    page_title = _('Partiyani tahrirlash')
    explicit_filial = True


# ============================================================
#  SOTUV — Joja sotuvi (alohida)
# ============================================================
class JojaSotuvList(FrontListView):
    model = Sotuv
    sahifa = 'sotuv_joja'
    page_title = _('Joja sotuvi')
    headers = [_('Sana'), _('Soni'), _('Birlik narxi'), _('Jami')]
    add_url = 'sotuv_joja_add'
    eksport = True
    edit_url = 'sotuv_joja_edit'
    del_model = 'sotuv'

    headers = [_('Sana'), _('Manba'), _('Soni'), _('Birlik narxi'), _('Jami')]

    def get_queryset(self):
        return super().get_queryset().filter(tur=Sotuv.Tur.JOJA)

    def cells(self, o):
        if o.manba == Sotuv.Manba.TOVUQBAZA:
            manba = o.get_jins_display() if o.jins else _('Tovuqlar bazasi')
        elif o.manba == Sotuv.Manba.JOJA:
            manba = _('Jojalar')
        else:
            manba = '—'
        return [o.sana, manba, f'{o.soni:,}', _pul(o.birlik_narxi), _pul(o.jami)]


class JojaSotuvMixin(FrontFormMixin):
    """Joja sotuvi: tur avtomatik 'joja' + manbadagi qoldiq yetarliligini tekshiradi."""

    def form_valid(self, form):
        form.instance.tur = Sotuv.Tur.JOJA
        from . import stock
        fil = active_filial(self.request)
        manba = form.cleaned_data.get('manba')
        jins = form.cleaned_data.get('jins') or ''
        soni = form.cleaned_data.get('soni') or 0
        mavjud = stock.mavjud_qoldiq(fil, manba, jins)
        # Tahrirlashda: eski yozuvning sonini qaytarib qo'shamiz (o'sha manbadan)
        eski = getattr(self, 'object', None)
        if eski and eski.pk and eski.manba == manba and (eski.jins or '') == jins:
            mavjud += eski.soni
        if soni > mavjud:
            if manba == Sotuv.Manba.JOJA:
                nom = _('joja')
            elif jins == 'xoroz':
                nom = _('xo‘roz')
            else:
                nom = _('tovuq')
            form.add_error('soni', _('Qoldiq yetarli emas. Mavjud: %(n)s %(nom)s.')
                           % {'n': mavjud, 'nom': nom})
            return self.form_invalid(form)
        return super().form_valid(form)


class JojaSotuvCreate(JojaSotuvMixin, CreateView):
    model = Sotuv
    form_class = forms.JojaSotuvForm
    success_url = reverse_lazy('sotuv_joja_list')
    cancel_url = 'sotuv_joja_list'
    sahifa = 'sotuv_joja'
    page_title = _('Yangi joja sotuvi')


class JojaSotuvUpdate(JojaSotuvMixin, UpdateView):
    model = Sotuv
    form_class = forms.JojaSotuvForm
    success_url = reverse_lazy('sotuv_joja_list')
    cancel_url = 'sotuv_joja_list'
    sahifa = 'sotuv_joja'
    page_title = _('Joja sotuvini tahrirlash')

    def get_queryset(self):
        return super().get_queryset().filter(tur=Sotuv.Tur.JOJA)


# ============================================================
#  SOTUV — Tuxum sotuvi (alohida, sifat bilan)
# ============================================================
class TuxumSotuvList(FrontListView):
    model = Sotuv
    sahifa = 'sotuv_tuxum'
    page_title = _('Tuxum sotuvi')
    headers = [_('Sana'), _('Sifat'), _('Soni'), _('Birlik narxi'), _('Jami')]
    add_url = 'sotuv_tuxum_add'
    eksport = True
    edit_url = 'sotuv_tuxum_edit'
    del_model = 'sotuv'

    def get_queryset(self):
        return super().get_queryset().filter(tur=Sotuv.Tur.TUXUM)

    def cells(self, o):
        sifat = o.get_tuxum_sifati_display() if o.tuxum_sifati else '—'
        return [o.sana, sifat, f'{o.soni:,}', _pul(o.birlik_narxi), _pul(o.jami)]


class TuxumSotuvCreate(FrontFormMixin, CreateView):
    model = Sotuv
    form_class = forms.TuxumSotuvForm
    success_url = reverse_lazy('sotuv_tuxum_list')
    cancel_url = 'sotuv_tuxum_list'
    sahifa = 'sotuv_tuxum'
    page_title = _('Yangi tuxum sotuvi')

    def form_valid(self, form):
        form.instance.tur = Sotuv.Tur.TUXUM
        return super().form_valid(form)


class TuxumSotuvUpdate(FrontFormMixin, UpdateView):
    model = Sotuv
    form_class = forms.TuxumSotuvForm
    success_url = reverse_lazy('sotuv_tuxum_list')
    cancel_url = 'sotuv_tuxum_list'
    sahifa = 'sotuv_tuxum'
    page_title = _('Tuxum sotuvini tahrirlash')

    def get_queryset(self):
        return super().get_queryset().filter(tur=Sotuv.Tur.TUXUM)


# ============================================================
#  FILIAL (faqat super admin)
# ============================================================
class FilialList(SuperAdminRequiredMixin, ListView):
    model = Filial
    template_name = 'frontend/object_list.html'
    paginate_by = 25

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['headers'] = [_('Filial nomi'), _('Davlat'), _('Manzil'), _('Holat'), _('Hodimlar')]
        ctx['rows'] = [{
            'cells': [
                o.nomi, o.get_davlat_display(), o.manzil or '—',
                format_html('<span class="tag {}">{}</span>',
                            'tag-in' if o.faol else 'tag-out',
                            _('Faol') if o.faol else _('Nofaol')),
                o.hodimlar.count(),
            ],
            'edit_url': reverse('filial_edit', args=[o.pk]),
            'del_url': reverse('ochirish', args=['filial', o.pk]),
        } for o in ctx['object_list']]
        ctx['page_title'] = _('Filiallar')
        ctx['sahifa'] = 'filial'
        ctx['add_url'] = reverse('filial_add')
        return ctx


class FilialCreate(SuperAdminRequiredMixin, CreateView):
    model = Filial
    form_class = forms.FilialForm
    template_name = 'frontend/object_form.html'
    success_url = reverse_lazy('filial_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({'page_title': _('Yangi filial'), 'sahifa': 'filial',
                    'cancel_url': reverse('filial_list')})
        return ctx


class FilialUpdate(SuperAdminRequiredMixin, UpdateView):
    model = Filial
    form_class = forms.FilialForm
    template_name = 'frontend/object_form.html'
    success_url = reverse_lazy('filial_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({'page_title': _('Filialni tahrirlash'), 'sahifa': 'filial',
                    'cancel_url': reverse('filial_list')})
        return ctx


# ============================================================
#  XODIMLAR (login/parolsiz) — super admin boshqaradi
# ============================================================
class XodimList(FrontListView):
    # Filial admini ham o'z filialidagi xodimlarni ko'ra oladi (scope_qs cheklaydi).
    model = Xodim
    sahifa = 'xodim'
    page_title = _('Xodimlar')
    headers = [_('Ism familiya'), _('Lavozim'), _('Oylik maosh'), _('Filial'), _('Holat')]
    add_url = 'xodim_add'
    edit_url = 'xodim_edit'
    del_model = 'xodim'
    select_related = ('filial',)

    def cells(self, o):
        holat = format_html('<span class="tag {}">{}</span>',
                            'tag-in' if o.faol else 'tag-out',
                            _('Faol') if o.faol else _('Nofaol'))
        return [o.ism, o.lavozim, _pul(o.oylik), o.filial, holat]


class XodimFormMixin(FrontFormMixin):
    """Super admin xohlagan filialga; filial admini faqat o'z filialiga xodim qo'shadi."""

    @property
    def explicit_filial(self):
        # Super admin filialni o'zi tanlaydi; filial admini uchun avto-belgilanadi.
        return self.request.user.is_authenticated and self.request.user.super_admin

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filial admini filialni tanlamaydi — o'z filiali avtomatik qo'yiladi.
        if not self.explicit_filial and 'filial' in form.fields:
            del form.fields['filial']
        return form


class XodimCreate(XodimFormMixin, CreateView):
    model = Xodim
    form_class = forms.XodimForm
    success_url = reverse_lazy('xodim_list')
    cancel_url = 'xodim_list'
    sahifa = 'xodim'
    page_title = _('Yangi xodim')


class XodimUpdate(XodimFormMixin, UpdateView):
    model = Xodim
    form_class = forms.XodimForm
    success_url = reverse_lazy('xodim_list')
    cancel_url = 'xodim_list'
    sahifa = 'xodim'
    page_title = _('Xodimni tahrirlash')


# ============================================================
#  HISOBOTLAR + PDF (super admin)
# ============================================================
def _hisobot_data(request):
    f = active_filial(request)

    def scoped(M):
        qs = M.objects.all()
        return qs if f is None else qs.filter(filial=f)

    kirimlar = list(scoped(Kirim).select_related('partiya')[:500])
    rasxodlar = list(scoped(Rasxod).select_related('kategoriya')[:500])
    maoshlar = list(scoped(Maosh).select_related('hodim')[:500])
    sotuvlar = list(scoped(Sotuv)[:500])

    inv_jami = scoped(Kirim).aggregate(s=Sum('summa'))['s'] or 0
    rasxod_jami = scoped(Rasxod).aggregate(s=Sum('summa'))['s'] or 0
    maosh_jami = scoped(Maosh).aggregate(s=Sum('summa'))['s'] or 0
    sabablar = list(scoped(Rasxod).values('kategoriya__nomi').annotate(jami=Sum('summa')).order_by('-jami'))

    def tushum(tur):
        return scoped(Sotuv).filter(tur=tur).aggregate(s=Sum(F('soni') * F('birlik_narxi')))['s'] or 0
    joja_t = tushum(Sotuv.Tur.JOJA)
    tuxum_t = tushum(Sotuv.Tur.TUXUM)
    tushum_jami = joja_t + tuxum_t
    from decimal import Decimal
    rasxod_umumiy = rasxod_jami + maosh_jami
    sof_foyda = Decimal(str(tushum_jami)) - rasxod_umumiy   # Tushum − Rasxod
    balans = inv_jami - rasxod_jami - maosh_jami + Decimal(str(tushum_jami))

    return {
        'filial': f,
        'sana': timezone.localdate(),
        'kirimlar': kirimlar, 'rasxodlar': rasxodlar, 'maoshlar': maoshlar, 'sotuvlar': sotuvlar,
        'sabablar': sabablar,
        'inv_jami': inv_jami, 'rasxod_jami': rasxod_jami, 'maosh_jami': maosh_jami,
        'joja_t': joja_t, 'tuxum_t': tuxum_t, 'tushum_jami': tushum_jami,
        'rasxod_umumiy': rasxod_umumiy,
        'sof_foyda': sof_foyda,
        'balans': balans,
    }


class HisobotView(SuperAdminRequiredMixin, TemplateView):
    template_name = 'frontend/reports.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(_hisobot_data(self.request))
        # Oylarni taqqoslash (shu sahifa ichida)
        f = active_filial(self.request)
        ctx.update(compare.taqqoslash(f, self.request.GET.get('d1'), self.request.GET.get('d2')))
        ctx['sahifa'] = 'hisobot'
        return ctx


def _pdf_link_callback(uri, rel):
    """PDF ichidagi url() larni mahalliy fayl yo'liga aylantiradi (fontlar uchun)."""
    import os
    if uri.startswith('file://'):
        uri = uri[7:]
    if os.path.isfile(uri):
        return uri
    return uri


@login_required
def hisobot_pdf(request):
    if not request.user.super_admin:
        raise PermissionDenied
    import os

    from django.conf import settings
    from xhtml2pdf import pisa

    data = _hisobot_data(request)
    data.update(compare.taqqoslash(active_filial(request),
                                   request.GET.get('d1'), request.GET.get('d2')))
    font_dir = os.path.join(settings.BASE_DIR, 'static', 'fonts')
    data['font_regular'] = os.path.join(font_dir, 'DejaVuSans.ttf')
    data['font_bold'] = os.path.join(font_dir, 'DejaVuSans-Bold.ttf')
    html = render(request, 'frontend/report_pdf.html', data).content.decode('utf-8')
    resp = HttpResponse(content_type='application/pdf')
    resp['Content-Disposition'] = 'attachment; filename="DOA-hisobot.pdf"'
    pisa.CreatePDF(html, dest=resp, link_callback=_pdf_link_callback, encoding='utf-8')
    log_faoliyat(request, Faoliyat.Amal.QOSHISH, 'PDF hisobot yuklandi')
    return resp


# ============================================================
#  AKTIVLIK (super admin)
# ============================================================
class AktivlikList(SuperAdminRequiredMixin, ListView):
    model = Faoliyat
    template_name = 'frontend/activity.html'
    paginate_by = 50

    def get_queryset(self):
        return Faoliyat.objects.select_related('user')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['sahifa'] = 'aktivlik'
        return ctx


# ============================================================
#  BILDIRISHNOMALAR (notification)
# ============================================================
@login_required
def bildirishnoma_oqish(request, pk):
    """Bitta bildirishnomani o'qilgan deb belgilab, havolaga o'tkazadi."""
    n = get_object_or_404(request.user.bildirishnomalar, pk=pk)
    if not n.oqilgan:
        n.oqilgan = True
        n.save(update_fields=['oqilgan'])
    return redirect(n.havola or reverse('bildirishnomalar'))


@login_required
def bildirishnoma_hammasi_oqildi(request):
    """Barcha bildirishnomalarni o'qilgan deb belgilaydi."""
    request.user.bildirishnomalar.filter(oqilgan=False).update(oqilgan=True)
    return redirect(request.META.get('HTTP_REFERER') or reverse('bildirishnomalar'))


class BildirishnomaList(LoginRequiredMixin, ListView):
    template_name = 'frontend/notifications.html'
    paginate_by = 30
    context_object_name = 'object_list'

    def get_queryset(self):
        return self.request.user.bildirishnomalar.select_related('actor')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['sahifa'] = 'bildirishnoma'
        ctx['page_title'] = _('Bildirishnomalar')
        return ctx


# ============================================================
#  TUXUM YIG'IMI (kunlik real ishlab chiqarish) + PROGNOZ KPI
# ============================================================
class TuxumYigimList(FrontListView):
    model = TuxumYigim
    sahifa = 'tuxum_yigim'
    page_title = _('Tuxum yig‘imi')
    headers = [_('Sana'), _('Partiya'), _('Yig‘ilgan tuxum'), _('Kiritgan')]
    add_url = 'tuxum_yigim_add'
    edit_url = 'tuxum_yigim_edit'
    del_model = 'tuxumyigim'
    select_related = ('partiya', 'kiritgan')

    def cells(self, o):
        return [o.sana, o.partiya or '—', f'{o.soni} {_("dona")}', o.kiritgan or '—']


class TuxumYigimCreate(FrontFormMixin, CreateView):
    model = TuxumYigim
    form_class = forms.TuxumYigimForm
    success_url = reverse_lazy('tuxum_yigim_list')
    cancel_url = 'tuxum_yigim_list'
    sahifa = 'tuxum_yigim'
    page_title = _('Yangi tuxum yig‘imi')


class TuxumYigimUpdate(FrontFormMixin, UpdateView):
    model = TuxumYigim
    form_class = forms.TuxumYigimForm
    success_url = reverse_lazy('tuxum_yigim_list')
    cancel_url = 'tuxum_yigim_list'
    sahifa = 'tuxum_yigim'
    page_title = _('Tuxum yig‘imini tahrirlash')


class TuxumPrognozView(SuperAdminRequiredMixin, TemplateView):
    """Tuxum tug'uvchanlik prognozi va samaradorligi (HDEP KPI)."""
    template_name = 'frontend/egg_forecast.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        f = active_filial(self.request)
        tahlil = egg_kpi.partiya_tahlili(f)
        ctx['sahifa'] = 'tuxum_prognoz'
        ctx['tahlil'] = tahlil
        ctx['kpi'] = egg_kpi.umumiy_kpi(f, tahlil=tahlil)
        # Grafik uchun partiya tanlash (yoki birinchisi)
        tanlangan = None
        pid = self.request.GET.get('partiya')
        partiyalar = [t['partiya'] for t in tahlil]
        if pid:
            tanlangan = next((p for p in partiyalar if str(p.pk) == pid), None)
        if tanlangan is None and partiyalar:
            tanlangan = partiyalar[0]
        ctx['partiyalar'] = partiyalar
        ctx['tanlangan'] = tanlangan
        ctx['grafik'] = egg_kpi.grafik_svg(egg_kpi.hdep_grafik(tanlangan))
        return ctx


# ============================================================
#  TELEGRAM ulanish (super admin)
# ============================================================
class TelegramView(SuperAdminRequiredMixin, TemplateView):
    template_name = 'frontend/telegram.html'

    def get_context_data(self, **kwargs):
        from apps.accounts import telegram
        from apps.accounts.models import TelegramKod, TelegramUlanish
        ctx = super().get_context_data(**kwargs)
        ctx['sahifa'] = 'telegram'
        ctx['bot_username'] = telegram.bot_username()
        ctx['ulanishlar'] = TelegramUlanish.objects.filter(user=self.request.user, faol=True)
        kod = (TelegramKod.objects.filter(user=self.request.user, ishlatilgan=False,
                                          amal_qiladi__gte=timezone.now())
               .order_by('-yaratilgan').first())
        ctx['kod'] = kod
        return ctx


@login_required
def telegram_kod_yarat(request):
    """Super admin uchun bir martalik ulanish kodi yaratadi (15 daqiqa)."""
    import secrets
    from datetime import timedelta

    from apps.accounts.models import TelegramKod
    if not request.user.super_admin or request.method != 'POST':
        raise PermissionDenied
    # eski foydalanilmagan kodlarni bekor qilamiz
    TelegramKod.objects.filter(user=request.user, ishlatilgan=False).update(ishlatilgan=True)
    kod = f'{secrets.randbelow(900000) + 100000}'  # 6 xonali
    TelegramKod.objects.create(
        user=request.user, kod=kod,
        amal_qiladi=timezone.now() + timedelta(minutes=15),
    )
    messages.success(request, _('Yangi kod yaratildi. Uni botga yuboring (15 daqiqa amal qiladi).'))
    return redirect('telegram')


@login_required
def telegram_uzish(request, pk):
    """Telegram ulanishini uzadi (faqat o'ziniki)."""
    from apps.accounts.models import TelegramUlanish
    if not request.user.super_admin or request.method != 'POST':
        raise PermissionDenied
    ul = get_object_or_404(TelegramUlanish, pk=pk, user=request.user)
    ul.faol = False
    ul.save(update_fields=['faol'])
    messages.success(request, _('Telegram ulanishi uzildi.'))
    return redirect('telegram')


