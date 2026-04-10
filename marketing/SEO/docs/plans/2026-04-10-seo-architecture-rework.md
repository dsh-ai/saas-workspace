# SEO-архитектура: реализация переработки

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Перестроить SEO-архитектуру unilist.ru под три тематических кластера для сегмента РОП/B2B, опубликовать все материалы одновременно.

**Architecture:** Три независимых кластера («Клиент завис», «Конверсия воронки», «Контроль менеджеров»), каждый с пиллар-статьёй + спутниками + конвертирующим лендингом. Пиллар — широкий охват темы + внутренние ссылки на спутники. Спутники — узкие под конкретный запрос + ссылка на пиллар.

**Стек:** Markdown-статьи в `marketing/Контент/<slug>/blog-<slug>.md`, лендинги в `dev_unilist/` (отдельная задача для разработчика). SEO-метаданные фиксируются в каждом md-файле.

---

## Задача 1: Пиллар — «Клиент завис»

**Файл:** создать `marketing/Контент/klient-zavis-chto-delat-ropu/blog-klient-zavis-chto-delat-ropu.md`

**Запрос:** «почему клиент не отвечает» (600/мес, +146%)

**Шаг 1: Создать файл статьи**

```markdown
---
title: "Клиент завис: полный гид для РОПа — что делать когда клиент не отвечает"
h1: "Клиент завис после анкеты: что делать РОПу — полный разбор"
slug: klient-zavis-chto-delat-ropu
target_query: "почему клиент не отвечает"
volume: 600
cluster: 1-klient-zavis
type: pillar
---
```

**Шаг 2: Структура пиллара (разделы H2)**

```
## Почему клиент перестаёт отвечать: 6 реальных причин
## Как понять что происходит — без звонка клиенту
## 5 сигналов что сделка умирает прямо сейчас
## Что делать РОПу: пошаговый алгоритм
## Как не допустить зависания: системное решение
## Инструменты для отслеживания активности клиента
```

**Шаг 3: Внутренние ссылки (обязательно включить в текст)**

- → `/blog/pochemu-klient-ne-otvechaet` («подробнее о причинах»)
- → `/blog/5-signalov-chto-klient-zavis` («читай про сигналы»)
- → `/blog/risk-poteri-sdelki` («как оценить риск потери»)
- → `/dlya-ropa` (CTA в конце: «инструмент для отслеживания»)

**Шаг 4: Мета-теги**

```
Title: Клиент не отвечает после анкеты: что делать РОПу — полный гид | Unilist
Description: Клиент получил документы и пропал? Разбираем 6 причин, алгоритм действий для РОПа и как видеть активность клиента без созвонов.
```

**Шаг 5: Коммит**

```bash
git add marketing/Контент/klient-zavis-chto-delat-ropu/
git commit -m "content: add pillar article — klient-zavis cluster"
```

---

## Задача 2: Спутник кластера 1 — «Риск потери сделки»

**Файл:** создать `marketing/Контент/risk-poteri-sdelki/blog-risk-poteri-sdelki.md`

**Запрос:** «риск потери клиентов» (520/мес)

**Шаг 1: Создать файл**

```markdown
---
title: "Риск потери сделки в B2B: как распознать и предотвратить"
h1: "Риск потери сделки: 7 признаков что клиент уходит и как это остановить"
slug: risk-poteri-sdelki
target_query: "риск потери клиентов"
volume: 520
cluster: 1-klient-zavis
type: satellite
---
```

**Шаг 2: Структура (H2)**

```
## Почему B2B-сделки срываются на финальных этапах
## 7 признаков высокого риска потери клиента
## Как оценить риск по поведению клиента с анкетой
## Что делать при каждом уровне риска
## Как выстроить систему раннего предупреждения
```

**Шаг 3: Внутренние ссылки**

- → `/blog/klient-zavis-chto-delat-ropu` (пиллар, в начале статьи)
- → `/dlya-ropa` (CTA)

**Шаг 4: Мета-теги**

```
Title: Риск потери клиента в B2B: 7 признаков и как предотвратить | Unilist
Description: Разбираем сигналы высокого риска потери сделки на этапе сбора требований. Как видеть угрозу раньше чем клиент скажет «нет».
```

**Шаг 5: Коммит**

```bash
git add marketing/Контент/risk-poteri-sdelki/
git commit -m "content: add satellite — risk-poteri-sdelki"
```

---

## Задача 3: Обновить спутники кластера 1 (существующие)

