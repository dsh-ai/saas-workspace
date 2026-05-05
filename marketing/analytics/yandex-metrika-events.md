# Яндекс Метрика — карта событий unilist.ru

**Назначение:** каталог всех событий и целей для Яндекс Метрики на лендинге `unilist.ru` и блоге `unilist.ru/blog`. Используется для:
1. Создания целей в Метрике (UI: «Цели» → «Добавить цель» → JavaScript-событие).
2. Вставки `ym(...)` в код React/HTML.

**Заполнить перед использованием:**
- `COUNTER_ID` — номер счётчика Метрики (в коде встроен в `window.ym`).

**Конвенция Goal ID:** `snake_case`, латиница, формат `<секция>_<действие>_<цель>`.

---

## 0. Базовая интеграция (один раз в `layout.tsx`)

```tsx
// src/components/analytics/yandex-metrika.tsx
"use client";

import Script from "next/script";

const ID = process.env.NEXT_PUBLIC_YM_ID;

export function YandexMetrika() {
  if (!ID) return null;
  return (
    <>
      <Script
        id="ym-init"
        strategy="afterInteractive"
        dangerouslySetInnerHTML={{
          __html: `(function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
m[i].l=1*new Date();for (var j = 0; j < document.scripts.length; j++) {if (document.scripts[j].src === r) { return; }}
k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)})
(window, document, "script", "https://mc.yandex.ru/metrika/tag.js?id=${ID}", "ym");
ym(${ID}, "init", { defer: true, clickmap: true, trackLinks: true, accurateTrackBounce: true, webvisor: true, ecommerce: "dataLayer" });`,
        }}
      />
      <noscript>
        <div>
          <img src={`https://mc.yandex.ru/watch/${ID}`} style={{ position: "absolute", left: "-9999px" }} alt="" />
        </div>
      </noscript>
    </>
  );
}
```

В `src/app/layout.tsx`:
```tsx
<body>
  <YandexMetrika />
  {children}
</body>
```

В `.env.production` (через Coolify env vars):
```
NEXT_PUBLIC_YM_ID=12345678
```

**Хелпер** для всех reachGoal-вызовов (типобезопасно):

```tsx
// src/lib/analytics.ts
type GoalParams = Record<string, unknown>;

declare global {
  interface Window {
    ym?: (counterId: number, action: string, ...args: unknown[]) => void;
  }
}

const COUNTER_ID = Number(process.env.NEXT_PUBLIC_YM_ID);

export function track(goal: string, params?: GoalParams) {
  if (!COUNTER_ID || typeof window === "undefined" || !window.ym) return;
  window.ym(COUNTER_ID, "reachGoal", goal, params);
}

