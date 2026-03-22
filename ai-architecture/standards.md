# AI Standards

## Паттерн вызова AI (обязательный)

```typescript
const prompt = this.promptService.getPrompt('key', { var1, var2 });
const cacheKey = this.aiCacheService.computeHash('service_type', prompt);
const cached = await this.aiCacheService.get(cacheKey);
if (cached !== null) {
  await this.aiCacheService.incrementHit(cacheKey);
  return cached;
}
const message = await this.anthropic.messages.create({ model, max_tokens, messages });
await this.billingService.recordTokenUsage(userId, { ... });
const result = this.parseResult(message.content[0].text);
await this.aiCacheService.set(cacheKey, 'service_type', entityId, result, tokens);
return result;
```

## Правила
1. Всегда кэшировать через `AiCacheService`
2. Всегда биллить через `BillingService.recordTokenUsage()`
3. Промты только через `PromptService.getPrompt()` — не хардкодить
4. Парсить JSON с fallback на raw text
5. Логировать cache hit/miss через `this.logger.log()`
