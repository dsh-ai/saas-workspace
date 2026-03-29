# PostHog Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Self-hosted PostHog on 37.9.7.141, frontend (posthog-js) + backend (posthog-node) hybrid integration with user identification and key funnel events.

**Architecture:** PostHog runs via docker-compose on the GlitchTip VPS (37.9.7.141). Frontend uses PostHogProvider wrapping the app. Backend has a singleton PostHogService injected into AuthService, BillingService, AiRouterService, and ResponsesService.

**Tech Stack:** PostHog self-hosted (docker-compose), posthog-js (Next.js 16), posthog-node (NestJS), nginx, certbot

---

## Task 1: Deploy PostHog via docker-compose on 37.9.7.141

**Files:**
- Create on server: `/opt/posthog/docker-compose.yml`

**Step 1: SSH into VPS and clone PostHog**

```bash
ssh root@37.9.7.141
mkdir -p /opt/posthog && cd /opt/posthog
git clone https://github.com/PostHog/posthog.git . --depth=1
```

**Step 2: Configure PostHog**

```bash
cp .env.template .env
```

Edit `/opt/posthog/.env` — set:
```
POSTHOG_SECRET=<generate: python3 -c "import secrets; print(secrets.token_hex(32))">
SITE_URL=https://posthog.unilist.ru
EMAIL_HOST=smtp.yandex.ru
```

**Step 3: Start PostHog**

```bash
docker compose -f docker-compose.yml up -d
```

Wait 2-3 minutes. Check:
```bash
docker compose ps
```
Expected: all containers `running` (web, worker, clickhouse, redis, postgres).

**Step 4: Verify PostHog is up**

```bash
curl http://localhost:8000/
```
Expected: HTML response (PostHog login page).

---

## Task 2: Configure nginx + SSL for posthog.unilist.ru

**Files:**
- Create on server: `/etc/nginx/sites-available/posthog`

**Step 1: Add nginx config**

```bash
cat > /etc/nginx/sites-available/posthog << 'EOF'
server {
    listen 80;
    server_name posthog.unilist.ru;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

ln -s /etc/nginx/sites-available/posthog /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

**Step 2: Issue SSL certificate**

```bash
certbot --nginx -d posthog.unilist.ru --non-interactive --agree-tos -m admin@unilist.ru
```

Expected: "Successfully deployed certificate".

**Step 3: Verify**

Open https://posthog.unilist.ru in browser.
Expected: PostHog signup/login page.
Create admin account. **Save API key** — it looks like `phc_xxxx`.

---

## Task 3: Frontend — install posthog-js and create lib/posthog.ts

**Working directory:** `/Users/shuvaev/Продукты/unilist/dev_unilist/frontend`

**Files:**
- Create: `lib/posthog.ts`

**Step 1: Install posthog-js**

```bash
npm install posthog-js
```

**Step 2: Create lib/posthog.ts**

```typescript
import posthog from 'posthog-js';

export function initPostHog() {
  if (typeof window === 'undefined') return;
  if (!process.env.NEXT_PUBLIC_POSTHOG_KEY) return;

  posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY, {
    api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST ?? 'https://posthog.unilist.ru',
    capture_pageview: false, // managed manually via usePathname
    persistence: 'localStorage',
  });
}

export { posthog };
```

**Step 3: Commit**

```bash
git add lib/posthog.ts package.json package-lock.json
git commit -m "feat(analytics): install posthog-js and create init helper"
```

---

## Task 4: Frontend — create PostHogProvider

**Files:**
- Create: `components/providers/posthog-provider.tsx`

**Step 1: Create the provider**

```tsx
'use client';

import { useEffect } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';
import { initPostHog, posthog } from '@/lib/posthog';

export function PostHogProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    initPostHog();
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const url = pathname + (searchParams.toString() ? `?${searchParams.toString()}` : '');
    posthog.capture('$pageview', { $current_url: window.location.origin + url });
  }, [pathname, searchParams]);

  return <>{children}</>;
}
```

**Step 2: Wrap app in layout.tsx**

Modify `app/layout.tsx`:

```tsx
import { PostHogProvider } from '@/components/providers/posthog-provider';
import { Suspense } from 'react';
```

Wrap the body content:
```tsx
<AuthProvider>
  <ToastProvider>
    <Suspense fallback={null}>
      <PostHogProvider>
        {children}
      </PostHogProvider>
    </Suspense>
  </ToastProvider>
