from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.common.admin import BazaAdmin

from .models import Kirim, Maosh, Rasxod, RasxodKategoriya


@admin.register(Kirim)
class KirimAdmin(BazaAdmin):
    list_display = ('sana', 'partiya', 'summa', 'kiritgan')
    list_filter = ('sana',)
    search_fields = ('izoh',)
    date_hierarchy = 'sana'
    autocomplete_fields = ('partiya',)
    readonly_fields = ('kiritgan', 'yaratilgan', 'ozgartirilgan')


@admin.register(RasxodKategoriya)
class RasxodKategoriyaAdmin(ModelAdmin):
    list_display = ('nomi',)
    search_fields = ('nomi',)


@admin.register(Rasxod)
class RasxodAdmin(BazaAdmin):
    list_display = ('sana', 'kategoriya', 'summa', 'kiritgan')
    list_filter = ('kategoriya', 'sana')
    search_fields = ('izoh',)
    date_hierarchy = 'sana'
    autocomplete_fields = ('kategoriya',)
    readonly_fields = ('kiritgan', 'yaratilgan', 'ozgartirilgan')


@admin.register(Maosh)
class MaoshAdmin(BazaAdmin):
    list_display = ('hodim', 'sana', 'summa', 'kiritgan')
    list_filter = ('sana',)
    search_fields = ('hodim__ism',)
    autocomplete_fields = ('hodim',)
    readonly_fields = ('kiritgan', 'yaratilgan', 'ozgartirilgan')
