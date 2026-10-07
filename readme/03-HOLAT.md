# 📊 Loyiha Holati (Progress)

> Bu fayl **har ish qadamida yangilanadi**. Belgilar: ✅ tugallandi · 🔄 jarayonda · ⬜ hali qilinmagan

*Oxirgi yangilanish: 2026-10-05*

---

## Umumiy progress

| Bosqich | Holat |
|---------|-------|
| 0. Hujjatlar ("miyya" papka) | ✅ |
| 1. Poydevor (Django + Unfold + xavfsizlik) | ✅ |
| 2. accounts (hodimlar, rollar) | ✅ |
| 3. finance (kirim, rasxod, maosh) | ✅ |
| 4. Dizayn + 4 til (uz/tr/ru/en) | ✅ |
| 5. inventory (tovuq, tuxum) | ✅ |
| 6. sales (sotuv) | ✅ |
| 7. Dashboard (kirim/rasxod/balans + ombor qoldiq + sotuv) | ✅ |
| 8. **Frontend** (to'q zamonaviy dizayn: login + dashboard) | ✅ |
| 9. Frontend modul sahifalari (ro'yxat + forma) | ✅ |
| 10. **Ko'p-filiallilik** (super admin + filiallar) | ✅ |
| 11. Rollarga qarab ruxsatlar (filial ichida) | ⬜ |
| 12. Sinov + Deploy | ⬜ |

---

## ✅ Qilingan ishlar

- [x] Word fayl (`Platforma DOA Nutrition.docx`) o'qildi va tahlil qilindi.
- [x] `readme/` "miyya" papkasi yaratildi (README, TALABLAR, ARXITEKTURA, HOLAT).
- [x] **Poydevor:**
  - [x] Virtual muhit (`venv`) va `requirements.txt`
  - [x] Django 5.2 loyihasi (`config/`) + `apps/` tuzilishi (4 ta app)
  - [x] `django-unfold` o'rnatildi va sozlandi (yashil tema, "DOA Nutrition")
  - [x] `.env` / `.env.example` / `.gitignore` (maxfiy kalitlar himoyalangan)
  - [x] Xavfsizlik: django-axes (5 xato → blok), parol siyosati, sessiya muddati, HTTPS sozlamalari (prod), o'zgarishlar tarixi (simple_history)
  - [x] O'zbek tili (`uz`), Toshkent vaqti
  - [x] Baza migratsiya qilindi, server ishga tushirildi va tekshirildi ✔
- [x] **accounts:** custom `User` modeli (rollar: admin/buxgalter/hodim) + admin panel
- [x] Test superuser yaratildi (`admin`)
- [x] **finance moduli:**
  - [x] `apps/common` — umumiy `Valyuta` (UZS/USD/TRY) va `BazaModel` (vaqt + kim kiritgan)
  - [x] `Kirim`, `Rasxod`, `RasxodKategoriya`, `Maosh` modellari (audit tarixi bilan)
  - [x] Unfold admin panellar (filtr, qidiruv, sana ierarxiyasi, autocomplete)
  - [x] Kiritgan hodim avtomatik saqlanadi
- [x] **4 til (uz / tr / ru / en):**
  - [x] `LANGUAGES`, `LOCALE_PATHS`, til almashtirish tugmasi (Unfold)
  - [x] Barcha matnlar `gettext_lazy` bilan belgilandi
  - [x] `locale/{en,ru,tr}/django.po` to'ldirildi va `.mo` ga kompilyatsiya qilindi
  - [x] Tekshirildi: 4 tilda ham to'g'ri ishlaydi ✔
- [x] **Dizayn yaxshilandi:**
  - [x] Unfold yon menyu — guruhlar + ikonkalar (Asosiy / Moliya / Xodimlar)
  - [x] Dashboard — valyuta bo'yicha kirim/rasxod/balans kartalari + sanoqlar
  - [x] Emerald yashil rang sxemasi, `egg` ikonka

- [x] **inventory moduli:**
  - [x] `TuxumKirim` — tuxum kiritish + brak soni (jami kirim/brak hisoblash)
  - [x] `TovuqPartiya` — tovuq partiyasi (soni, xarid summasi, valyuta)
  - [x] `TovuqVazn` — haftalik o'rtacha vazn (partiya sahifasida inline)
  - [x] Unfold admin panellar + sidebar "Ombor" guruhi (ikonkalar bilan)
  - [x] Dashboard'ga qo'shildi: tuxum (jami), brak tuxum, tovuq soni
  - [x] Yangi matnlar 4 tilga tarjima qilindi
  - [x] Tekshirildi: admin sahifalar + dashboard + TR/RU/EN ✔

- [x] **sales moduli:**
  - [x] `Sotuv` modeli — tur (tovuq/tuxum), soni, birlik narxi, jami (avto), valyuta, xaridor
  - [x] Tovuq sotuvida partiyaga bog'lash (ixtiyoriy)
  - [x] Unfold admin + sidebar "Sotuv" guruhi
  - [x] **Ombor qoldig'i** dashboard'da: tuxum/tovuq qoldiq = kirim − sotilgan
  - [x] 4 tilga tarjima (fuzzy xatolar ham tuzatildi) + tekshirildi ✔

- [x] **Frontend (custom to'q dizayn):**
  - [x] `apps/frontend` app + WhiteNoise (production static, kesh-buster)
  - [x] `static/css/app.css` — to'q zamonaviy dizayn tizimi (glass, emerald, radial nur)
  - [x] Login sahifasi (`/kirish/`) — chiroyli, til tanlash tugmalari
  - [x] Dashboard (`/`) — sidebar (guruh + ikonka) + topbar (til + user) + balans/ombor/sotuv kartalari + so'nggi yozuvlar
  - [x] Inline SVG ikonkalar (tashqi CDN yo'q), mobil-moslashuvchan
  - [x] Django auth (axes himoyasi bilan), CSRF, sessiya
  - [x] Brauzerda tekshirildi: login + dashboard + til almashish (UZ/RU) ✔
  - [x] Barcha yangi matnlar 4 tilga tarjima qilindi

- [x] **Frontend modul sahifalari (custom dizaynda, admin panelga o'tmaydi):**
  - [x] Har modul uchun ro'yxat sahifasi (jadval, qidiruv/pager, "Qo'shish" tugmasi)
  - [x] Qo'shish + tahrirlash formalari (styled: date-picker, select, textarea)
  - [x] Kirim / Rasxod / Maosh / Tuxum / Tovuq / Sotuv — hammasi ishlaydi
  - [x] Kiritgan hodim avtomatik saqlanadi; form POST tekshirildi ✔
  - [x] Sidebar havolalari endi frontend sahifalariga (admin emas)
  - [x] Fayl/URL nomlari inglizcha: `login.html`, `/login/`, `/logout/`, `*_list/add/edit`
  - [x] Yangi matnlar 4 tilga tarjima qilindi; brauzerda tekshirildi ✔

- [x] **Ombor qayta qurildi (mijoz aniqlashtirishi, 2026-09-28):**
  - [x] `TovuqHarakat` — qo'shildi (sotib olindi, narx bilan) / kasallandi-nobud bo'ldi (sabab bilan)
  - [x] `TovuqVazn` — haftalik vazn (endi partiyasiz, mustaqil)
  - [x] `TuxumKirim` — faqat soni qo'shiladi (narx olib tashlandi)
  - [x] `TuxumBrak` — alohida model, sabab bilan
  - [x] `Sotuv`dan partiya bog'lanishi olib tashlandi
  - [x] Sidebar: **Tovuq** (ombor+vazn) va **Tuxum** (ombor+brak) bo'limlari
  - [x] Qoldiq hisobi yangilandi (qo'shildi−kasal−sotilgan; kirim−brak−sotilgan)
  - [x] Frontend + admin + 4 til + POST test + brauzer tekshiruvi ✔

- [x] **Ko'p-filiallilik (multi-tenant, 2026-09-28):**
  - [x] `Filial` modeli (nomi, davlat: UZ/TJ/TM/TR, manzil, faol)
  - [x] `User.filial` — filialsiz foydalanuvchi = **super admin** (hammasini ko'radi)
  - [x] Har bir ma'lumot (kirim/rasxod/ombor/sotuv) `filial`ga bog'landi (`BazaModel`)
  - [x] Filial xodimi faqat o'z filiali ma'lumotini ko'radi/yuritadi (avto-filtr)
  - [x] Yozuv qo'shilganda filial avtomatik biriktiriladi
  - [x] Super admin uchun topbarda **filial almashtirgich** (sessiyada saqlanadi) + "Barcha filiallar"
  - [x] **Filiallar** boshqaruv sahifasi (faqat super admin) — ro'yxat + qo'shish/tahrirlash
  - [x] Dashboard filialga qarab hisoblaydi (yoki barcha filiallar jamlanadi)
  - [x] Super admin bo'lmagan xodim `/filiallar/`ga kira olmaydi (403)
  - [x] Test client + brauzer bilan to'liq tekshirildi ✔; 4 tilga tarjima

- [x] **Til dropdown + bayroqlar** (2026-09-28): UZ/TR/RU/EN endi dropdown, 🇺🇿🇹🇷🇷🇺🇬🇧 bayroqlar bilan (topbar va login).
- [x] **Light / Dark tema** (2026-09-28): topbardagi ☀/🌙 tugma, `localStorage`da saqlanadi, login sahifada ham. CSS o'zgaruvchilar orqali.
- [x] **Shrift o'lchami + qalinlik** (2026-09-28): topbardagi "Aa" menyu — 4 o'lcham (kichik/oddiy/katta/XL) + qalin toggle. `px→rem` (42 ta), `localStorage`da saqlanadi. Brauzerda tekshirildi ✔
- [x] **Akkount kartasi** (2026-09-28): account ustiga bossa karta — rasm/avatar, ism, rol, filial, telefon, email + "Shaxsiy ma'lumotlar" (profil tahrirlash, rasm yuklash). `User.rasm` qo'shildi. Parolni faqat super admin o'zgartiradi.
- [x] **Domen o'zgarishlari** (2026-09-29):
  - [x] **Faqat USD** — so'm (UZS) va lira (TRY) olib tashlandi; mavjud yozuvlar USD ga o'girildi
  - [x] **Dashboard kartalari bosiladigan** (drill-in) — kirim/rasxod/joja(tovuq)/joja(xoroz)/brak/sotuv sahifalariga
  - [x] **Tuxum kirimi olib tashlandi** — tuxum faqat sotiladi (brak alohida qoldi)
  - [x] **Tovuq → Joja**; joja ikkiga bo'linadi: **tovuq** (mokiyon) va **xo'roz** (`jins` maydoni)
  - [x] Sotuv turlari: tuxum / tovuq / xo'roz; Joja qoldiq jins bo'yicha hisoblanadi
  - [x] Migratsiya, admin, 4 til, brauzer — hammasi tekshirildi ✔
- [x] **Sotuv va pul o'zgarishlari** (2026-09-29):
  - [x] Sotuv turi: **tuxum** va **joja** (tovuq/xo'roz emas)
  - [x] Pul hamma joyda **$ + 2 kasr** (`pul` filtri / `_pul`) — 0.15 endi `$0.15` ko'rinadi
  - [x] **Xaridor** ustuni/maydoni sotuvdan olib tashlandi
  - [x] Sotuvda **tuxum** tanlansa → **tuxum sifati** (sifatli/sifatsiz) maydoni chiqadi (JS shart)
  - [x] Migratsiya, 4 til, brauzer bilan tekshirildi ✔
- [x] **Bo'lim qayta tuzilishi** (2026-09-29):
  - [x] Sotuv ikkiga bo'lindi: **Joja sotuvi** va **Tuxum sotuvi** (alohida sahifa/forma; tur avtomatik)
  - [x] Tashqi **Tuxum (brak) bo'limi olib tashlandi** — brak endi sotuvda "sifatsiz tuxum" orqali
  - [x] **Jojalar** — bitta bo'lim: joja ombori (harakatlar) + haftalik vaznlar bitta sahifada, jins filtri (Hammasi/Tovuq/Xo'roz)
  - [x] Dashboard kartalari: Tovuq/Xo'roz qoldiq + Joja sotuvi + Tuxum sotuvi
  - [x] URL/sidebar/admin/4 til yangilandi; brauzerda tekshirildi ✔
- [x] **Jojalar 3 bo'lim + Partiya** (2026-09-29):
  - [x] Jojalar sahifasi 3 tab: **Joja holati** (status: olingan/nobud/qoldiq + nobud yozuvlari) · **Haftalik vazn** · **Joja haridi**
  - [x] Joja holati "nobud bo'ldi" yozuvi: sana, joja turi, harakat turi (faqat nobud), soni, partiya
  - [x] Joja haridi: sana, joja turi, soni, dona narxi, jami (avto), partiya
  - [x] **Partiya** modeli qo'shildi — filial kabi, har partiya alohida hisoblanadi; **Partiyalar** boshqaruv sahifasi
  - [x] Partiya dropdown faol filialga qarab filtrlanadi
  - [x] Migratsiya, admin, 4 til, brauzer — tekshirildi ✔
- [x] **Moliya bo'limi soddalashtirildi** (2026-09-29):
  - [x] **Maosh** — bitta sana: endi *hodim, sana, summa* (oy va to'langan sana olib tashlandi)
  - [x] **Rasxod** — *sana, sabab (tanlanadigan), summa*; sabab yonida inline **"+"** bilan yangi sabab qo'shiladi (AJAX, darhol tanlanadi); erkin matnli sabab olib tashlandi
  - [x] **Kirimlar → Investitsiya** — *sana, partiya, summa* (manba olib tashlandi, partiyaga bog'landi)
  - [x] Sidebar/dashboard/admin/4 til yangilandi; brauzerda tekshirildi ✔
- [x] **Investitsiya + Partiya ruxsatlari** (2026-09-29):
  - [x] **Partiyalar** "Boshqaruv" bo'limiga ko'chdi — faqat super admin boshqaradi (filial bilan)
  - [x] **Investitsiyani faqat super admin kiritadi**; qo'shishda: sana, **kimga (filial/davlat)**, summa, partiya
  - [x] Filial hodimlari faqat **o'ziga ajratilgan** investitsiyani ko'radi (read-only, qo'shish/tahrirlash yo'q)
  - [x] Super admin barcha (yoki tanlangan filial) investitsiyalarini ko'radi
  - [x] Ruxsatlar test client bilan tekshirildi (hodim → 403); 4 til; check ✔ (brauzer sinovi keyingi safar)
- [x] **Dizayn yangilandi + Xodimlar** (2026-10-01):
  - [x] **Light (kunduzgi) asosiy tema** bo'ldi (oldin dark edi); dark endi almashtirgich orqali
  - [x] **Yashil sidebar** — oq kontentdan ajralib turadi (ko'zni charchatmaydi); CSS tokenlar bilan
  - [x] **Logo** qo'yildi: `static/img/logo.svg` (sidebar oq qutichada + login sahifada)
  - [x] **Xodim** modeli (login/parolsiz): ism, lavozim, oylik maosh, filial — "Xodimlar" bo'limi (Boshqaruv, super admin)
  - [x] **Maosh** endi `Xodim`ga bog'lanadi (User emas); filial hodimi o'z filial xodimidan tanlaydi
  - [x] Admin "Hodimlar" → "Foydalanuvchilar" (login akkauntlar) deb nomlandi
  - [x] Migratsiya, 4 til, brauzer bilan tekshirildi ✔
- [x] **Rang tuzatish + dashboard grafiklari** (2026-10-01):
  - [x] Light rejimda ko'rinmagan ranglar tuzatildi (alert, xabarlar, tag-chick endi tema o'zgaruvchilaridan)
  - [x] **Dashboard:** KPI kartalari **trend** (↑/↓ foiz, shu oy/o'tgan oy) bilan
  - [x] **Bar grafik** — investitsiya va rasxod (6 oy), animatsiyali; **donut** — sotuv tushumi (joja/tuxum)
  - [x] Animatsiyalar: kartalar reveal, sonlar count-up ($), grafik/donut o'sish
  - [x] Dark va light — ikkalasi ham tekshirildi ✔
- [x] **Tushum/Balans + tuzatishlar** (2026-10-01):
  - [x] "Qo'shish" tugmasi matni ko'rinmasdi (`.panel-head a` qoidasi yashil rang berardi) — tuzatildi (oq matn, to'q yashil tugma); barcha ro'yxat sahifalariga tegishli
  - [x] Dashboardga **Tushum (sotuvdan)** kartasi qo'shildi (sotuv tushumi)
  - [x] **Balans = Investitsiya − Rasxod + Tushum** (oldin: inv − rasxod)
  - [x] Rasxod = Rasxodlar + Maoshlar (o'zgarmagan)
  - [x] 4 KPI karta (Investitsiya/Rasxod/Tushum/Balans) — hammasi **bosiladigan** (tegishli sahifaga)
  - [x] Tushum uchun ham trend; brauzerda tekshirildi ✔
- [x] **Katta funksiyalar to'plami** (2026-10-01):
  - [x] **Joja vazni birligi** — gram/kg tanlanadi
  - [x] **24 soat qulfi** — filial hodimi yozuvni faqat 24 soat ichida tahrirlay/o'chira oladi (super admin doim); qulflangan qatorda qulf ikonkasi
  - [x] **O'chirish (savatcha)** tugmasi har qatorda (tahrirlash yonida)
  - [x] **Maxsus modal** o'chirishni tasdiqlaydi (browser alert emas) — blur, animatsiya
  - [x] **Hisobotlar** bo'limi (super admin): investitsiya/rasxod/sabablar/tushum/balans + **chiroyli PDF yuklab olish** (xhtml2pdf)
  - [x] **Aktivlik** jurnali (super admin): kim, qachon, qaysi IP, nima qildi (kirish/chiqish/qo'shish/tahrirlash/o'chirish) — signal + har amalda yoziladi
  - [x] Migratsiya, 4 til, test client + brauzer bilan tekshirildi ✔

- **2026-10-01 — Mijoz qo'shimchalari (6 ta):**
  - [x] **Login oynasi** — logo kattalashtirildi (168px), ortiqcha "DOA Nutrition" yozuvi olib tashlandi (logoning o'zida bor)
  - [x] **Sidebar logosi** kattalashtirildi (54px)
  - [x] **PDF turkcha shrift tuzatildi** — DejaVuSans (+Bold) `static/fonts/` ga qo'shildi, `@font-face` + `link_callback`; turkcha harflar (ş ğ İ ı ç ö ü …) endi to'rtburchak emas, to'g'ri chiqadi ✔ (pdfminer bilan tekshirildi)
  - [x] **Filial admini o'z filialiga xodim qo'sha oladi** — Xodim bo'limi barcha foydalanuvchilarga ochildi (MOLIYA menyusida), filial admini uchun filial avto-belgilanadi va faqat o'z filialidagi xodimni tahrirlay/o'chira oladi
    - Tuzatildi: majburiy (null=False) `filial` FK da `hasattr(inst,'filial')` bo'sh yozuvda `False` qaytarardi → `filial_id` orqali tekshirishga o'tildi (xodim saqlanmay qolgan edi)
    - `tahrirlash_mumkin`: `yaratilgan` maydoni yo'q modellar (Xodim) doim tahrirlanadi
  - [x] **Excel'simon ustun filtrlari** — har bir ustun sarlavhasida filtr (voronka) tugmasi: qiymatlar bo'yicha belgilash, qidiruv, o'sish/kamayish saralash; barcha jadvallarda (tuxum/joja sotuvi, investitsiya, rasxod, maosh, xodim, joja, aktivlik)
  - [x] **Ichki skroll** — ko'p qator bo'lsa karta ichida aylanadi (`max-height:62vh`), jadval sarlavhasi yopishib turadi (sticky)

- **2026-10-05 — PostgreSQL ga o'tish, ma'lumotlarni tozalash, kamchiliklarni to'ldirish:**
  - [x] **PostgreSQL ga ulandi** — `psycopg[binary]` o'rnatildi, `.env` ga `DATABASE_URL=postgres://postgres:***@localhost:5432/doanut`, barcha migratsiyalar PostgreSQL da qayta bajarildi; yozish/o'qish brauzerda tekshirildi ✔
  - [x] **Barcha soxta (demo) ma'lumotlar o'chirildi** — Kirim, Rasxod, Maosh, Sotuv, JojaHarakat, JojaVazn, Partiya, Xodim, Filial, Faoliyat, RasxodKategoriya = **0**. Dashboard butunlay **$0.00**. Faqat 1 super admin (`admin`) qoldirildi.
  - [x] **Raqamli validatsiya** (yangi) — summa/narx/vazn **0 dan katta**, soni **kamida 1**, oylik **manfiy emas** bo'lishi shart. Manfiy/nol kiritib bo'lmaydi (`MinValueValidator` + HTML `min`/`step`).
  - [x] **Parolni o'zgartirish** (yangi) — super admin uchun `/profil/parol/` sahifasi (eski parol + yangi parol 2 marta), account menyusida havola. O'zbekcha matnlar, aktivlikka yoziladi. (Filial xodimlari parolni o'zgartira olmaydi — avvalgidek.)
  - [x] **Birinchi ishga tushirish ko'rsatmasi** — super adminda filial bo'lmasa, dashboardda "Avval filial qo'shing →" bannerasi chiqadi.
  - [x] **4 tilda tarjima** — yangi matnlar (validatsiya, parol, onboarding) uz/tr/ru/en ga tarjima qilinib `compilemessages` qilindi; `.po` fayllari venv ifloslanishidan tozalandi (`--ignore=venv`).

  - [x] **Bildirishnoma (Notification) tizimi** — tizimda kimdir yangilik qilsa (qo'shish/tahrirlash/o'chirish) boshqalarga qo'ng'iroq keladi; **o'zi qilgan odamga kelmaydi**. Super adminlar hammasini, filial foydalanuvchilari faqat o'z filialidagi yangilikni oladi. Topbarda qo'ng'iroq + o'qilmaganlar soni, dropdown va `/bildirishnomalar/` sahifasi.
  - [x] **Fayl nomlari standartlashtirildi** — `parol.html` → `password_change.html`; yangi shablon `notifications.html` (inglizcha, standartga mos).
  - [x] **"Saqlanmoqda" overlay** — forma yuborilganda ekran xiralashib, markazda zamonaviy spinner + "Saqlanmoqda…/Kirilmoqda…/O'chirilmoqda…" chiqadi (sekin internetda ham ko'rinadi). `form[data-loading]` + `app.js`/`app.css`. 4 tilda.

  - [x] **Tuxum tug‘uvchanlik prognozi va samaradorligi (HDEP KPI)** — super admin uchun analitika sahifasi (`/tuxum-prognoz/`). Har partiyaning yoshi (hafta) + tirik tovuq + o‘rtacha vazndan **zot standarti HDEP egri chizig‘i** bo‘yicha kunlik kutilayotgan tuxum hisoblanadi; real yig‘im bilan solishtiriladi (yashil standart / qizil real chiziqli grafik). Partiyalar jadvali: standart/real HDEP, samaradorlik %, signal (🟢 a’lo / 🟡 e’tibor / 🔴 past) + tavsiya. Yangi model `TuxumYigim` (kunlik tuxum yig‘imi) + `egg_kpi.py` algoritmlari. 4 tilda.

  - [x] **Telegram bot integratsiyasi (@doa_nutritionbot)** — super admin uchun. Xavfsiz ulanish: saytdan (Telegram bo‘limi) **bir martalik 6 xonali kod** olinadi (15 daqiqa, bir marta), botga `/start` → kod yuboriladi → chat super adminga bog‘lanadi (Telegram ID kodga yozilmaydi, admin o‘zgarsa yangi kod olinadi). Bot: tizimdagi har bir yangilikni darhol yuboradi, har kuni soat 21:00 da kunlik hisobot (`TELEGRAM_HISOBOT_SOATI`), hamda interaktiv so‘rovlar `/balans /tuxum_qoldiq /joja_qoldiq /hisobot /uzish`. Token `.env` da (maxfiy). Long-polling: `python manage.py telegrambot`; cron hisobot: `telegram_hisobot`. Faqat stdlib + certifi (TLS). 4 tilda.

  - [x] **Botda til tanlash** — `/language` (yoki /start) → 🇺🇿🇬🇧🇷🇺🇹🇷. Tanlangan til `TelegramUlanish.til` da saqlanadi; bot barcha javoblarni, bildirishnoma va kunlik hisobotni **o'sha tilda** yuboradi (gettext + `override`). 4 tilga to'liq tarjima.
  - [x] **Bot buyruqlari inglizchaga** — `/balance`, `/eggs`, `/poultry`, `/report`, `/unlink`, `/language`, `/help`.
  - [x] **O'zbekcha fayl nomlari standartga (inglizcha)** — `jojalar.html→poultry.html`, `hisobotlar.html→reports.html`, `hisobot_pdf.html→report_pdf.html`, `aktivlik.html→activity.html`, `_joja_table.html→_poultry_table.html`, `_amallar.html→_actions.html`, komanda `telegram_hisobot→telegram_report`. Barcha referenslar yangilandi, tekshirildi (sahifalar + PDF 200).

  - [x] **Sof foyda** (Tushum − Rasxod) — dashboard (5-karta), hisobotlar, PDF va Telegram `/balance` ga qo'shildi.
  - [x] **Oylarni taqqoslash** — alohida sahifa emas, **Hisobotlar** sahifasi ichida (va PDF da). Ikki oyni tanlab (filter) solishtiradi: Investitsiya, Rasxod, Tushum, Sof foyda bo'yicha o'sish/kamayish % (jadval + rang: rasxod kamayishi=yashil, tushum/foyda o'sishi=yashil) + guruhli ustunli diagramma. `compare.py`. 4 tilda. (Mijoz so'rovi: hammasi bitta joyda bo'lsin.)

  - [x] **Excel (.xlsx) eksport** — Maosh, Rasxod, Joja sotuvi, Tuxum sotuvi jadvallarida "Qo'shish" oldida **Excel** tugmasi (dropdown: **Filter bo'yicha** / **Hammasini**). Chiroyli rangli: yashil header (oq bold), pul ustunlari `$` raqam formati, zebra, ramka, muzlatilgan sarlavha; sanalar jadvaldagidek. **Hammasi** = barcha yozuvlar (sahifalashdan oshadi), **Filter bo'yicha** = jadvaldagi ustun filtriga mos yozuvlar (serverda barcha yozuvlarga qo'llanadi). `openpyxl`, `export_xlsx.py`. CSV emas — toza xlsx.

  - [x] **To'liq audit (tozalash + xavfsizlik)** — `check --deploy` toza (0 ogohlantirish); pyflakes bo'yicha ilova kodida ortiqcha import/dead-code yo'q. Tuzatildi: (1) `pul` 3 joydan bitta `apps/common/utils.py` ga birlashtirildi; (2) Excel eksport POST noto'g'ri/buzuq ma'lumotда endi 500 bermaydi (himoyalandi); (3) 6 ta ishlatilmaydigan bo'sh Django stub fayl (backend `views.py`, `frontend/models.py`, `frontend/admin.py`) va `.DS_Store` o'chirildi. Xavfsizlik mustahkam: django-axes, parol validatorlari, HSTS/secure-cookie (SSL ostida), X-Frame DENY, filialга scoped querysetlar, CSRF.

  - [x] **Sidebar guruhlari yig'iladigan (dropdown)** — Asosiy/Moliya/Joja/Sotuv/Boshqaruv sarlavhalari bosilganda ochiladi/yopiladi (chevron aylanadi, silliq animatsiya). Holat localStorage'da eslab qolinadi; faol sahifa guruhi doim ochiq.
  - [x] **Telegram tugmalari** — reply-keyboard localizatsiyalangan rangli (💰 Balans/Balance/Баланс/Bakiye, 🥚 Tuxumlar…), tilга qarab o'zgaradi; endi har bir buyruq javobida keyboard yangilanadi (eski tugmalar darhol yangisiga almashadi). ⚠️ Yangi tugmalar ko'rinishi uchun bot jarayonини qayta ishga tushirish shart (`manage.py telegrambot`).

  - [x] **Tovuqlar bazasi + yangi Jojalar (ochirish) tizimi:**
    - Eski "Jojalar" bo'limi → **"Tovuqlar bazasi"** deb nomlandi (tovuq/xo'roz, jins bilan).
    - Yangi **"Jojalar"** bo'limi (`JojaOchirish`) — tuxumdan ochirilgan jojalar (jins yo'q): sana, tuxum soni, ochilgan soni → farqi avtomatik **nobud** (200 tuxum − 190 ochilgan = 10 nobud). Bu tovuqlar bazasiga qo'shilmaydi.
    - **Joja sotuvida manba tanlash**: *Jojalar (ochirilgan)* yoki *Tovuqlar bazasi*; tovuqlar bazasi tanlansa qo'shimcha **Tovuq/Xo'roz** tanlanadi. Sotilgan miqdor tegishli bazadan ayriladi (ortiqcha sotishdan himoya — manfiy qoldiq bo'lmaydi).
    - **Dashboardga "Jojalar qoldig'i"** kartasi qo'shildi; tovuq/xo'roz qoldiqlari endi sotuvlarni hisobga oladi. `stock.py` yagona qoldiq hisoblagich.

## 🔄 Hozir qilinmoqda

- Ko'p-filiallilik + til dropdown + light/dark tema tayyor.
- Test hisoblar: super admin `admin`; filial xodimi `uzbek_hodim` (parol: `Uzbek2026!`, Toshkent filiali).

## ⬜ Keyingi qadamlar (navbat bilan)

- [ ] Rollarga qarab ruxsatlar (hodim faqat o'ziga tegishlisini ko'rishi)
- [ ] O'chirish (delete) tugmasi frontendda
- [ ] Qidiruv/filtr (sana, valyuta) ro'yxat sahifalarida
- [ ] Hisobotlar (kunlik/oylik foyda-zarar), eksport (Excel/PDF)
- [ ] Mijoz qo'shimchalari (yangi talablar chiqqanda)
- [ ] PostgreSQL + deploy (DEBUG=False, HTTPS, `collectstatic`)

## ⚙️ Deploy eslatmasi (kelajak uchun)

Serverga qo'yishda: `.env` da `DJANGO_DEBUG=False`, `SECURE_SSL=True`,
`DJANGO_ALLOWED_HOSTS`ni to'ldirish, `python manage.py collectstatic`,
`compilemessages`. WhiteNoise static'ni o'zi tez uzatadi (alohida nginx shart emas).
- [ ] Dashboard'ni ombor va sotuv statistikasi bilan kengaytirish
- [ ] Yangi matnlar chiqqanda tarjimalarni yangilash (`makemessages` + `compilemessages`)
- [ ] Test va deploy (PostgreSQL)

---

## 📝 Qarorlar jurnali (nima uchun shunday qilindi)

| Sana | Qaror | Sabab |
|------|-------|-------|
| 2026-09-27 | Django + Unfold tanlandi | Mijoz talabi; admin panel tayyor, xavfsiz |
| 2026-09-27 | `apps/` papkasida modullar | Toza, kengayadigan tuzilish |
| 2026-09-27 | Ombor holati hisoblab chiqiladi | Ma'lumot takrorlanmasin (kirim − sotuv) |
| 2026-09-27 | Ko'p valyuta: UZS, USD, TRY | Mijoz: asosan so'm va dollar, ba'zida turk lirasi |
| 2026-09-27 | django-axes, simple_history, .env | Yuqori xavfsizlik talabi |

## ❓ Mijozdan kutilayotgan qo'shimchalar

Mijoz: *"yana qo'shib boraman qo'shimchalar"* — yangi talablar shu yerga qo'shiladi.
