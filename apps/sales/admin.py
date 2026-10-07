from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.common.admin import BazaAdmin

from .models import Sotuv


@admin.register(Sotuv)
class SotuvAdmin(BazaAdmin):
    list_display = ('sana', 'tur', 'tuxum_sifati', 'soni', 'birlik_narxi', 'jami_korinish', 'kiritgan')
    list_filter = ('tur', 'tuxum_sifati', 'sana')
    search_fields = ('izoh',)
    date_hierarchy = 'sana'
    readonly_fields = ('kiritgan', 'yaratilgan', 'ozgartirilgan')

    @admin.display(description=_('Jami'))
    def jami_korinish(self, obj):
        return f'${obj.jami:,.2f}'
