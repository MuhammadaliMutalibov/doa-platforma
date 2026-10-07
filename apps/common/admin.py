"""Barcha modullar uchun umumiy admin yordamchilari."""

from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import ModelAdmin


class BazaAdmin(SimpleHistoryAdmin, ModelAdmin):
    """Yozuvni saqlaganda 'kiritgan hodim'ni avtomatik to'ldiradi."""

    def save_model(self, request, obj, form, change):
        if not obj.pk and hasattr(obj, 'kiritgan') and obj.kiritgan_id is None:
            obj.kiritgan = request.user
        super().save_model(request, obj, form, change)
