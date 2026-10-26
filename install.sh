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
    echo -e "\e[1;36m[1/3] Обновление Termux и установка Python...\e[0m"
    pkg update -y && pkg upgrade -y
    pkg install -y python git
else
    echo -e "\e[1;36m[1/3] Установка Python (Linux)...\e[0m"
    sudo apt update && sudo apt install -y python3 python3-pip git || true
fi

echo -e "\e[1;36m[2/3] Установка библиотек Python...\e[0m"
# В Termux иногда нужен флаг --break-system-packages
pip install --upgrade pip
pip install requests beautifulsoup4 colorama dnspython rarfile || pip install --break-system-packages requests beautifulsoup4 colorama dnspython rarfile

echo -e "\e[1;36m[3/3] Запуск Skarf Corporation...\e[0m"
cd "$(dirname "$0")"
python skarf.py