</AuthProvider>
```

Note: `Suspense` is required because `useSearchParams()` needs it in Next.js App Router.

**Step 3: Commit**

```bash
git add components/providers/posthog-provider.tsx app/layout.tsx
git commit -m "feat(analytics): add PostHogProvider with pageview tracking"
```

---

## Task 5: Frontend — identify/reset users in AuthProvider

**Files:**
- Modify: `components/providers/auth-provider.tsx`

**Step 1: Add posthog calls**

Add import at top:
```typescript
import { posthog } from '@/lib/posthog';
```

In `useEffect` after `api.get<User>('/auth/profile').then(setUser)`, add identify:
```typescript
.then((u) => {
  setUser(u);
  posthog.identify(u.id, {
    email: u.email,
    name: u.name,
    plan: u.plan,
    company: u.company,
    industry: u.industry,
  });
})
```

In `login` callback, after `setUser(data.user)`:
```typescript
posthog.identify(data.user.id, {
  email: data.user.email,
  name: data.user.name,
  plan: data.user.plan,
  company: data.user.company,
  industry: data.user.industry,
});
```

In `register` callback, after `setUser(data.user)`:
```typescript
posthog.identify(data.user.id, {
  email: data.user.email,
  name: data.user.name,
  plan: data.user.plan,
});
```

In `logout` callback, after `logoutFn()`:
```typescript
posthog.reset();
```

**Step 2: Check User type has the right fields**

Run:
```bash
grep -n "plan\|company\|industry" lib/types.ts
```
Expected: fields exist. If not, they may be optional — use `u.plan ?? undefined`.

**Step 3: Commit**

```bash
git add components/providers/auth-provider.tsx
git commit -m "feat(analytics): identify/reset posthog user on auth state change"
```

---

## Task 6: Frontend — add key UI events

**Files:**
- Modify: relevant page/component files where actions happen

**Step 1: Find where surveys/questionnaires are created and sent**

```bash
grep -rn "createSurvey\|create.*survey\|create.*questionnaire\|handleCreate\|onSubmit" app/surveys/ app/dashboard/ components/ --include="*.tsx" -l
```

**Step 2: Add questionnaire_created event**

In the survey creation handler, after successful API call:
```typescript
import { posthog } from '@/lib/posthog';
// ...
posthog.capture('questionnaire_created');
```

**Step 3: Add questionnaire_sent event**

In the send/share handler (where link is sent to client), after success:
```typescript
posthog.capture('questionnaire_sent', { surveyId });
```

**Step 4: Add upgrade_clicked event**

In the billing/upgrade button click handler:
```typescript
posthog.capture('upgrade_clicked', { from_plan: user.plan });
```

**Step 5: Add ai_summary_viewed event**

In the AI analysis/summary view, on mount or button click:
```typescript
posthog.capture('ai_summary_viewed', { surveyId });
```

**Step 6: Commit**

```bash
git add -p   # stage only relevant changes
git commit -m "feat(analytics): add key UI events to posthog"
```

---

## Task 7: Backend — create PostHogService and AnalyticsModule

**Working directory:** `/Users/shuvaev/Продукты/unilist/dev_unilist/backend`

**Files:**
- Create: `src/analytics/posthog.service.ts`
- Create: `src/analytics/analytics.module.ts`

**Step 1: Install posthog-node**

```bash
npm install posthog-node
```

**Step 2: Create src/analytics/posthog.service.ts**

```typescript
import { Injectable, OnModuleDestroy, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { PostHog } from 'posthog-node';

@Injectable()
export class PostHogService implements OnModuleDestroy {
  private readonly client: PostHog | null = null;
  private readonly logger = new Logger(PostHogService.name);

  constructor(private readonly configService: ConfigService) {
    const key = configService.get<string>('POSTHOG_KEY');
    const host = configService.get<string>('POSTHOG_HOST');
    if (key) {
      this.client = new PostHog(key, { host: host ?? 'https://posthog.unilist.ru' });
    } else {
      this.logger.warn('POSTHOG_KEY not set — analytics disabled');
    }
  }

  capture(distinctId: string, event: string, properties?: Record<string, unknown>) {
    if (!this.client) return;
    this.client.capture({ distinctId, event, properties });
  }

  identify(distinctId: string, properties: Record<string, unknown>) {
    if (!this.client) return;
    this.client.identify({ distinctId, properties });
  }

  async onModuleDestroy() {
    await this.client?.shutdown();
  }
}
```

**Step 3: Create src/analytics/analytics.module.ts**

```typescript
import { Global, Module } from '@nestjs/common';
import { PostHogService } from './posthog.service';

@Global()
@Module({
  providers: [PostHogService],
  exports: [PostHogService],
})
export class AnalyticsModule {}
```

**Step 4: Commit**

```bash
git add src/analytics/ package.json package-lock.json
git commit -m "feat(analytics): add PostHogService and AnalyticsModule"
```

---

## Task 8: Backend — register AnalyticsModule in AppModule

**Files:**
- Modify: `src/app.module.ts`

**Step 1: Add import**

Add to imports at top of file:
```typescript
import { AnalyticsModule } from './analytics/analytics.module';
```

Add `AnalyticsModule` to the `imports` array (before other modules).

**Step 2: Verify it builds**

```bash
npm run build 2>&1 | tail -5
```
Expected: no errors.

**Step 3: Commit**

```bash
git add src/app.module.ts
git commit -m "feat(analytics): register AnalyticsModule globally"
```

---

## Task 9: Backend — add user_registered event in AuthService

**Files:**
- Modify: `src/auth/auth.service.ts`

**Step 1: Inject PostHogService**

Add to constructor:
```typescript
private readonly posthog: PostHogService,
```

Add import:
```typescript
import { PostHogService } from '../analytics/posthog.service';
```

**Step 2: Add identify + event in register()**

After `return { accessToken, refreshToken, user: this.usersService.toDto(user) }` — but BEFORE the return, add:

```typescript
this.posthog.identify(user.id, { email: user.email, plan: user.plan });
this.posthog.capture(user.id, 'user_registered', { email: user.email });
```

**Step 3: Commit**

```bash
git add src/auth/auth.service.ts
git commit -m "feat(analytics): track user_registered in AuthService"
```

---

## Task 10: Backend — add subscription_changed event in BillingService

**Files:**
- Modify: `src/billing/billing.service.ts`

**Step 1: Inject PostHogService**

Add to constructor:
```typescript
private readonly posthog: PostHogService,
```

Add import:
```typescript
import { PostHogService } from '../analytics/posthog.service';
```

**Step 2: Add event in activateSubscription()**

Find method `activateSubscription` (line ~149). After the user plan is saved, add:

```typescript
this.posthog.capture(userId, 'subscription_changed', {
  plan: priceInfo.plan,
  planCode,
  amount: priceInfo.amount,
  currency: priceInfo.currency,
});
this.posthog.identify(userId, { plan: priceInfo.plan });
```

**Step 3: Commit**

```bash
git add src/billing/billing.service.ts
git commit -m "feat(analytics): track subscription_changed in BillingService"
```

---

## Task 11: Backend — add ai_request_completed event in AiRouterService

**Files:**
- Modify: `src/ai/ai-router.service.ts`

**Step 1: Inject PostHogService**

Add to constructor:
```typescript
private readonly posthog: PostHogService,
```

Add import:
```typescript
import { PostHogService } from '../analytics/posthog.service';
```

**Step 2: Update method signatures to accept userId**

The callers of `callRussian` and `callGlobal` need to pass `userId`. Check which services call AiRouterService:

```bash
grep -rn "aiRouter\|AiRouterService\|callRussian\|callGlobal" src/ --include="*.ts" -l
```

Add optional `userId?: string` parameter to `callRussian` and `callGlobal`. At the end of each method, before `return`:

```typescript
if (userId) {
  this.posthog.capture(userId, 'ai_request_completed', {
    provider: result.provider,
    model: result.model,
    inputTokens: result.inputTokens,
    outputTokens: result.outputTokens,
    costUsd: result.costUsd,
  });
}
```

**Step 3: Commit**

```bash
git add src/ai/ai-router.service.ts
git commit -m "feat(analytics): track ai_request_completed in AiRouterService"
```

---

## Task 12: Backend — add questionnaire_response_received in ResponsesService

**Files:**
- Modify: `src/responses/responses.service.ts`

**Step 1: Inject PostHogService**

Add to constructor and add import (same pattern as above).

**Step 2: Add event in submit()**

Find method `submit` (line ~49). After `response.submittedAt = new Date()` and save, add:

```typescript
// surveyOwnerId is the userId who owns this survey — get it from survey.userId
this.posthog.capture(response.survey.userId, 'questionnaire_response_received', {
  surveyId: response.survey.id,
  responseId: response.id,
});
```

Note: check if `survey.userId` is available — if not, load the survey first.

**Step 3: Commit**

```bash
git add src/responses/responses.service.ts
git commit -m "feat(analytics): track questionnaire_response_received in ResponsesService"
```

---

## Task 13: Set env variables and verify

**Step 1: Add to frontend .env.local**

```
NEXT_PUBLIC_POSTHOG_KEY=phc_xxxx
NEXT_PUBLIC_POSTHOG_HOST=https://posthog.unilist.ru
```

**Step 2: Add to backend .env**

```
POSTHOG_KEY=phc_xxxx
POSTHOG_HOST=https://posthog.unilist.ru
```

**Step 3: Add to Coolify env vars**

In Coolify UI for frontend app → Environment Variables:
- `NEXT_PUBLIC_POSTHOG_KEY` = `phc_xxxx`
- `NEXT_PUBLIC_POSTHOG_HOST` = `https://posthog.unilist.ru`

In Coolify UI for backend app → Environment Variables:
- `POSTHOG_KEY` = `phc_xxxx`
- `POSTHOG_HOST` = `https://posthog.unilist.ru`

**Step 4: Push and deploy**

```bash
git push origin main
```

**Step 5: Smoke test**

1. Open https://app.unilist.ru
2. In PostHog → Live Events — check `$pageview` appears
3. Register new user → check `user_registered` event with correct properties
4. Login → check identify call in PostHog → People
5. Create a survey → check `questionnaire_created`
