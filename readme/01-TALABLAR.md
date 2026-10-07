# 📋 Biznes Talablar

> Manba: **`Platforma DOA Nutrition.docx`** (mijoz yozgan). Quyida asl matn va uning aniq tushuntirishi.

## Asl matn (Word fayldan)

```
1. Kirim pul investitsiya
2. Rasxod kunlik (nimagaligini yozish). Oylik maoshlarni alohida
3. Tovuq va tuxumlar bazasi summasi soni
4. Tuxum kiritish — bazada nechta tuxum borligini ko'rsa bo'ladi, brak tuxumlar
   ham yoziladi, sotishda necha pulga sotayotganini yozadi, tuxumni nechta sotganini ham
5. Tovuqni ham kiritish bazaga va sotish. Bu bo'limda haftalik tovuqning vazni
6. Sotuv — tovuq sotadimi tuxum sotadimi, qanchadan sotdi, qancha sotdi — hammasi
```

---

## Tushuntirilgan talablar

### 1. 💰 Kirim (Investitsiya)
- Kompaniyaga tushgan pul / investitsiyalar qayd etiladi.
- Kerakli maydonlar: **summa**, **sana**, **manba/izoh** (kim/nima uchun), **kim kiritdi**.

### 2. 💸 Rasxod (Xarajatlar)
- **Kunlik xarajatlar** — har bir xarajatning **sababi yoziladi** (nimaga sarflandi).
- **Oylik maoshlar alohida** — hodimlar maoshi alohida bo'lim/model sifatida.
- Kerakli maydonlar: summa, sana, kategoriya/sabab, izoh.

### 3. 🐔🥚 Tovuq va Tuxum bazasi (Ombor)
- Umumiy baza: hozir omborда **nechta** tovuq/tuxum bor va ular **qancha summaga** teng.
- Ya'ni har doim: **soni** + **umumiy qiymati (summa)** ko'rinib turishi kerak.

### 4. 🥚 Tuxum bo'limi (aniqlashtirildi 2026-09-28)
- **Tuxum kirimi** — faqat **nechta qo'shildi** (sana bilan). **Narx YO'Q**, chunki
  tuxum sotib olinmaydi — tovuqdan olinadi, shunchaki omborga qo'shiladi.
- **Brak tuxum** — **alohida** bo'lim: soni + **sabab** bilan qo'shiladi.
- Ombor qoldig'i = kirim − brak − sotilgan.

### 5. 🐔 Tovuq bo'limi (aniqlashtirildi 2026-09-28)
- **Tovuq ombori (harakat)** — har yozuv ikki xil:
  - **Qo'shildi (sotib olindi)**: soni, sana, **narx (qanchaga)**, sabab
  - **Kasallandi / nobud bo'ldi**: soni, sana, sabab
- Ombor qoldig'i = qo'shilgan − kasal/nobud − sotilgan.
- **Haftalik vazn** — sana tanlanadi, o'sha hafta o'rtacha vazni (kg) yoziladi.

### 6.5. 🏢 Ko'p-filiallilik (aniqlashtirildi 2026-09-28)
- **Super admin** (Turkiyada, bosh) — barcha filiallarni bitta platformadan kuzatadi.
- **Filiallar**: hozir **O'zbekiston**, keyin Tojikiston, Turkmaniston qo'shiladi.
- Super admin har filialga **login/parol** beradi.
- Filial xodimlari **faqat o'z filiali** ma'lumotini ko'radi va yuritadi.
- Super admin yuqoridagi almashtirgichdan filial tanlaydi yoki "Barcha filiallar"ni ko'radi.

### 6. 🛒 Sotuv (umumiy)
- Sotuv turi: **tovuq** yoki **tuxum**.
- **Qanchadan** sotdi (birlik narxi), **qancha** sotdi (soni), **jami** summa.
- Sana va (ixtiyoriy) xaridor.

---

## ❓ Ochiq savollar (mijozdan aniqlashtirish kerak)

Bular keyinroq mijoz "qo'shimcha" qilganda aniqlashadi:

- [ ] Valyuta qaysi? (so'm / dollar?)
- [ ] Tovuqlar partiyalab (guruh) hisoblanadimi yoki bittalab?
- [ ] Tuxum "brak" bo'lganda alohida sababi yoziladimi?
- [ ] Maosh — har oy bir marta to'lanadimi, avans bo'ladimi?
- [ ] Hisobotlar (kunlik/oylik foyda-zarar) kerakmi?
- [ ] Necha xil hodim roli bor? (admin, buxgalter, oddiy hodim...)

> Mijoz aytgan edi: **"yana qo'shib boraman qo'shimchalar"** — shu sababli talablar
> kengayib boradi, model'lar moslashuvchan qilib quriladi.