**Файлы:**
- Изменить: `marketing/Контент/pochemu-klienty-ne-zapolnyayut-oprosnyye-listy/blog-pochemu-klienty-ne-zapolnyayut-oprosnyye-listy.md`
- Изменить: `marketing/Контент/5-signalov-chto-klient-zavis-na-oprosnike/blog-5-signalov-chto-klient-zavis-na-oprosnike.md`

**Шаг 1: В обе статьи добавить в начало (после intro)**

```markdown
> Если хочешь разобраться в теме глубже — читай полный гид:  
> [Клиент завис: что делать РОПу](/blog/klient-zavis-chto-delat-ropu)
```

**Шаг 2: В обе статьи добавить в конец перед CTA**

```markdown
**По теме:**
- [Риск потери сделки: 7 признаков](/blog/risk-poteri-sdelki)
- [Клиент завис: полный гид для РОПа](/blog/klient-zavis-chto-delat-ropu)
```

**Шаг 3: Коммит**

```bash
git add marketing/Контент/pochemu-klienty-ne-zapolnyayut-oprosnyye-listy/
git add marketing/Контент/5-signalov-chto-klient-zavis-na-oprosnike/
git commit -m "content: add internal links — cluster 1 satellites"
```

---

## Задача 4: Пиллар — «Конверсия воронки»

**Файл:** создать `marketing/Контент/konversiya-voronki-prodazh/blog-konversiya-voronki-prodazh.md`

**Запрос:** «конверсия воронки продаж» (550/мес, +29%)

**Шаг 1: Создать файл**

```markdown
---
title: "Конверсия воронки продаж B2B: полный гид по измерению и росту"
h1: "Конверсия воронки продаж: как измерить, где теряем и как исправить"
slug: konversiya-voronki-prodazh
target_query: "конверсия воронки продаж"
volume: 550
cluster: 2-konversiya
type: pillar
---
```

**Шаг 2: Структура (H2)**

```
## Что такое конверсия воронки продаж и зачем её измерять
## Ключевые метрики: что считать на каждом этапе
## Скрытый этап: между встречей и КП
## Почему падает конверсия на этапе анкеты
## Как найти где именно теряются сделки
## Инструменты для отслеживания конверсии
```

**Шаг 3: Внутренние ссылки**

- → `/blog/kak-izmerit-konversiyu` (спутник)
- → `/blog/oprosnyye-listy-ubivayut-konversiyu` (спутник)
- → `/blog/gde-teryayutsya-sdelki-b2b` (спутник)
- → `/kvalifikatsiya-lidov` (CTA)

**Шаг 4: Мета-теги**

```
Title: Конверсия воронки продаж B2B: как измерить и где теряем | Unilist
Description: Полный гид по конверсии воронки продаж: метрики, скрытые потери на этапе анкеты, инструменты контроля. Для РОПов B2B-компаний.
```

**Шаг 5: Коммит**

```bash
git add marketing/Контент/konversiya-voronki-prodazh/
git commit -m "content: add pillar article — konversiya-voronki cluster"
```

---

## Задача 5: Спутник кластера 2 — «Где теряются сделки»

**Файл:** создать `marketing/Контент/gde-teryayutsya-sdelki-b2b/blog-gde-teryayutsya-sdelki-b2b.md`

**Запрос:** «метрики воронки продаж» (235/мес)

**Шаг 1: Создать файл**

```markdown
---
title: "Где теряются сделки в B2B: разбор воронки по этапам"
h1: "Где теряются сделки в B2B воронке: 5 мест потерь и как их найти"
slug: gde-teryayutsya-sdelki-b2b
target_query: "метрики воронки продаж"
volume: 235
cluster: 2-konversiya
type: satellite
---
```

**Шаг 2: Структура (H2)**

```
## Почему сделки срываются там где вы не смотрите
## 5 этапов воронки где чаще всего теряют клиентов
## Этап анкеты и требований: самая тёмная зона
## Как посчитать потери на каждом этапе
## Что значат эти числа и что делать дальше
```

**Шаг 3: Внутренние ссылки**

- → `/blog/konversiya-voronki-prodazh` (пиллар, в начале)
- → `/kvalifikatsiya-lidov` (CTA)

**Шаг 4: Мета-теги**

```
Title: Где теряются сделки в B2B: разбор воронки по этапам | Unilist
Description: Разбираем 5 мест в B2B-воронке где чаще всего уходят клиенты. Как найти свою точку потерь и что с ней делать.
```

**Шаг 5: Коммит**

