#!/bin/bash
set -e  # остановить при ошибке

# Определяем путь к скрипту
SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"

VENV_DIR="$SCRIPT_DIR/venv"

# Проверяем, есть ли виртуальное окружение
if [ ! -d "$VENV_DIR" ]; then
    echo "[INFO] Виртуальное окружение не найдено, создаю..."
    python3 -m venv "$VENV_DIR"
    echo "[INFO] Окружение создано в $VENV_DIR"
fi

# Активируем окружение
source "$VENV_DIR/bin/activate"

# Проверим наличие pip и обновим его
pip install --upgrade pip >/dev/null

# (опционально) установим зависимости, если есть requirements.txt
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo "[INFO] Устанавливаю зависимости из requirements.txt..."
    pip install -r "$SCRIPT_DIR/requirements.txt"
fi

cd "$SCRIPT_DIR/"

"$SCRIPT_DIR/venv/bin/python3" "$SCRIPT_DIR/v4.py"  





