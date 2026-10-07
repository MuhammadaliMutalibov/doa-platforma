from django.contrib import admin

from apps.common.admin import BazaAdmin
from unfold.admin import ModelAdmin

from .models import JojaHarakat, JojaVazn, Partiya, TuxumBrak


@admin.register(Partiya)
class PartiyaAdmin(ModelAdmin):
    list_display = ('nomi', 'filial', 'sana', 'faol')
    list_filter = ('faol', 'filial')
    search_fields = ('nomi',)


@admin.register(JojaHarakat)
class JojaHarakatAdmin(BazaAdmin):
    list_display = ('sana', 'jins', 'tur', 'soni', 'dona_narxi', 'partiya', 'kiritgan')
    list_filter = ('jins', 'tur', 'partiya', 'sana')
    search_fields = ('izoh',)
    autocomplete_fields = ('partiya',)
    date_hierarchy = 'sana'
    readonly_fields = ('kiritgan', 'yaratilgan', 'ozgartirilgan')


@admin.register(JojaVazn)
class JojaVaznAdmin(ModelAdmin):
    list_display = ('sana', 'jins', 'ortacha_vazn', 'izoh')
    list_filter = ('jins', 'sana')
    date_hierarchy = 'sana'


@admin.register(TuxumBrak)
class TuxumBrakAdmin(BazaAdmin):
    list_display = ('sana', 'soni', 'sabab', 'kiritgan')
    list_filter = ('sana',)
    search_fields = ('sabab', 'izoh')
    date_hierarchy = 'sana'
    readonly_fields = ('kiritgan', 'yaratilgan', 'ozgartirilgan')