```bash
git add marketing/Контент/gde-teryayutsya-sdelki-b2b/
git commit -m "content: add satellite — gde-teryayutsya-sdelki"
```

---

## Задача 6: Обновить спутники кластера 2 (существующие)

**Файлы:**
- Изменить: `marketing/Контент/kak-izmerit-konversiyu-na-etape-oprosnogo-lista/blog-kak-izmerit-konversiyu-na-etape-oprosnogo-lista.md`
- Изменить: `marketing/Контент/oprosnyye-listy-ubivayut-konversiyu/blog-oprosnyye-listy-ubivayut-konversiyu.md`

**Шаг 1: В обе статьи добавить ссылку на пиллар (после intro)**

```markdown
> Полный разбор темы — в нашем гиде:  
> [Конверсия воронки продаж: как измерить и где теряем](/blog/konversiya-voronki-prodazh)
```

**Шаг 2: Добавить блок «По теме» в конце**

```markdown
**По теме:**
- [Где теряются сделки в B2B](/blog/gde-teryayutsya-sdelki-b2b)
- [Конверсия воронки продаж: полный гид](/blog/konversiya-voronki-prodazh)
```

**Шаг 3: Коммит**

```bash
git add marketing/Контент/kak-izmerit-konversiyu-na-etape-oprosnogo-lista/
git add marketing/Контент/oprosnyye-listy-ubivayut-konversiyu/
git commit -m "content: add internal links — cluster 2 satellites"
```

---

## Задача 7: Пиллар — «Контроль менеджеров»

**Файл:** создать `marketing/Контент/kontrol-menedzherov-bez-zvonkov/blog-kontrol-menedzherov-bez-zvonkov.md`

**Запрос:** «контроль менеджеров по продажам» (210/мес, +17%)

**Шаг 1: Создать файл**

```markdown
---
title: "Контроль менеджеров по продажам без созвонов: инструменты и методы"
h1: "Как РОП контролирует менеджеров без созвонов и отчётов — полный гид"
slug: kontrol-menedzherov-bez-zvonkov
target_query: "контроль менеджеров по продажам"
volume: 210
cluster: 3-kontrol
type: pillar
---
```

**Шаг 2: Структура (H2)**

```
## Почему традиционный контроль менеджеров не работает
## Что РОП должен видеть — и чего обычно не видит
## Контроль через активность клиента: новый подход
## KPI менеджера по продажам: что реально важно
## Инструменты контроля без микроменеджмента
## Как выстроить систему видимости за 1 неделю
```

**Шаг 3: Внутренние ссылки**

- → `/blog/kpi-menedzherov-po-prodazham` (спутник)
- → `/blog/kak-oprosnyy-list-vliyaet-na-kp` (спутник)
- → `/blog/oprosnyy-list-est-u-vsekh-upravlyaet-nikto` (спутник)
- → `/dlya-ropa` (CTA)
- → `/integratsiya-bitrix24` (CTA для Bitrix24-аудитории)

**Шаг 4: Мета-теги**

```
Title: Контроль менеджеров по продажам без созвонов: инструменты | Unilist
Description: Как РОП видит что происходит в сделках без созвонов с менеджерами. Инструменты контроля через активность клиента.
```

**Шаг 5: Коммит**

```bash
git add marketing/Контент/kontrol-menedzherov-bez-zvonkov/
git commit -m "content: add pillar article — kontrol-menedzherov cluster"
```

---

## Задача 8: Спутник кластера 3 — «KPI менеджеров»

**Файл:** создать `marketing/Контент/kpi-menedzherov-po-prodazham/blog-kpi-menedzherov-po-prodazham.md`

**Запрос:** «KPI менеджера по продажам» (772/мес)

**Шаг 1: Создать файл**

```markdown
---
title: "KPI менеджера по продажам: какие метрики реально важны для РОПа"
h1: "KPI менеджера по продажам: 7 метрик которые реально важны"
slug: kpi-menedzherov-po-prodazham
target_query: "KPI менеджера по продажам"
volume: 772
cluster: 3-kontrol
type: satellite
---
```

**Шаг 2: Структура (H2)**

```
## Почему стандартные KPI менеджера не показывают реальную картину
## 7 метрик которые РОП должен отслеживать
## Что делать с KPI на этапе сбора требований
## Как связать KPI менеджера с активностью клиента
## Инструменты для отслеживания KPI без Excel
```

**Шаг 3: Внутренние ссылки**

- → `/blog/kontrol-menedzherov-bez-zvonkov` (пиллар, в начале)
- → `/dlya-ropa` (CTA)

