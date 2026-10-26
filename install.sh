#!/data/data/com.termux/files/usr/bin/bash
# Skarf Corporation - Termux / Linux Installer
set -e

echo -e "\e[1;31m"
cat <<'EOF'
  ███████╗██╗  ██╗ █████╗ ██████╗ ███████╗
  ██╔════╝██║ ██╔╝██╔══██╗██╔══██╗██╔════╝
  ███████╗█████╔╝ ███████║██████╔╝█████╗  
  ╚════██║██╔═██╗ ██╔══██║██╔══██╗██╔══╝  
  ███████║██║  ██╗██║  ██║██║  ██║██║     
  ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     
EOF
echo -e "\e[0m"
echo -e "\e[1;32m[Skarf] Установка окружения...\e[0m"

# Проверка, запущено ли в Termux
if command -v pkg >/dev/null 2>&1; then
    echo -e "\e[1;36m[1/3] Обновление Termux и установка пакетов...\e[0m"
    pkg update -y && pkg upgrade -y
    # Устанавливаем Python и библиотеки через pkg (это надежнее pip в Termux)
    pkg install -y python git python-requests python-bs4 python-dnspython
else
    echo -e "\e[1;36m[1/3] Установка Python (Linux)...\e[0m"
    sudo apt update && sudo apt install -y python3 python3-pip python3-requests python3-bs4 python3-dnspython git || true
fi

# Устанавливаем только те пакеты, которых может не быть в pkg
pip install rarfile --break-system-packages || pip install rarfile || true
pip install colorama --break-system-packages || pip install colorama || true

echo -e "\e[1;36m[3/3] Запуск Skarf Corporation...\e[0m"
cd "$(dirname "$0")"
python skarf.py