export function trackParams(params: GoalParams) {
  if (!COUNTER_ID || typeof window === "undefined" || !window.ym) return;
  window.ym(COUNTER_ID, "params", params);
}
```

Использование в компоненте:
```tsx
import { track } from "@/lib/analytics";
<Link href="..." onClick={() => track("cta_register_hero")}>...</Link>
```

---

## 1. Pageview (просмотры страниц)

Метрика автоматически фиксирует переход и History API. Дополнительно отправляем кастомные параметры визита для разделения по типам.

| Событие | Где | JS-вызов |
|---|---|---|
| Просмотр главной | `/` | `ym(${COUNTER_ID}, 'params', { page_type: 'home' })` |
| Просмотр блог-индекса | `/blog/` | `ym(${COUNTER_ID}, 'params', { page_type: 'blog_index' })` |
| Просмотр статьи блога | `/blog/[slug]/` | `ym(${COUNTER_ID}, 'params', { page_type: 'blog_article', slug: '<slug>', cluster: '<cluster>' })` |
| Просмотр 404 | `/404` | `ym(${COUNTER_ID}, 'params', { page_type: 'not_found' })` |

**Goal в Метрике:** не нужен (pageview есть нативно), достаточно параметров визита.

---

## 2. Hero (главная)

| Goal ID | Человеческое название | Где | JS |
|---|---|---|---|
| `hero_pill_register` | Клик на pill «Трекер опросных листов для роста конверсии» → ведёт на регистрацию | Hero, верхний баннер | `ym(${COUNTER_ID}, 'reachGoal', 'hero_pill_register')` |
| `hero_pill_changelog` | (legacy) Клик на pill «Новое: 14 пилотных команд» | Hero, верхний баннер | `ym(${COUNTER_ID}, 'reachGoal', 'hero_pill_changelog')` |
| `cta_register_hero` | Hero CTA — Создать опросный лист за 5 минут | Hero, основной CTA | `ym(${COUNTER_ID}, 'reachGoal', 'cta_register_hero', { source: 'hero' })` |
| `cta_demo_hero` | Hero CTA — Посмотреть 2-минутное демо | Hero, вторичный CTA | `ym(${COUNTER_ID}, 'reachGoal', 'cta_demo_hero')` |

---

## 3. Навигация (Navbar + Footer)

| Goal ID | Человеческое название | Где | JS |
|---|---|---|---|
| `nav_logo_home` | Клик на логотип Unilist в шапке | Navbar | `ym(${COUNTER_ID}, 'reachGoal', 'nav_logo_home')` |
| `nav_anchor_features` | Переход к разделу «Возможности» | Navbar | `ym(${COUNTER_ID}, 'reachGoal', 'nav_anchor_features')` |
| `nav_anchor_how` | Переход к разделу «Как работает» | Navbar | `ym(${COUNTER_ID}, 'reachGoal', 'nav_anchor_how')` |
| `nav_anchor_pricing` | Переход к разделу «Тарифы» | Navbar | `ym(${COUNTER_ID}, 'reachGoal', 'nav_anchor_pricing')` |
| `nav_anchor_faq` | Переход к разделу «FAQ» | Navbar | `ym(${COUNTER_ID}, 'reachGoal', 'nav_anchor_faq')` |
| `nav_open_blog` | Переход в блог из навигации | Navbar | `ym(${COUNTER_ID}, 'reachGoal', 'nav_open_blog')` |
| `cta_login_navbar` | Клик «Войти» в шапке | Navbar | `ym(${COUNTER_ID}, 'reachGoal', 'cta_login_navbar')` |
| `cta_register_navbar` | Клик «Попробовать бесплатно» в шапке | Navbar | `ym(${COUNTER_ID}, 'reachGoal', 'cta_register_navbar', { source: 'navbar' })` |
| `mobile_menu_toggle` | Открытие/закрытие mobile-меню | Navbar | `ym(${COUNTER_ID}, 'reachGoal', 'mobile_menu_toggle', { state: open ? 'open' : 'close' })` |
| `cta_register_mobile_menu` | CTA из mobile-меню | Navbar | `ym(${COUNTER_ID}, 'reachGoal', 'cta_register_mobile_menu', { source: 'mobile_menu' })` |
| `footer_link_features` | Footer → Возможности | Footer | `ym(${COUNTER_ID}, 'reachGoal', 'footer_link_features')` |
| `footer_link_how` | Footer → Как работает | Footer | `ym(${COUNTER_ID}, 'reachGoal', 'footer_link_how')` |
| `footer_link_pricing` | Footer → Тарифы | Footer | `ym(${COUNTER_ID}, 'reachGoal', 'footer_link_pricing')` |
| `footer_link_faq` | Footer → FAQ | Footer | `ym(${COUNTER_ID}, 'reachGoal', 'footer_link_faq')` |
| `footer_link_blog` | Footer → Блог | Footer | `ym(${COUNTER_ID}, 'reachGoal', 'footer_link_blog')` |
| `footer_link_telegram` | Footer → Telegram | Footer | `ym(${COUNTER_ID}, 'reachGoal', 'footer_link_telegram')` |
| `footer_link_email` | Footer → Email | Footer | `ym(${COUNTER_ID}, 'reachGoal', 'footer_link_email')` |
| `footer_link_legal_offer` | Footer → Оферта | Footer | `ym(${COUNTER_ID}, 'reachGoal', 'footer_link_legal_offer')` |
| `footer_link_legal_privacy` | Footer → Политика конфиденциальности | Footer | `ym(${COUNTER_ID}, 'reachGoal', 'footer_link_legal_privacy')` |
| `footer_link_legal_pdn` | Footer → Обработка ПДн | Footer | `ym(${COUNTER_ID}, 'reachGoal', 'footer_link_legal_pdn')` |
| `cta_register_footer` | CTA «14 дней бесплатно» в футере | Footer | `ym(${COUNTER_ID}, 'reachGoal', 'cta_register_footer', { source: 'footer' })` |

---

## 3a. Familiar (секция «Знакомо?»)

| Goal ID | Человеческое название | Где | JS |
|---|---|---|---|
| `cta_register_familiar` | CTA под секцией «Знакомо?» — регистрация | Familiar | `ym(${COUNTER_ID}, 'reachGoal', 'cta_register_familiar', { source: 'familiar' })` |

---

## 4. Sticky CTA (mobile)

| Goal ID | Человеческое название | Где | JS |
|---|---|---|---|
| `cta_register_sticky` | Sticky CTA на mobile — Создать за 5 минут | StickyCta | `ym(${COUNTER_ID}, 'reachGoal', 'cta_register_sticky', { source: 'sticky_mobile' })` |

---

## 5. Pricing

| Goal ID | Человеческое название | Где | JS |
|---|---|---|---|
| `pricing_toggle_monthly` | Переключение на помесячную оплату | Pricing toggle | `ym(${COUNTER_ID}, 'reachGoal', 'pricing_toggle_monthly')` |
| `pricing_toggle_yearly` | Переключение на годовую оплату (-20%) | Pricing toggle | `ym(${COUNTER_ID}, 'reachGoal', 'pricing_toggle_yearly')` |
| `cta_register_pricing_trial` | Тариф Trial → Начать бесплатно | Pricing | `ym(${COUNTER_ID}, 'reachGoal', 'cta_register_pricing_trial', { plan: 'trial', billing: '<monthly\|yearly>', price: 0 })` |
| `cta_register_pricing_base` | Тариф Базовый → Выбрать | Pricing | `ym(${COUNTER_ID}, 'reachGoal', 'cta_register_pricing_base', { plan: 'base', billing, price })` |
| `cta_register_pricing_ai` | Тариф AI → Выбрать | Pricing | `ym(${COUNTER_ID}, 'reachGoal', 'cta_register_pricing_ai', { plan: 'ai', billing, price })` |

**E-commerce** (опционально, для воронки в Метрике):
```js
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  ecommerce: {
    currencyCode: 'RUB',
    detail: { products: [{ id: 'plan_base', name: 'Базовый', price: 1990, category: 'subscription' }] }
  }
});
```

---

## 6. FAQ

| Goal ID | Человеческое название | Где | JS |
|---|---|---|---|
| `faq_open_question` | Открытие вопроса в FAQ | FAQ accordion | `ym(${COUNTER_ID}, 'reachGoal', 'faq_open_question', { question: '<short slug>' })` |
| `cta_telegram_faq` | FAQ → Написать в Telegram | FAQ support card | `ym(${COUNTER_ID}, 'reachGoal', 'cta_telegram_faq', { source: 'faq_support' })` |

---

## 7. Integrations

| Goal ID | Человеческое название | Где | JS |
|---|---|---|---|
| `integrations_request` | Клик «Запросить интеграцию» | Integrations | `ym(${COUNTER_ID}, 'reachGoal', 'integrations_request')` |
| `integrations_card_click` | Клик по карточке интеграции (Bitrix24/AmoCRM/...) | Integrations | `ym(${COUNTER_ID}, 'reachGoal', 'integrations_card_click', { integration: '<name>', status: '<live\|soon\|roadmap>' })` |

---

## 8. Blog

### Блог-индекс (`/blog/`)
| Goal ID | Человеческое название | Где | JS |
|---|---|---|---|
| `blog_article_open` | Открытие статьи из списка | /blog | `ym(${COUNTER_ID}, 'reachGoal', 'blog_article_open', { slug, source: 'blog_index' })` |

### Блог-карусель на главной
| Goal ID | Человеческое название | Где | JS |
|---|---|---|---|
| `blog_strip_article` | Открытие статьи из ленты на главной | BlogStrip | `ym(${COUNTER_ID}, 'reachGoal', 'blog_strip_article', { slug, source: 'home_blog_strip' })` |
| `blog_strip_all` | Клик «Все статьи» из ленты на главной | BlogStrip | `ym(${COUNTER_ID}, 'reachGoal', 'blog_strip_all')` |

### Страница статьи (`/blog/[slug]/`)
| Goal ID | Человеческое название | Где | JS |
|---|---|---|---|
| `blog_back_to_index` | Клик «← Все статьи» в шапке статьи | Article header | `ym(${COUNTER_ID}, 'reachGoal', 'blog_back_to_index', { from_slug })` |
| `blog_source_click` | Клик на источник из секции «Источники» | Article body | `ym(${COUNTER_ID}, 'reachGoal', 'blog_source_click', { url, slug })` |
| `cta_register_article` | CTA в конце статьи — Создать за 5 минут | Article CTA | `ym(${COUNTER_ID}, 'reachGoal', 'cta_register_article', { source: 'article', slug })` |
| `cta_telegram_article` | CTA в конце статьи — Поговорить с фаундером | Article CTA | `ym(${COUNTER_ID}, 'reachGoal', 'cta_telegram_article', { source: 'article', slug })` |
| `article_scroll_25` | Прочитал 25% статьи | Scroll | `ym(${COUNTER_ID}, 'reachGoal', 'article_scroll_25', { slug })` |
| `article_scroll_50` | Прочитал 50% статьи | Scroll | `ym(${COUNTER_ID}, 'reachGoal', 'article_scroll_50', { slug })` |
| `article_scroll_75` | Прочитал 75% статьи | Scroll | `ym(${COUNTER_ID}, 'reachGoal', 'article_scroll_75', { slug })` |
| `article_scroll_100` | Прочитал 100% статьи | Scroll | `ym(${COUNTER_ID}, 'reachGoal', 'article_scroll_100', { slug })` |

---

## 9. Final CTA + Bento + How

| Goal ID | Человеческое название | Где | JS |
|---|---|---|---|
| `cta_register_final` | Финальный CTA — Создать за 5 минут | CtaFinal | `ym(${COUNTER_ID}, 'reachGoal', 'cta_register_final', { source: 'cta_final' })` |
| `cta_telegram_final` | Финальный CTA — Поговорить с фаундером | CtaFinal | `ym(${COUNTER_ID}, 'reachGoal', 'cta_telegram_final', { source: 'cta_final' })` |
| `how_demo_video` | Клик «Демо-видео» (anchor `#demo`) | Hero / How | `ym(${COUNTER_ID}, 'reachGoal', 'how_demo_video')` |

