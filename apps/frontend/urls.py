from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('filial-tanlash/', views.set_filial, name='set_filial'),
    path('profil/', views.ProfilView.as_view(), name='profil'),
    path('profil/parol/', views.ParolView.as_view(), name='parol_ozgartirish'),
    path('tuxum-yigim/', views.TuxumYigimList.as_view(), name='tuxum_yigim_list'),
    path('tuxum-yigim/yangi/', views.TuxumYigimCreate.as_view(), name='tuxum_yigim_add'),
    path('tuxum-yigim/<int:pk>/', views.TuxumYigimUpdate.as_view(), name='tuxum_yigim_edit'),
    path('tuxum-prognoz/', views.TuxumPrognozView.as_view(), name='tuxum_prognoz'),
    path('telegram/', views.TelegramView.as_view(), name='telegram'),
    path('telegram/kod/', views.telegram_kod_yarat, name='telegram_kod_yarat'),
    path('telegram/uzish/<int:pk>/', views.telegram_uzish, name='telegram_uzish'),
    path('bildirishnomalar/', views.BildirishnomaList.as_view(), name='bildirishnomalar'),
    path('bildirishnomalar/oqish/<int:pk>/', views.bildirishnoma_oqish, name='bildirishnoma_oqish'),
    path('bildirishnomalar/hammasi/', views.bildirishnoma_hammasi_oqildi, name='bildirishnoma_hammasi'),
    path('ochirish/<str:model>/<int:pk>/', views.ochirish, name='ochirish'),

    # Hisobotlar + Aktivlik (super admin)
    path('hisobotlar/', views.HisobotView.as_view(), name='hisobot'),
    path('hisobotlar/pdf/', views.hisobot_pdf, name='hisobot_pdf'),
    path('aktivlik/', views.AktivlikList.as_view(), name='aktivlik'),

    # Filiallar (super admin)
    path('filiallar/', views.FilialList.as_view(), name='filial_list'),
    path('filiallar/yangi/', views.FilialCreate.as_view(), name='filial_add'),
    path('filiallar/<int:pk>/', views.FilialUpdate.as_view(), name='filial_edit'),

    # Xodimlar (super admin)
    path('xodimlar/', views.XodimList.as_view(), name='xodim_list'),
    path('xodimlar/yangi/', views.XodimCreate.as_view(), name='xodim_add'),
    path('xodimlar/<int:pk>/', views.XodimUpdate.as_view(), name='xodim_edit'),

    # Kirim
    path('kirim/', views.KirimList.as_view(), name='kirim_list'),
    path('kirim/yangi/', views.KirimCreate.as_view(), name='kirim_add'),
    path('kirim/<int:pk>/', views.KirimUpdate.as_view(), name='kirim_edit'),

    # Rasxod
    path('rasxod/', views.RasxodList.as_view(), name='rasxod_list'),
    path('rasxod/yangi/', views.RasxodCreate.as_view(), name='rasxod_add'),
    path('rasxod/<int:pk>/', views.RasxodUpdate.as_view(), name='rasxod_edit'),
    path('rasxod/sabab/qoshish/', views.sabab_qoshish, name='sabab_qoshish'),
    path('rasxod/sabab/royhat/', views.sabab_royhat, name='sabab_royhat'),
    path('rasxod/sabab/<int:pk>/tahrirlash/', views.sabab_tahrirlash, name='sabab_tahrirlash'),
    path('rasxod/sabab/<int:pk>/ochirish/', views.sabab_ochirish, name='sabab_ochirish'),

    # Maosh
    path('maosh/', views.MaoshList.as_view(), name='maosh_list'),
    path('maosh/yangi/', views.MaoshCreate.as_view(), name='maosh_add'),
    path('maosh/<int:pk>/', views.MaoshUpdate.as_view(), name='maosh_edit'),

    # Jojalar — 3 bo'lim (holati / vazn / harid)
    path('jojalar/', views.JojalarView.as_view(), name='jojalar'),
    path('jojalar/harid/yangi/', views.JojaHaridCreate.as_view(), name='joja_harid_add'),
    path('jojalar/harid/<int:pk>/', views.JojaHaridUpdate.as_view(), name='joja_harid_edit'),
    path('jojalar/nobud/yangi/', views.JojaNobudCreate.as_view(), name='joja_nobud_add'),
    path('jojalar/nobud/<int:pk>/', views.JojaNobudUpdate.as_view(), name='joja_nobud_edit'),
    path('jojalar/vazn/yangi/', views.VaznCreate.as_view(), name='vazn_add'),
    path('jojalar/vazn/<int:pk>/', views.VaznUpdate.as_view(), name='vazn_edit'),
    path('joja-ochirish/', views.JojaOchirishList.as_view(), name='joja_list'),
    path('joja-ochirish/yangi/', views.JojaOchirishCreate.as_view(), name='joja_add'),
    path('joja-ochirish/<int:pk>/', views.JojaOchirishUpdate.as_view(), name='joja_edit'),
    path('kunlik-log/', views.KunlikLogList.as_view(), name='kunlik_log_list'),
    path('kunlik-log/yangi/', views.KunlikLogCreate.as_view(), name='kunlik_log_add'),
    path('kunlik-log/<int:pk>/', views.KunlikLogUpdate.as_view(), name='kunlik_log_edit'),
    path('salomatlik/', views.EmlashList.as_view(), name='emlash_list'),
    path('salomatlik/yangi/', views.EmlashCreate.as_view(), name='emlash_add'),
    path('salomatlik/<int:pk>/', views.EmlashUpdate.as_view(), name='emlash_edit'),

    # Partiyalar
    path('partiyalar/', views.PartiyaList.as_view(), name='partiya_list'),
    path('partiyalar/yangi/', views.PartiyaCreate.as_view(), name='partiya_add'),
    path('partiyalar/<int:pk>/', views.PartiyaUpdate.as_view(), name='partiya_edit'),

    # Sotuv — Joja sotuvi
    path('sotuv/joja/', views.JojaSotuvList.as_view(), name='sotuv_joja_list'),
    path('sotuv/joja/yangi/', views.JojaSotuvCreate.as_view(), name='sotuv_joja_add'),
    path('sotuv/joja/<int:pk>/', views.JojaSotuvUpdate.as_view(), name='sotuv_joja_edit'),

    # Sotuv — Tuxum sotuvi
    path('sotuv/tuxum/', views.TuxumSotuvList.as_view(), name='sotuv_tuxum_list'),
    path('sotuv/tuxum/yangi/', views.TuxumSotuvCreate.as_view(), name='sotuv_tuxum_add'),
    path('sotuv/tuxum/<int:pk>/', views.TuxumSotuvUpdate.as_view(), name='sotuv_tuxum_edit'),
]
