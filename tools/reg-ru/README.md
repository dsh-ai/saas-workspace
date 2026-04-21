# Reg.ru API tools

Управление доменами и DNS в Reg.ru через API v2.

## Установка

```bash
pip install requests
cp ../../.secrets/regru.env.example ../../.secrets/regru.env
# заполнить REGRU_USERNAME, REGRU_PASSWORD
```

Добавить текущий IP в whitelist: ЛК Reg.ru → Настройки → API → `/user/account/#/settings/api/`.

## Проверка связи

```bash
python client.py           # domain/nop ping
```

## Команды

```bash
# инвентаризация → saas-workspace/dev/domains.md
python inventory.py

# что истекает в ближайшие 30 дней (exit 1 если <7 дней)
python monitor.py --days 30

# DNS
python dns.py list example.ru
python dns.py add-a example.ru www 1.2.3.4
python dns.py add-txt example.ru @ "v=spf1 include:_spf.google.com ~all"
python dns.py add-mx example.ru @ 10 aspmx.l.google.com
python dns.py remove example.ru www A --content 1.2.3.4

# email-готовность домена (Respondo): MX+SPF+DMARC+DKIM одной командой
python dns.py apply-email example.ru \
  --mx-host aspmx.l.google.com --mx-prio 10 \
  --dkim-selector respondo \
  --dkim-key "v=DKIM1; k=rsa; p=MIGfMA0G..."

# VK WorkSpace (двухшаговая настройка)
python setup-vk.py verify example.ru "mailruverify-XXXX"
python setup-vk.py mail example.ru \
  --mx emx.mail.ru:10 \
  --spf "v=spf1 redirect=_spf.vkteam.ru" \
  --dkim-value "v=DKIM1; k=rsa; p=..."
```

## Файлы

- `client.py` — обёртка API (auth через `.secrets/regru.env`)
- `inventory.py` — список доменов → markdown
- `monitor.py` — мониторинг истечения
- `dns.py` — CLI для DNS-записей

## Безопасность

- `.secrets/` в `.gitignore`
- Только username+password (для MVP); миграция на `sig` — в будущем, если потребуется prod-код
