@echo off
chcp 65001 >nul
title Skarf Corporation Installer

:: Установка консольного шрифта Consolas (чтобы рамки были ровными)
reg add "HKCU\Console" /v FaceName /t REG_SZ /d "Consolas" /f >nul

echo [Skarf] Проверка Python...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python не найден! Скачай с python.org и поставь галочку "Add to PATH".
    pause & exit /b 1
)

echo [Skarf] Установка библиотек...
python -m pip install --quiet requests beautifulsoup4 colorama dnspython

echo [Skarf] Запуск...
python skarf.py
pause