---

## 10. Микро-конверсии (необязательные, по желанию)

| Goal ID | Человеческое название | Где | JS |
|---|---|---|---|
| `scroll_depth_50` | Доскролл главной до 50% | Home | `ym(${COUNTER_ID}, 'reachGoal', 'scroll_depth_50')` |
| `scroll_depth_75` | Доскролл главной до 75% | Home | `ym(${COUNTER_ID}, 'reachGoal', 'scroll_depth_75')` |
| `scroll_depth_100` | Доскролл главной до низа | Home | `ym(${COUNTER_ID}, 'reachGoal', 'scroll_depth_100')` |
| `time_on_page_30s` | Провёл на странице 30 сек | Home | `ym(${COUNTER_ID}, 'reachGoal', 'time_on_page_30s')` |
| `time_on_page_60s` | Провёл на странице 60 сек | Home | `ym(${COUNTER_ID}, 'reachGoal', 'time_on_page_60s')` |

---

## 11. Сводный список Goal ID (для импорта в Метрику)

Метрика не поддерживает массовый импорт целей через API/CSV — нужно создавать вручную в UI: **Цели → Добавить → JavaScript-событие → Идентификатор**. Список:

```
hero_pill_register
hero_pill_changelog
cta_register_hero
cta_demo_hero
nav_logo_home
nav_anchor_features
nav_anchor_how
nav_anchor_pricing
nav_anchor_faq
nav_open_blog
cta_login_navbar
cta_register_navbar
mobile_menu_toggle
cta_register_mobile_menu
footer_link_features
footer_link_how
footer_link_pricing
footer_link_faq
footer_link_blog
footer_link_telegram
footer_link_email
footer_link_legal_offer
footer_link_legal_privacy
footer_link_legal_pdn
cta_register_footer
cta_register_sticky
cta_register_familiar
pricing_toggle_monthly
pricing_toggle_yearly
cta_register_pricing_trial
cta_register_pricing_base
cta_register_pricing_ai
faq_open_question
cta_telegram_faq
integrations_request
integrations_card_click
blog_article_open
blog_strip_article
blog_strip_all
blog_back_to_index
blog_source_click
cta_register_article
cta_telegram_article
article_scroll_25
article_scroll_50
article_scroll_75
article_scroll_100
cta_register_final
cta_telegram_final
how_demo_video
scroll_depth_50
scroll_depth_75
scroll_depth_100
time_on_page_30s
time_on_page_60s
```

