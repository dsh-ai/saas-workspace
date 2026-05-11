#!/usr/bin/env bash
set -euo pipefail

VPS="${VPS:-root@193.168.136.29}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_ed25519}"
SSH="ssh -i $SSH_KEY $VPS"
SCP="scp -i $SSH_KEY"
RSYNC_SSH="ssh -i $SSH_KEY"

LOCAL_BOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOCAL_SECRETS="$LOCAL_BOT_DIR/../../.secrets/telegram-bot.env"

if [[ ! -f "$LOCAL_SECRETS" ]]; then
    echo "Missing $LOCAL_SECRETS — aborting." >&2
    exit 1
fi

echo "==> [1/6] Preparing user + dirs on VPS"
$SSH bash -s <<'EOF'
set -euo pipefail
id -u unilist &>/dev/null || useradd -m -s /bin/bash unilist
mkdir -p /opt/unilist-bot/{app,posts/drafts,posts/scheduled,posts/published}
chown -R unilist:unilist /opt/unilist-bot
# Ensure python3.11 is available (Ubuntu 22.04 ships 3.10 by default).
if ! command -v python3.11 >/dev/null 2>&1; then
    apt-get update -qq
    apt-get install -y -qq software-properties-common
    add-apt-repository -y ppa:deadsnakes/ppa
    apt-get update -qq
    apt-get install -y -qq python3.11 python3.11-venv python3.11-dev
fi
# Selectel RU egress filters most Telegram API CIDR ranges. Pin the one IP that responds.
# If this IP stops responding, find a new one via: for ip in $(dig +short api.telegram.org); do timeout 3 bash -c "</dev/tcp/$ip/443" && echo "OK $ip"; done
grep -q "api.telegram.org" /etc/hosts || echo "149.154.167.220 api.telegram.org" >> /etc/hosts
EOF

echo "==> [2/6] Syncing code"
rsync -avz --delete --no-owner --no-group \
    --exclude='.venv/' --exclude='__pycache__/' --exclude='*.egg-info/' \
    --exclude='.pytest_cache/' --exclude='.local/' --exclude='tests/' \
    --exclude='deploy/' \
    -e "$RSYNC_SSH" \
    "$LOCAL_BOT_DIR/" "$VPS:/opt/unilist-bot/app/"

echo "==> [3/6] Pushing prod env"
# Rewrite POSTS_ROOT and STATE_DB to VPS paths.
TMP_ENV=$(mktemp)
trap "rm -f $TMP_ENV" EXIT
sed -e 's|^POSTS_ROOT=.*|POSTS_ROOT=/opt/unilist-bot/posts|' \
    -e 's|^STATE_DB=.*|STATE_DB=/opt/unilist-bot/state.db|' \
    "$LOCAL_SECRETS" > "$TMP_ENV"
$SCP "$TMP_ENV" "$VPS:/opt/unilist-bot/.env"
$SSH "chown unilist:unilist /opt/unilist-bot/.env && chmod 600 /opt/unilist-bot/.env"

echo "==> [4/6] Setting up venv on VPS"
$SSH bash -s <<'EOF'
set -euo pipefail
chown -R unilist:unilist /opt/unilist-bot
cd /opt/unilist-bot/app
if [[ ! -d .venv ]]; then
    sudo -u unilist python3.11 -m venv .venv
fi
sudo -u unilist .venv/bin/pip install --quiet --upgrade pip
sudo -u unilist .venv/bin/pip install --quiet -e .
EOF

echo "==> [5/6] Installing systemd unit"
$SCP "$LOCAL_BOT_DIR/deploy/telegram-bot.service" "$VPS:/etc/systemd/system/telegram-bot.service"
$SSH "systemctl daemon-reload && systemctl enable telegram-bot && systemctl restart telegram-bot"

echo "==> [6/6] Health check (8s wait, then status + last log lines)"
sleep 8
$SSH "systemctl is-active telegram-bot && journalctl -u telegram-bot -n 30 --no-pager"

echo "==> Done. Tail logs: $SSH 'journalctl -u telegram-bot -f'"
