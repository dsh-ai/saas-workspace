# PostHog Code Integration

## Конфигурация

| Переменная | Значение |
|---|---|
| `POSTHOG_HOST` | `https://posthog.unilist.ru` |
| `POSTHOG_KEY` | API key из PostHog UI (Settings → Project → API Key) |

В Coolify выставить для обоих сервисов: frontend (Next.js) и backend (NestJS).

---

## Frontend (Next.js)

### Зависимость

```bash
npm install posthog-js
```

### lib/posthog.ts

```typescript
import posthog from 'posthog-js';

export const initPostHog = () => {
  if (typeof window !== 'undefined') {
    posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
      api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://posthog.unilist.ru',
      capture_pageview: false, // вручную через usePathname
    });
  }
};

export { posthog };
```

### PostHogProvider

Обёртка провайдера в `app/layout.tsx`. Отслеживает смену роутов через `usePathname`.

### AuthProvider — identify/reset

```typescript
// При логине:
posthog.identify(user.id, { email: user.email, name: user.name });

// При логауте:
posthog.reset();
```

### UI события

| Событие | Триггер |
|---|---|
| `questionnaire_submitted` | Отправка анкеты |
| `ai_request_started` | Запрос к AI |
| `upgrade_clicked` | Клик на апгрейд |
| `trial_banner_viewed` | Показ trial баннера |

---

## Backend (NestJS)

### Зависимость

```bash
npm install posthog-node
```

### PostHogService (`src/analytics/posthog.service.ts`)

```typescript
import { PostHog } from 'posthog-node';

@Injectable()
export class PostHogService implements OnModuleDestroy {
  private client: PostHog;

  constructor() {
    this.client = new PostHog(process.env.POSTHOG_KEY!, {
      host: process.env.POSTHOG_HOST || 'https://posthog.unilist.ru',
    });
  }

  capture(distinctId: string, event: string, properties?: Record<string, any>) {
    this.client.capture({ distinctId, event, properties });
  }

  async onModuleDestroy() {
    await this.client.shutdown();
  }
}
```

### AnalyticsModule

Зарегистрирован в `AppModule`. `PostHogService` экспортирован как глобальный.

### Backend события

| Событие | Сервис | Когда |
|---|---|---|
| `user_registered` | AuthService | После успешной регистрации |
| `subscription_changed` | BillingService | После изменения подписки |
| `ai_request_completed` | AiRouterService | После успешного AI запроса |
| `questionnaire_response_received` | ResponsesService | После получения ответа на анкету |

### Пример вызова

```typescript
this.posthog.capture(userId, 'user_registered', {
  email: user.email,
  plan: 'trial',
});
```
