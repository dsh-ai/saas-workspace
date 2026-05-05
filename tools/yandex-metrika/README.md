# Yandex Metrika tools

## create-goals.py

Создаёт цели в Метрике через [Management API](https://yandex.ru/dev/metrika/ru/management/openapi/goal/addGoal).

### Подготовка

1. **Получить OAuth-токен** с правом записи (`metrika:write`):
   - Зарегистрировать приложение: https://oauth.yandex.com/client/new
     - Платформа: Web-сервисы
     - Redirect URI: `https://oauth.yandex.ru/verification_code`
     - Права: «Яндекс.Метрика → Создание счётчиков, изменение параметров…» + «Получение статистики…»
   - Получить токен (Implicit flow): открыть в браузере
     `https://oauth.yandex.ru/authorize?response_type=token&client_id=<CLIENT_ID>`
   - Из URL после редиректа скопировать `access_token`.

2. **Положить креды:**
   ```
   cp .secrets/yandex-metrika.env.example .secrets/yandex-metrika.env
   # вписать YM_TOKEN
   ```

### Использование

```bash
cd tools/yandex-metrika
python create-goals.py --list      # посмотреть, что уже есть
python create-goals.py --dry-run   # показать payload без отправки
python create-goals.py             # создать все цели из goals.json
```

Скрипт пропускает цели, имя которых уже существует на счётчике.

### Состав целей (goals.json)

53 цели типа JavaScript-событие (`action`) — полный каталог из
`marketing/analytics/yandex-metrika-events.md` (разделы 2–10).

Сгруппированы по секциям лендинга: Hero, Navbar, Footer, Mobile menu,
Sticky CTA, Pricing, FAQ, Integrations, Blog (индекс/карусель/статья со
скролл-метриками), Final CTA, How, и микроконверсии главной (скролл/время).

Источник правды по идентификаторам и местам вставки `ym(...)` —
`marketing/analytics/yandex-metrika-events.md`.

### Передача событий из кода

```js
// JS-цели типа action
ym(97774201, 'reachGoal', 'cta_click_hero');
ym(97774201, 'reachGoal', 'form_submit');
```

В Tilda — добавить в HTML-блок T123 на нужные кнопки/формы:
```html
<script>
  document.querySelector('.t-btn').addEventListener('click', function() {
    ym(97774201, 'reachGoal', 'cta_click_hero');
  });
</script>
```
