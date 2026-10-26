# -*- coding: utf-8 -*-
# Skarf Corporation // OSINT Edition v12.0 (Stable)
import os, sys, subprocess, importlib.util, platform, time, random, socket, re, hashlib, base64, threading, csv, json, sqlite3, zipfile
from pathlib import Path
import datetime
import urllib.parse

# --- АВТОУСТАНОВКА ЗАВИСИМОСТЕЙ ---
# sherlock-lib убран!
REQUIRED = {
    "requests": "requests", 
    "bs4": "beautifulsoup4", 
    "colorama": "colorama", 
    "dns": "dnspython", 
    "rarfile": "rarfile"
}

def ensure_deps():
    missing = [pkg for mod, pkg in REQUIRED.items() if importlib.util.find_spec(mod) is None]
    if not missing: return
    print(f"[Skarf] Ставлю зависимости: {', '.join(missing)}")
    for flags in ([], ["--break-system-packages"]):
        r = subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", *flags, *missing], capture_output=True)
        if r.returncode == 0: return
    print("[Skarf] Не удалось установить. Запусти вручную: pip install " + " ".join(missing))
    sys.exit(1)

ensure_deps()

import requests
from bs4 import BeautifulSoup
from colorama import Fore, Style, init as cinit
import dns.resolver
import rarfile
cinit(autoreset=True)

# --- УТИЛИТЫ ---
R, G, Y, C, M, W = Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.CYAN, Fore.MAGENTA, Fore.WHITE
BOLD, DIM, RESET = Style.BRIGHT, Style.DIM, Style.RESET_ALL

def clear():
    os.system("cls" if platform.system() == "Windows" else "clear")

def pause():
    input(f"\n{DIM}Enter — назад...{RESET}")

class Spinner:
    def __init__(self, msg="Загрузка"):
        self.msg = msg
        self.frames = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        self.running = False
        self.thread = None
    def _spin(self):
        i = 0
        while self.running:
            sys.stdout.write(f"\r  {C}{self.frames[i % len(self.frames)]}{RESET} {self.msg}   ")
            sys.stdout.flush()
            time.sleep(0.08)
            i += 1
    def __enter__(self):
        self.running = True
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()
        return self
    def __exit__(self, *args):
        self.running = False
        if self.thread: self.thread.join()
        sys.stdout.write("\r" + " " * (len(self.msg) + 8) + "\r")

def save_report(filename, content):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c for c in filename if c.isalnum() or c in "._- ")
    fname = f"report_{safe_name}_{ts}.txt"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(f"=== SKARF CORPORATION REPORT ===\n")
        f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Target: {filename}\n")
        f.write("="*40 + "\n\n")
        f.write(content)
    print(f"\n{G}[+] Отчет сохранен: {fname}{RESET}")

# ==========================================
# ВИЗУАЛИЗАЦИЯ
# ==========================================
BANNER = r"""
  ███████╗██╗  ██╗ █████╗ ██████╗ ███████╗
  ██╔════╝██║ ██╔╝██╔══██╗██╔══██╗██╔════╝
  ███████╗█████╔╝ ███████║██████╔╝█████╗  
  ╚════██║██╔═██╗ ██╔══██║██╔══██╗██╔══╝  
  ███████║██║  ██╗██║  ██║██║  ██║██║     
  ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     
"""

def show_panel():
    clear()
    user = os.getlogin() if hasattr(os, 'getlogin') else "User"
    os_name = platform.system()
    
    info = [
        f"{R}┌──────────────────────────┐{RESET}",
        f"{R}│{RESET} {C}System:{RESET} {os_name:<16} {R}│{RESET}",
        f"{R}│{RESET} {C}User:{RESET}   {user:<16} {R}│{RESET}",
        f"{R}│{RESET} {C}Status:{RESET} {G}Online{RESET}           {R}│{RESET}",
        f"{R}└──────────────────────────┘{RESET}"
    ]

    b_lines = BANNER.strip('\n').split('\n')
    print("\n")
    for i in range(len(b_lines)):
        print(f"                    {R}{BOLD}{b_lines[i]}{RESET}  {info[i] if i < len(info) else ''}")
    
    print(f"\n{DIM}                    By @slitev{RESET}\n")

