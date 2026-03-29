# PostHog Infrastructure

## Сервер

- **VPS:** Selectel, Ubuntu 22.04, IP `37.9.7.141`
- **Проект Selectel:** `f66190758e644187b7eb92f2918d3f4a` (Unilist)
- **Server ID (Nova):** `8cb4639c-1cda-4e34-af1e-ed8f549d9eec`
- **Root credentials:** root / 9d54179Wih2g
- **Путь установки:** `/opt/posthog/`

## Docker Compose

Используется официальный `docker-compose.hobby.yml` от PostHog.

```bash
cd /opt/posthog
docker compose -f docker-compose.hobby.yml up -d
```

Для перезапуска только proxy:
```bash
docker compose -f docker-compose.hobby.yml up -d --force-recreate proxy
```

## Файл /opt/posthog/.env

```env
DOMAIN=posthog.unilist.ru
POSTHOG_APP_TAG=latest
POSTHOG_SECRET=c8cc6ba14eddad717cf54fda49c92ddd9d17fd5041b550b0803447c67da7da93
ENCRYPTION_SALT_KEYS=a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2
TLS_BLOCK=
REGISTRY_URL=posthog/posthog
CADDY_HOST=posthog.unilist.ru, http://, https://
```

### Важно: CADDY_HOST

Переменная `CADDY_HOST` используется в `docker-compose.base.yml`:
```yaml
CADDYFILE: "${CADDY_HOST:-http://localhost:8000} { ... }"
```

Это **подстановка на этапе парсинга docker-compose** из `.env` файла, а НЕ из environment контейнера. Поэтому значение должно быть в `.env`, а не в `docker-compose.hobby.yml`.

## Caddy (reverse proxy)

Caddy встроен в PostHog hobby deployment. Слушает порты 80 и 443. SSL-сертификат получает автоматически через Let's Encrypt.

Логи: `docker logs posthog-proxy-1 --tail 50`

## DNS

A-запись в reg.ru: `posthog.unilist.ru → 37.9.7.141`

## Проблемы при установке

### fail2ban блокирует SSH

IP `62.4.45.151` (рабочий) попал под бан fail2ban из-за многократных попыток подключения. Разбанить:
```bash
fail2ban-client set sshd unbanip 62.4.45.151
fail2ban-client set recidive unbanip 62.4.45.151
```
Или зайти с другого IP (мобильный интернет).

### Let's Encrypt NXDOMAIN при первом старте

Caddy пытается получить сертификат до того, как DNS распространился. Caddy ретраит каждые 60 сек — просто подождать после добавления A-записи.

### Проверка состояния контейнеров

```bash
docker ps -a | grep posthog
docker logs posthog-proxy-1 --tail 20
docker logs posthog-web-1 --tail 20
docker logs posthog-worker-1 --tail 20
curl -sI http://localhost:8000/
```
