#!/usr/bin/env bash
# Установка AFK Inbox бота как отдельного systemd-сервиса.
# Использование на сервере:
#   chmod +x deploy/install.sh
#   ./deploy/install.sh /opt/bots/afk-inbox-bot
#
# Перед установкой:
#   1. Скопируйте проект в APP_DIR (git clone / scp)
#   2. Создайте .env в APP_DIR
#   3. python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
#   4. Остановите бота на локальном ПК (один токен = один процесс)

set -euo pipefail

APP_DIR="${1:-/opt/bots/afk-inbox-bot}"
DEPLOY_USER="${SUDO_USER:-$(whoami)}"
SERVICE_NAME="afk-inbox-bot"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
TEMPLATE="$(cd "$(dirname "$0")" && pwd)/systemd/${SERVICE_NAME}.service"

if [[ ! -d "$APP_DIR" ]]; then
  echo "Папка не найдена: $APP_DIR"
  exit 1
fi

if [[ ! -f "$APP_DIR/.env" ]]; then
  echo "Создайте $APP_DIR/.env (скопируйте из .env.example)"
  exit 1
fi

if [[ ! -x "$APP_DIR/.venv/bin/python" ]]; then
  echo "Создайте venv: cd $APP_DIR && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
  exit 1
fi

mkdir -p "$APP_DIR/data"

sed \
  -e "s|__APP_DIR__|${APP_DIR}|g" \
  -e "s|__DEPLOY_USER__|${DEPLOY_USER}|g" \
  "$TEMPLATE" | sudo tee "$SERVICE_FILE" > /dev/null

sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo ""
echo "Сервис установлен: $SERVICE_NAME"
echo "  Статус:  sudo systemctl status $SERVICE_NAME"
echo "  Логи:    journalctl -u $SERVICE_NAME -f"
echo "  Стоп:    sudo systemctl stop $SERVICE_NAME"