def draw_menu():
    def make_box(items):
        lines = [f"{R}+---------------------+{RESET}"]
        for key, label in items:
            line = f"| {Y}[{key:>2}]{RESET} {label:<15} {R}|{RESET}"
            lines.append(line)
        lines.append(f"{R}+---------------------+{RESET}")
        return lines

    c1 = make_box([
        ("1", "TG OSINT"),
        ("2", "VK OSINT"),
        ("3", "Username Check"),
        ("4", "Local DB"),
        ("5", "Phone Info")
    ])
    
    c2 = make_box([
        ("6", "IP / Geo"),
        ("7", "DNS Lookup"),
        ("8", "Port Scan"),
        ("9", "Email Leaks"),
        ("10", "Pass Gen")
    ])

    c3 = make_box([
        ("11", "Hash / B64"),
        ("12", "Web Search"),
        ("13", "URL Shorten"),
        ("14", "Sys Info"),
        ("0", "Exit")
    ])

    for i in range(len(c1)):
        print(f"  {c1[i]}  {c2[i]}  {c3[i]}")
    print()

# ==========================================
# ЛОГИКА (15 ФУНКЦИЙ)
# ==========================================
DB_DIR = Path("db")
TEMP_DIR = Path("db_temp")

def ensure_dirs():
    if not DB_DIR.exists(): DB_DIR.mkdir()
    if not TEMP_DIR.exists(): TEMP_DIR.mkdir()