**Шаг 4: Мета-теги**

```
Title: KPI менеджера по продажам: 7 метрик которые реально важны | Unilist
Description: Какие KPI менеджера по продажам действительно показывают проблемы в воронке. Для РОПов которые хотят видеть, а не догадываться.
```

**Шаг 5: Коммит**

```bash
git add marketing/Контент/kpi-menedzherov-po-prodazham/
git commit -m "content: add satellite — kpi-menedzherov"
```

---

## Задача 9: Обновить спутники кластера 3 (существующие)

**Файлы:**
- Изменить: `marketing/Контент/kak-oprosnyy-list-vliyaet-na-kachestvo-kp/blog-kak-oprosnyy-list-vliyaet-na-kachestvo-kp.md`
- Изменить: `marketing/Контент/oprosnyy-list-est-u-vsekh-upravlyaet-nikto/blog-oprosnyy-list-est-u-vsekh-upravlyaet-nikto.md`

**Шаг 1: Переосмыслить `kak-oprosnyy-list-vliyaet-na-kp`**

Текущий угол: «как опросный лист влияет на качество КП».  
Новый угол: «как РОП контролирует качество данных через опросный лист».  
Обновить H1: «Опросный лист как инструмент контроля: как РОП видит качество работы менеджера».

**Шаг 2: В обе статьи добавить ссылку на пиллар**

```markdown
> Полный разбор темы:  
> [Как РОП контролирует менеджеров без созвонов](/blog/kontrol-menedzherov-bez-zvonkov)
```

**Шаг 3: Добавить блок «По теме»**

```markdown
**По теме:**
- [KPI менеджера по продажам: 7 метрик](/blog/kpi-menedzherov-po-prodazham)
- [Контроль менеджеров без созвонов: полный гид](/blog/kontrol-menedzherov-bez-zvonkov)
```

**Шаг 4: Коммит**

```bash
git add marketing/Контент/kak-oprosnyy-list-vliyaet-na-kachestvo-kp/
git add marketing/Контент/oprosnyy-list-est-u-vsekh-upravlyaet-nikto/
git commit -m "content: update satellites + add internal links — cluster 3"
```

---

## Задача 10: Обновить SEO-архитектуру

**Файл:** заменить `marketing/SEO/pages/seo-architecture.md` новой версией.

**Шаг 1:** Скопировать ключевые данные из дизайн-документа  
`marketing/SEO/docs/plans/2026-04-10-seo-architecture-rework-design.md`  
и переписать `seo-architecture.md` как актуальный reference-документ.

**Шаг 2:** Обновить `marketing/Контент/content-plan.md` — добавить новые статьи в раздел «В работе».

**Шаг 3: Коммит**

```bash
git add marketing/SEO/pages/seo-architecture.md
git add marketing/Контент/content-plan.md
git commit -m "docs: update SEO architecture and content plan"
```

---

## Задача 11: Лендинги — задача для разработчика

> Эти изменения вносятся в `/Users/shuvaev/Продукты/unilist/dev_unilist/` — отдельный репозиторий.

**`/dlya-ropa`** — доработать:
- H1: «Unilist для РОПа: видите что происходит с клиентом — без созвонов»
- Добавить блок «Читайте также»: ссылки на пилларов кластеров 1 и 3
- CTA: «Попробовать бесплатно» → `app.unilist.ru`

**`/kvalifikatsiya-lidov`** — доработать:
- Добавить блок «Читайте также»: ссылки на пиллар и спутники кластера 2
- CTA: «Попробовать бесплатно» → `app.unilist.ru`

**`/integratsiya-bitrix24`** — доработать:
- Добавить блок «Читайте также»: ссылки на пиллар кластера 3
- CTA: «Установить из Marketplace»

---

## Итог: что публикуем одновременно

| # | Материал | Тип | Кластер |
|---|---|---|---|
| 1 | `klient-zavis-chto-delat-ropu` | Пиллар | 1 |
| 2 | `risk-poteri-sdelki` | Спутник | 1 |
| 3 | `konversiya-voronki-prodazh` | Пиллар | 2 |
| 4 | `gde-teryayutsya-sdelki-b2b` | Спутник | 2 |
| 5 | `kontrol-menedzherov-bez-zvonkov` | Пиллар | 3 |
| 6 | `kpi-menedzherov-po-prodazham` | Спутник | 3 |
| 7–12 | 6 существующих статей | Обновление | все |
| 13–15 | 3 лендинга | Обновление | все |
