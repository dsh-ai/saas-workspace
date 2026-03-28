# trigger emails

## Структура проекта

```
/Users/shuvaev/Продукты/unilist/saas-workspace/product_process/trigger emails
MEMORY.md
```

## Готовые артефакты

| Файл | Содержит | Статус |
|------|---------|--------|
| `docs/plans/2026-03-28-email-lifecycle-design.md` | Дизайн-документ: карта сценариев, дизайн-система, тексты 14 писем | ✅ Готово |
| `docs/plans/2026-03-28-email-lifecycle-implementation.md` | План реализации: 16 задач, HTML-шаблоны | ✅ Готово |
| `templates/_base/transactional.html` | Базовый шаблон Family A (минималистичный) | ✅ Готово |
| `templates/_base/lifecycle.html` | Базовый шаблон Family B (брендированный, синяя полоска) | ✅ Готово |
| `templates/T1-confirm-email/` | Подтверждение email | ✅ Готово |
| `templates/T2-welcome/` | Добро пожаловать | ✅ Готово |
| `templates/T3-payment-success/` | Квитанция об оплате | ✅ Готово |
| `templates/T4-payment-failed/` | Ошибка оплаты | ✅ Готово |
| `templates/T5-reset-password/` | Сброс пароля | ✅ Готово |
| `templates/L1-onboarding-day1/` | Онбординг: день 1 (+1ч после подтверждения) | ✅ Готово |
| `templates/L2-onboarding-day3/` | Онбординг: день 3 (нет анкет) | ✅ Готово |
| `templates/L3-onboarding-day7/` | Онбординг: день 7 (нет CRM-интеграции) | ✅ Готово |
| `templates/L4-trial-ending/` | Trial заканчивается (за 3 дня) | ✅ Готово |
| `templates/L5-trial-expired/` | Trial истёк | ✅ Готово |
| `templates/L6-payment-reminder-5d/` | Напоминание об оплате (за 5 дней) | ✅ Готово |
| `templates/L7-payment-reminder-1d/` | Предстоящее списание (за 1 день) | ✅ Готово |
| `templates/L8-subscription-paused/` | Подписка приостановлена | ✅ Готово |
| `templates/L9-reactivation/` | Реактивация (14 дней без активности) | ✅ Готово |

## ESP

**UnisenderGo** — переменные в формате `{{variable_name}}`

## Дизайн-система

- **Акцентный цвет:** `#0000FF`
- **Шрифт:** Golos Text (400/700/900) + fallback Arial
- **Фон страницы:** `#F6F6F6`
- **Фон письма:** `#FFFFFF`
- **Family A (Transactional):** без синей полоски, простой футер
- **Family B (Lifecycle):** синяя полоска 4px сверху, расширенный футер