# 1. TG OSINT
def f_telegram_osint():
    show_panel()
    print(f"  {C}{BOLD}[1] Telegram OSINT{RESET}\n")
    username = input(f"{Y}  Введите юзернейм (без @): {RESET}").strip().replace("@", "")
    if not username: return pause()

    tg_url = f"https://t.me/{username}"
    with Spinner(f"Сканирую {tg_url}..."):
        try:
            r = requests.get(tg_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            if r.status_code != 200:
                print(f"  {R}[-] Аккаунт @{username} не найден.{RESET}"); return pause()
            
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.find("meta", property="og:title")
            desc = soup.find("meta", property="og:description")
            image = soup.find("meta", property="og:image")
            
            name = title["content"] if title else "Нет данных"
            bio = desc["content"] if desc else "Нет данных"
            
            print(f"  {G}[+] ПРОФИЛЬ НАЙДЕН:{RESET}")
            print(f"    {C}Имя:{RESET} {name}")
            print(f"    {C}Био:{RESET} {bio}")
            print(f"    {C}Ссылка:{RESET} {tg_url}")
            
            res = f"Name: {name}\nBio: {bio}\nURL: {tg_url}\n"
            if image and "content" in image.attrs and "telegram.org" not in image["content"]:
                try:
                    img_data = requests.get(image["content"], timeout=10).content
                    img_name = f"avatar_{username}.jpg"
                    with open(img_name, "wb") as f: f.write(img_data)
                    print(f"    {C}Аватарка:{RESET} {G}Скачана ({img_name}){RESET}")
                except: pass
            save_report(f"tg_{username}", res)
        except Exception as e: print(f"  {R}[!] Ошибка: {e}{RESET}")
    pause()

# 2. VK OSINT
def f_vk_osint():
    show_panel()
    print(f"  {C}{BOLD}[2] VK OSINT{RESET}\n")
    query = input(f"{Y}  Введите ник или ФИО: {RESET}").strip()
    if not query: return pause()

    if " " in query:
        print(f"\n  {C}[*] Поиск по ФИО через DuckDuckGo...{RESET}")
        with Spinner("Ищу профили ВК..."):
            try:
                q = f'site:vk.com "{query}"'
                r = requests.post("https://html.duckduckgo.com/html/", data={"q": q}, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                soup = BeautifulSoup(r.text, "html.parser")
                links = soup.select(".result__a")[:5]
                if not links: print(f"  {R}[-] Ничего не найдено.{RESET}")
                else:
                    print(f"  {G}[+] Найдено {len(links)} профилей:{RESET}\n")
                    for i, a in enumerate(links, 1):
                        print(f"    {G}{i}.{RESET} {a.get_text(strip=True)}")
                        print(f"       {DIM}{a.get('href','')}{RESET}")
            except Exception as e: print(f"  {R}[!] Ошибка: {e}{RESET}")
    else:
        vk_id = query.replace("@", "")
        with Spinner(f"Запрос к vk.com/{vk_id}..."):
            try:
                r = requests.get(f"https://vk.com/{vk_id}", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                if r.status_code != 200: print(f"  {R}[-] Профиль не найден.{RESET}")
                else:
                    soup = BeautifulSoup(r.text, "html.parser")
                    title = soup.find("title")
                    print(f"  {G}[+] Найдено:{RESET} {title.text.strip() if title else 'Скрыт'}")
                    print(f"    {C}Ссылка:{RESET} https://vk.com/{vk_id}")
            except Exception as e: print(f"  {R}[!] Ошибка: {e}{RESET}")
    pause()

# 3. USERNAME CHECK (Замена Шерлока)
def f_username_check():
    show_panel()
    print(f"  {C}{BOLD}[3] Username Check (OSINT){RESET}\n")
    un = input(f"{Y}  Введите ник: {RESET}").strip().replace("@", "")
    if not un: return pause()

    sites = {
        "GitHub": f"https://github.com/{un}",
        "Telegram": f"https://t.me/{un}",
        "VK": f"https://vk.com/{un}",
        "Instagram": f"https://instagram.com/{un}",
        "TikTok": f"https://tiktok.com/@{un}",
        "Steam": f"https://steamcommunity.com/id/{un}",
        "Twitch": f"https://twitch.tv/{un}",
        "Reddit": f"https://reddit.com/user/{un}",
        "Pinterest": f"https://pinterest.com/{un}",
        "YouTube": f"https://youtube.com/@{un}",
        "Twitter": f"https://twitter.com/{un}",
        "Tumblr": f"https://{un}.tumblr.com",
        "Flickr": f"https://flickr.com/people/{un}",
        "SoundCloud": f"https://soundcloud.com/{un}",
        "Roblox": f"https://roblox.com/user.aspx?username={un}"
    }

    print()
    found = {}
    for site, url in sites.items():
        print(f"  {C}[*] Проверяю {site:<12}{RESET}", end="", flush=True)
        try:
            # Делаем быстрый HEAD запрос, чтобы не качать страницы целиком
            r = requests.head(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True)
            
            # Некоторые сайты (ТикТок, Инста) отдают 200 даже если нет юзера, но проверка работает для большинства
            if r.status_code == 200:
                print(f" {G}[+] НАЙДЕН{RESET}")
                found[site] = url
            else:
                print(f" {DIM}[-] Нет{RESET}")
        except:
            print(f" {R}[!] Ошибка сети{RESET}")

    if found:
        print(f"\n  {G}[+] Итог: аккаунт найден на {len(found)} площадках.{RESET}")
        res_text = f"Username: {un}\n\n"
        for s, u in found.items():
            res_text += f"{s}: {u}\n"
        save_report(f"usercheck_{un}", res_text)
    else:
        print(f"\n  {R}[-] Ничего не найдено.{RESET}")
    
    pause()

# 4. Local DB
def f_local_db_search():
    show_panel()
    print(f"  {C}{BOLD}[4] Поиск по локальным БД{RESET}\n")
    ensure_dirs()
    if not list(DB_DIR.glob("*")):
        print(f"  {R}[!] В папке db/ нет файлов.{RESET}"); return pause()

    query = input(f"{Y}  Введите запрос: {RESET}").strip()
    if not query: return pause()
    
    with Spinner("Сканирую базы..."):
        files = list(DB_DIR.rglob("*.txt")) + list(DB_DIR.rglob("*.csv")) + list(DB_DIR.rglob("*.db"))
        results = []
        for fp in files:
            try:
                if fp.suffix == ".db":
                    conn = sqlite3.connect(fp); cur = conn.cursor()
                    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    for t in [x[0] for x in cur.fetchall()]:
                        cur.execute(f"SELECT * FROM {t}")
                        cols = [d[0] for d in cur.description]
                        for row in cur.fetchall():
                            if query.lower() in str(row).lower():
                                results.append(f"[{fp.name}:{t}] {dict(zip(cols, row))}")
                    conn.close()
                else:
                    with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if query.lower() in line.lower():
                                results.append(f"[{fp.name}] {line.strip()}")
            except: pass
            
    if results:
        print(f"  {G}[+] Найдено: {len(results)}{RESET}")
        for r in results[:10]: print(f"    {r}")
        save_report(f"db_{query}", "\n".join(results))
    else:
        print(f"  {R}[-] Ничего не найдено.{RESET}")
    pause()

# 5. Phone Info
def f_phone_info():
    show_panel()
    print(f"  {C}{BOLD}[5] Информация по телефону{RESET}\n")
    ph = input(f"{Y}  Введите номер: {RESET}").strip()
    if not ph: return pause()
    
    digits = re.sub(r"\D", "", ph)
    print(f"\n  {C}Очищенный номер:{RESET} +{digits}")
    print(f"  {G}Возможные ссылки в мессенджерах:{RESET}")
    print(f"    • WhatsApp: https://wa.me/{digits}")
    print(f"    • Telegram: https://t.me/+{digits}")
    
    print(f"\n  {C}[*] Поиск страницы ВК по номеру...{RESET}")
    with Spinner("Сканирую DuckDuckGo..."):
        try:
            q = f'site:vk.com "{digits}" OR "{ph}"'
            r = requests.post("https://html.duckduckgo.com/html/", data={"q": q}, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, "html.parser")
            links = soup.select(".result__a")[:5]
            if not links: print(f"  {DIM}[-] ВК не найден.{RESET}")
            else:
                print(f"  {G}[+] Найдено {len(links)} профилей:{RESET}\n")
                for i, a in enumerate(links, 1):
                    print(f"    {G}{i}.{RESET} {a.get_text(strip=True)}")
                    print(f"       {DIM}{a.get('href','')}{RESET}")
        except: print(f"  {R}[!] Ошибка{RESET}")
    pause()

# 6. IP / Geo
def f_ip_info():
    show_panel()
    print(f"  {C}{BOLD}[6] IP / Геолокация{RESET}\n")
    with Spinner("Запрашиваю ip-api..."):
        try: r = requests.get("http://ip-api.com/json/", timeout=10).json()
        except: print(f"{R}  Ошибка сети{RESET}"); return pause()
    if r.get("status") == "fail": print(f"{R}  Ошибка: {r.get('message')}{RESET}"); return pause()
    for k, v in r.items(): print(f"  {G}{k:<12}{RESET} {v}")
    pause()

# 7. DNS Lookup
def f_dns_lookup():
    show_panel()
    print(f"  {C}{BOLD}[7] DNS Lookup{RESET}\n")
    dom = input(f"{Y}  Домен: {RESET}").strip()
    if not dom: return pause()
    for rtype in ("A", "MX", "NS", "TXT"):
        try:
            ans = dns.resolver.resolve(dom, rtype, lifetime=5)
            print(f"  {C}{rtype}:{RESET}")
            for a in ans: print(f"    {G}•{RESET} {a}")
        except: print(f"  {DIM}{rtype}: нет записи{RESET}")
    pause()

# 8. Port Scan
def f_port_scan():
    show_panel()
    print(f"  {C}{BOLD}[8] Port Scan{RESET}\n")
    host = input(f"{Y}  Хост/IP: {RESET}").strip()
    if not host: return pause()
    ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 8080]
    print(f"\n  {DIM}Сканирую {host}...{RESET}\n")
    for p in ports:
        s = socket.socket(); s.settimeout(0.5)
        try:
            s.connect((host, p))
            print(f"  {G}OPEN{RESET}  {p:<6} {socket.getservbyport(p)}")
        except: pass
        finally: s.close()
    pause()

# 9. Email Leaks
def f_email_leaks():
    show_panel()
    print(f"  {C}{BOLD}[9] Email Leaks{RESET}\n")
    em = input(f"{Y}  Email: {RESET}").strip()
    if not em: return pause()
    with Spinner("Проверяю базы..."):
        try:
            r = requests.get(f"https://api.xposedornot.com/v1/check-email/{em}", timeout=10)
            data = r.json()
            if data and "breaches" in data and data["breaches"]:
                breaches = data["breaches"][0]
                print(f"  {R}[!] Найден в утечках:{RESET}")
                for b in breaches: print(f"    {Y}•{RESET} {b}")
            else:
                print(f"  {G}[+] Утечек не найдено.{RESET}")
        except: print(f"{R}Ошибка API{RESET}")
    pause()

# 10. Pass Gen
def f_password_gen():
    show_panel()
    print(f"  {C}{BOLD}[10] Генератор пароля{RESET}\n")
    n = input(f"{Y}  Длина (20): {RESET}").strip() or "20"
    try: n = int(n)
    except: n = 20
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    print(f"\n  {G}{''.join(random.choices(chars, k=n))}{RESET}")
    pause()

# 11. Hash / B64
def f_hash_b64():
    show_panel()
    print(f"  {C}{BOLD}[11] Hash / Base64{RESET}\n")
    s = input(f"{Y}  Строка: {RESET}").encode()
    if not s: return pause()
    print(f"\n  {C}MD5:{RESET} {hashlib.md5(s).hexdigest()}")
    print(f"  {C}SHA256:{RESET} {hashlib.sha256(s).hexdigest()}")
    print(f"  {C}B64:{RESET} {base64.b64encode(s).decode()}")
    pause()

# 12. Web Search
def f_web_search():
    show_panel()
    print(f"  {C}{BOLD}[12] Веб-поиск{RESET}\n")
    q = input(f"{Y}  Запрос: {RESET}").strip()
    if not q: return pause()
    with Spinner("Ищу..."):
        try:
            r = requests.post("https://html.duckduckgo.com/html/", data={"q": q}, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, "html.parser")
            links = soup.select(".result__a")[:10]
            if not links: print(f"  {R}Ничего не найдено.{RESET}")
            else:
                for i, a in enumerate(links, 1): print(f"  {G}{i:>2}.{RESET} {a.get_text(strip=True)}")
        except: print(f"{R}Ошибка{RESET}")
    pause()

# 13. URL Shorten
def f_url_shorten():
    show_panel()
    print(f"  {C}{BOLD}[13] URL Shortener{RESET}\n")
    url = input(f"{Y}  Введите ссылку: {RESET}").strip()
    if not url: return pause()
    with Spinner("Сокращаю..."):
        try:
            r = requests.get(f"http://tinyurl.com/api-create.php?url={url}", timeout=10)
            if r.status_code == 200: print(f"\n  {G}[+] Короткая ссылка:{RESET} {r.text}")
            else: print(f"{R}Ошибка{RESET}")
        except: print(f"{R}Ошибка{RESET}")
    pause()

# 14. Sys Info
def f_sys_info():
    show_panel()
    print(f"  {C}{BOLD}[14] Система{RESET}\n")
    print(f"  {C}OS:{RESET} {platform.system()} {platform.release()}")
    print(f"  {C}Python:{RESET} {platform.python_version()}")
    print(f"  {C}Host:{RESET} {socket.gethostname()}")
    pause()

# ==========================================
# МЕНЮ
# ==========================================
MENU = {
    "1": f_telegram_osint, "2": f_vk_osint, "3": f_username_check,
    "4": f_local_db_search, "5": f_phone_info, "6": f_ip_info,
    "7": f_dns_lookup, "8": f_port_scan, "9": f_email_leaks,
    "10": f_password_gen, "11": f_hash_b64, "12": f_web_search,
    "13": f_url_shorten, "14": f_sys_info, "0": None
}

def menu():
    ensure_dirs()
    while True:
        show_panel()
        draw_menu()
        
        choice = input(f"  {R}Skarf{R} > {RESET}").strip()
        if choice in MENU:
            fn = MENU[choice]
            if fn is None: 
                print(f"  {DIM}Выход.{RESET}")
                return
            fn()
        else:
            print(f"  {R}Неверный выбор{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    try: menu()
    except KeyboardInterrupt: print(f"\n{DIM}Прервано.{RESET}")