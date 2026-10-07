# 🏗 Arxitektura va Texnik Reja

## Loyiha tuzilishi (rejalashtirilgan)

```
DOA-platforma/
├── readme/                  # 🧠 Loyiha "miyyasi" (bu papka)
├── .env                     # Maxfiy kalitlar (git'ga tushmaydi)
├── .env.example             # Namuna
├── .gitignore
├── requirements.txt         # Python kutubxonalar
├── manage.py
├── config/                  # Django asosiy sozlamalar
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── static/                  # CSS/JS (frontend dizayn)
│   └── css/app.css          # To'q zamonaviy dizayn tizimi
├── templates/
│   ├── admin/index.html     # Unfold dashboard qo'shimchasi
│   └── frontend/            # base, kirish (login), dashboard
├── locale/                  # Tarjimalar (uz/tr/ru/en)
└── apps/                    # Barcha modullar shu yerda
    ├── common/              # Umumiy: Valyuta, BazaModel, BazaAdmin
    ├── accounts/            # Hodimlar, rollar, xavfsizlik
    ├── finance/             # Kirim, Rasxod, Maosh
    ├── inventory/           # Tovuq va Tuxum bazasi
    ├── sales/               # Sotuv
    └── frontend/            # Custom frontend (login + dashboard)
```

## Frontend arxitekturasi

- **Server-rendered** (Django templates) — bitta loyiha, bitta deploy, tez va xavfsiz.
- **Dizayn:** o'zim yozgan CSS (Tailwind uslubida), to'q (dark) tema, glass kartalar,
  emerald urg'u. Tashqi CDN yo'q → internetsiz serverda ham ishlaydi.
- **Statik fayllar:** WhiteNoise (production'da siqilgan + kesh-buster).
- **Auth:** Django sessiya + django-axes; login `/kirish/`, chiqish `/chiqish/`.
- **Statistika:** `apps/frontend/stats.py` (frontend va Unfold dashboard ham shundan oladi).
- Hozircha modul sahifalari (kirim/rasxod/...) admin orqali; keyingi bosqichda frontendga ko'chiriladi.

## Django ilovalari (apps) va modellari

> ⚠️ Model'lar v1 — mijoz qo'shimcha talab qo'shsa kengaytiriladi.

### 🔐 `accounts` — Hodimlar va xavfsizlik
- **User** (custom) — hodimlar. Rol: `admin`, `buxgalter`, `hodim`.
- Django'ning o'rnatilgan permission (ruxsat) tizimi ishlatiladi.

### 💰 `finance` — Moliya
| Model | Maydonlar (asosiy) |
|-------|--------------------|
| `Kirim` (Investitsiya) | summa, sana, manba, izoh, kiritgan_hodim |
| `Rasxod` | summa, sana, kategoriya, sabab/izoh, kiritgan_hodim |
| `Maosh` | hodim, summa, oy (yil-oy), to'langan_sana, izoh |

### 📦 `inventory` — Ombor (Tovuq + Tuxum)
| Model | Maydonlar (asosiy) |
|-------|--------------------|
| `TovuqPartiya` | nomi/partiya, boshlang'ich_soni, xarid_narxi, sana |
| `TovuqVazn` | partiya, hafta_sanasi, o'rtacha_vazn |
| `TuxumKirim` | soni, brak_soni, sana, izoh |

> **Ombor holati** (hozir nechta bor + summa) — model'lardan hisoblab chiqariladi
> (`@property` yoki Unfold dashboard'da jamlanadi), alohida "stock" model bilan
> zarur bo'lsa qo'shiladi.

### 🛒 `sales` — Sotuv
| Model | Maydonlar (asosiy) |
|-------|--------------------|
| `Sotuv` | tur (tovuq/tuxum), soni, birlik_narxi, jami (auto), sana, xaridor, hodim |

## 🔒 Xavfsizlik rejasi (yuqori himoya)

- [ ] `SECRET_KEY`, DB parollari — faqat `.env` da (`django-environ`).
- [ ] `DEBUG = False` productionда.
- [ ] `ALLOWED_HOSTS` aniq belgilanadi.
- [ ] HTTPS majburiy: `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`.
- [ ] Kuchli parol siyosati (`AUTH_PASSWORD_VALIDATORS`).
- [ ] **django-axes** — login'ga bruteforce hujumdan himoya (5 marta xato → bloklash).
- [ ] Rol asosida ruxsatlar (hodim faqat o'ziga tegishlisini ko'radi).
- [ ] **django-simple-history** — kim, qachon, nimani o'zgartirgani yoziladi (audit).
- [ ] Sessiya muddati cheklangan (`SESSION_COOKIE_AGE`).
- [ ] `.env` va `db.sqlite3` — `.gitignore` da.

## 🎨 Dizayn (Unfold)

- **django-unfold** temasi: zamonaviy, toza, mobilга moslashgan.
- Kompaniya rangi va logotipi (DOA Nutrition) sozlanadi.
- Dashboard: kirim/chiqim, ombor holati, sotuv statistikasi kartochkalarda.
- O'zbek tili interfeys (`LANGUAGE_CODE = 'uz'`).

## 🗺 Bosqichlar (yo'l xaritasi)

1. **Poydevor** — venv, Django, Unfold o'rnatish, sozlamalar, xavfsizlik. ← hozir shu yerda
2. **accounts** — custom user, rollar.
3. **finance** — Kirim/Rasxod/Maosh modellari + admin.
4. **inventory** — Tovuq/Tuxum modellari + admin.
5. **sales** — Sotuv modeli + admin.
6. **Dashboard** — Unfold statistika sahifasi.
7. **Sinov + Deploy** — test, PostgreSQL, serverga chiqarish.
