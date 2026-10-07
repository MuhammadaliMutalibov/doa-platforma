# 🐔 DOA Nutrition — Boshqaruv Platformasi

> Bu papka loyihaning **"miyyasi"** (brain). Bu yerda loyiha haqida hamma narsa yozib boriladi:
> **nima qilish kerak, nima qilindi, nima qoldi.** Har bir ish qadamida shu papka yangilanadi.

---

## 📌 Loyiha nima?

**DOA Nutrition** — parranda fermasi (tovuq va tuxum) kompaniyasi uchun **ichki boshqaruv paneli** (admin panel).
Kompaniya hodimlari shu platforma orqali kompaniyaning butun moliyaviy va tovar aylanmasini boshqaradi:

- 💰 **Kirim** — investitsiya va tushган pullar
- 💸 **Rasxod** — kunlik xarajatlar va oylik maoshlar
- 🐔 **Tovuq bazasi** — tovuqlar soni, summasi, haftalik vazni
- 🥚 **Tuxum bazasi** — tuxumlar soni, brak (yaroqsiz) tuxumlar
- 🛒 **Sotuv** — tovuq/tuxum sotuvi (narx va soni)
- 📊 **Dashboard** — umumiy hisob-kitob va statistika

## 🎯 Asosiy maqsadlar

1. **Xavfsizlik yuqori bo'lishi** — bu kompaniyaning ichki moliyaviy ma'lumotlari, himoya kuchli bo'lishi shart.
2. **Dizayn chiroyli va tushunarli** — hodimlar oson foydalana olsin.
3. **Aniq hisob-kitob** — har bir kirim/chiqim, tovar aylanmasi izlanadigan (traceable) bo'lsin.

## 🛠 Texnologiyalar

| Qatlam | Tanlov | Sabab |
|--------|--------|-------|
| Til | Python 3.10+ | Django uchun |
| Framework | Django 5.x | Kuchli, xavfsiz, admin paneli tayyor |
| Admin UI | **django-unfold** | Zamonaviy, chiroyli admin tema |
| Baza (dev) | SQLite | Ishlab chiqishda oson |
| Baza (prod) | PostgreSQL | Ishonchli, ko'p foydalanuvchi |
| Konfiguratsiya | django-environ | Maxfiy kalitlarni `.env` da saqlash |
| Login himoyasi | django-axes | Bruteforce hujumdan himoya |
| O'zgarishlar tarixi | django-simple-history | Kim nima o'zgartirganini kuzatish |

---

## 🗂 "Miyya" papkasidagi hujjatlar

Quyidagi tartibda o'qing:

| Fayl | Nima haqida |
|------|-------------|
| [`01-TALABLAR.md`](./01-TALABLAR.md) | Word fayldagi biznes talablar, tushuntirib berilgan |
| [`02-ARXITEKTURA.md`](./02-ARXITEKTURA.md) | Texnik reja: Django app'lar, modellar, xavfsizlik |
| [`03-HOLAT.md`](./03-HOLAT.md) | ✅ Nima qilindi / 🔄 nima qilinmoqda / ⬜ nima qoldi |

---

*Oxirgi yangilanish: 2026-09-27*