**Приоритет (если выберете не все):**
- **Must-have (макро-конверсии):** все `cta_register_*`, `cta_telegram_*`, `pricing_toggle_*`.
- **Should-have:** `blog_article_open`, `blog_strip_article`, `faq_open_question`, `mobile_menu_toggle`.
- **Nice-to-have:** scroll/time-метрики, footer-ссылки, integrations.

---

## 12. Готовые сниппеты для разметки в коде

### LinkButton-обёртка с reachGoal
```tsx
// src/components/analytics/tracked-link.tsx
"use client";

import Link, { type LinkProps } from "next/link";
import type { ComponentProps, ReactNode } from "react";
import { track } from "@/lib/analytics";

type Props = LinkProps &
  Omit<ComponentProps<"a">, keyof LinkProps> & {
    children: ReactNode;
    goal: string;
    goalParams?: Record<string, unknown>;
  };

export function TrackedLink({ goal, goalParams, onClick, children, ...rest }: Props) {
  return (
    <Link
      {...rest}
      onClick={(e) => {
        track(goal, goalParams);
        onClick?.(e);
      }}
    >
      {children}
    </Link>
  );
}
```

Использование:
```tsx
<TrackedLink
  href="https://app.unilist.ru/auth/register"
  goal="cta_register_hero"
  goalParams={{ source: "hero" }}
  className="btn-gradient"
>
  Создать опросный лист за 5 минут
</TrackedLink>
```

