from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin

from .models import Filial, User, Xodim

# Admin panelda filial bo'yicha cheklash (scoping) yo'q — shuning uchun unga faqat
# super admin (filialga bog'lanmagan, is_staff) kira oladi. Filial foydalanuvchisiga
# is_staff berilgan bo'lsa ham, boshqa filiallar ma'lumotini ko'ra olmaydi.
_asl_has_permission = admin.site.has_permission


def _faqat_super_admin(request):
    return _asl_has_permission(request) and request.user.filial_id is None


admin.site.has_permission = _faqat_super_admin


@admin.register(Filial)
class FilialAdmin(ModelAdmin):
    list_display = ('nomi', 'davlat', 'faol', 'yaratilgan')
    list_filter = ('davlat', 'faol')
    search_fields = ('nomi', 'manzil')


@admin.register(Xodim)
class XodimAdmin(ModelAdmin):
    list_display = ('ism', 'lavozim', 'oylik', 'filial', 'faol')
    list_filter = ('filial', 'faol')
    search_fields = ('ism', 'lavozim')
    autocomplete_fields = ('filial',)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    """Hodimlar admin paneli (Unfold ko'rinishida)."""

    list_display = ('username', 'get_full_name', 'rol', 'filial', 'is_active', 'is_staff')
    list_filter = ('rol', 'filial', 'is_active', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'telefon')
    autocomplete_fields = ('filial',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Qo\'shimcha', {'fields': ('rol', 'telefon', 'filial', 'rasm')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Qo\'shimcha', {'fields': ('rol', 'telefon', 'filial')}),
    )