### Кнопка с reachGoal (inline)
```tsx
<button
  onClick={() => {
    setOpen((s) => !s);
    track("mobile_menu_toggle", { state: !open ? "open" : "close" });
  }}
>
  ...
</button>
```

### Параметры визита для блог-страницы
```tsx
// /blog/[slug] page.tsx — useEffect через client-component
"use client";
import { useEffect } from "react";
import { trackParams } from "@/lib/analytics";

export function BlogParams({ slug, cluster }: { slug: string; cluster?: string }) {
  useEffect(() => {
    trackParams({ page_type: "blog_article", slug, cluster });
  }, [slug, cluster]);
  return null;
}
```

### Скролл-глубина статьи (один компонент на странице)
```tsx
"use client";
import { useEffect } from "react";
import { track } from "@/lib/analytics";

export function ArticleScrollDepth({ slug }: { slug: string }) {
  useEffect(() => {
    const fired = new Set<number>();
    function onScroll() {
      const h = document.documentElement;
      const scrolled = (h.scrollTop + window.innerHeight) / h.scrollHeight;
      [0.25, 0.5, 0.75, 1].forEach((d) => {
        const pct = Math.round(d * 100);
        if (scrolled >= d && !fired.has(pct)) {
          fired.add(pct);
          track(`article_scroll_${pct}`, { slug });
        }
      });
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [slug]);
  return null;
}
```

---

## 13. Чеклист внедрения

- [ ] Получить `COUNTER_ID` в Яндекс Метрике (https://metrika.yandex.ru)
- [ ] Добавить `NEXT_PUBLIC_YM_ID=...` в Coolify env (prod-приложение `qv3mhlmk7b8eov7ge9u5myn3`)
- [ ] Создать `src/components/analytics/yandex-metrika.tsx` (раздел 0)
- [ ] Подключить `<YandexMetrika />` в `layout.tsx`
- [ ] Создать `src/lib/analytics.ts` с хелперами `track` / `trackParams`
- [ ] Создать `src/components/analytics/tracked-link.tsx`
- [ ] Заменить ключевые `<Link>` и `<LinkButton>` на `<TrackedLink>` с goal-атрибутами
- [ ] Добавить `<BlogParams />` в `/blog/[slug]/page.tsx`
- [ ] Добавить `<ArticleScrollDepth />` в `/blog/[slug]/page.tsx`
- [ ] Добавить scroll/time-handlers на `/` (если включаем nice-to-have)
- [ ] **Создать все цели в UI Метрики** (раздел 11 — список Goal ID)
- [ ] Прогнать через `https://metrika.yandex.ru/list` → отчёт «Конверсии» — убедиться, что цели приходят
- [ ] Включить вебвизор (`webvisor: true` уже в init) и проверить запись сессий
- [ ] Подключить `clickmap` / тепловую карту — уже включён через `init`

---

## Полезные ссылки

- Документация Метрики по reachGoal: https://yandex.ru/support/metrika/objects/reachgoal.html
- Параметры визита: https://yandex.ru/support/metrika/objects/params-method.html
- E-commerce dataLayer: https://yandex.ru/support/metrika/data/e-commerce.html
- Цели через JavaScript-событие: https://yandex.ru/support/metrika/general/goals-js-event.html
