#!/usr/bin/env python3
# -pk



import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime
import threading
import logging
import json
import sqlite3
from urllib.parse import urljoin
import argparse
from random import choice
from flask import Flask, render_template_string, jsonify
import smtplib
from email.mime.text import MIMEText
from telegram import Bot
from telegram.error import TelegramError
import tweepy
import asyncio

# ========================= CONFIG & LOGGINGS =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("keycode_bot.log"),
        logging.StreamHandler()
    ]
)

# Key patterns
PATTERNS = {
    "Steam": re.compile(r"[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}"),
    "Xbox": re.compile(r"[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}"),
    "PlayStation": re.compile(r"[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}"),
}

# Load config
DEFAULT_CONFIG = {
    "seed_websites": [
        "https://www.reddit.com/r/FreeGameFindings/new/",
        "https://gg.deals/giveaways/",
        "https://www.indiegala.com/freebie"
    ],
    "aggregator_urls": ["https://www.giveawaylisting.com/"],
    "x_keywords": ["#SteamGiveaway", "#FreeSteamKey", "#XboxCode", "#PSNGiveaway", "steam key", "free key"],
    "base_scan_interval": 300,
    "x_api": {
        "bearer_token": "",
        "api_key": "", "api_secret": "", "access_token": "", "access_secret": ""
    },
    "proxies": [],
    "notifications": {
        "discord_webhook": "",
        "telegram": {"bot_token": "", "chat_id": ""},
        "email": {"smtp_server": "smtp.gmail.com", "port": 587, "sender": "", "password": "", "recipient": ""}
    }
}

try:
    with open("config.json", "r") as f:
        CONFIG = json.load(f)
except FileNotFoundError:
    CONFIG = DEFAULT_CONFIG
    with open("config.json", "w") as f:
        json.dump(CONFIG, f, indent=4)
    logging.warning("config.json created. Please fill in your credentials.")
    exit(1)

# ========================= DATABASE =========================
db_lock = threading.Lock()
conn = sqlite3.connect("keycodes.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS keys (
        key TEXT PRIMARY KEY,
        platform TEXT,
        source TEXT,
        found_at TIMESTAMP,
        status TEXT DEFAULT 'unclaimed'
    )
""")
conn.commit()

# ========================= X (Twitter) CLIENT =========================
x_client = None
if CONFIG["x_api"]["bearer_token"]:
    x_client = tweepy.Client(bearer_token=CONFIG["x_api"]["bearer_token"], wait_on_rate_limit=True)
elif all(CONFIG["x_api"][k] for k in ["api_key", "api_secret", "access_token", "access_secret"]):
    auth = tweepy.OAuth1UserHandler(
        CONFIG["x_api"]["api_key"],
        CONFIG["x_api"]["api_secret"],
        CONFIG["x_api"]["access_token"],
        CONFIG["x_api"]["access_secret"]
    )
    x_client = tweepy.Client(auth, wait_on_rate_limit=True)
else:
    logging.warning("No valid X/Twitter credentials found. X scanning disabled.")

# ========================= PROXY MANAGER =========================
class ProxyManager:
    def __init__(self, proxies):
        self.proxies = [p for p in proxies if p.strip()]
        self.lock = threading.Lock()

    def get(self):
        with self.lock:
            if not self.proxies:
                return None
            return {"http": choice(self.proxies), "https": choice(self.proxies)}

proxy_manager = ProxyManager(CONFIG["proxies"])

# ========================= NOTIFIER =========================
class Notifier:
    def __init__(self, cfg):
        self.discord = cfg["discord_webhook"].strip()
        self.tg_bot = Bot(token=cfg["telegram"]["bot_token"].strip()) if cfg["telegram"]["bot_token"].strip() else None
        self.tg_chat = cfg["telegram"]["chat_id"]
        self.email_cfg = cfg["email"]

    def send(self, message: str):
        tasks = []

        if self.discord:
            tasks.append(requests.post(self.discord, json={"content": message}, timeout=10))

        if self.tg_bot and self.tg_chat:
            tasks.append(
                asyncio.create_task(self.tg_bot.send_message(chat_id=self.tg_chat, text=message, disable_web_page_preview=True))
            )

        if self.email_cfg["sender"] and self.email_cfg["password"]:
            msg = MIMEText(message)
            msg["Subject"] = "New Game Key Found!"
            msg["From"] = self.email_cfg["sender"]
            msg["To"] = self.email_cfg["recipient"] or self.email_cfg["sender"]
            try:
                with smtplib.SMTP(self.email_cfg["smtp_server"], self.email_cfg["port"], timeout=10) as s:
                    s.starttls()
                    s.login(self.email_cfg["sender"], self.email_cfg["password"])
                    s.send_message(msg)
            except Exception as e:
                logging.error(f"Email failed: {e}")

        if tasks:
            threading.Thread(target=lambda: [t() if hasattr(t, '__call__') else asyncio.run(t) for t in tasks], daemon=True).start()

notifier = Notifier(CONFIG["notifications"])

# ========================= BOT CORE =========================
class KeycodeBot:
    def __init__(self):
        self.websites = CONFIG["seed_websites"][:]
        self.scan_interval = CONFIG["base_scan_interval"]
        self.running = False

    def discover_sites(self):
        new_sites = set(self.websites)
        headers = {"User-Agent": "Mozilla/5.0 (compatible; KeycodeBot/1.0)"}
        for agg in CONFIG["aggregator_urls"]:
            try:
                r = requests.get(agg, headers=headers, proxies=proxy_manager.get(), timeout=15)
                soup = BeautifulSoup(r.text, "html.parser")
                for a in soup.find_all("a", href=True):
                    url = urljoin(agg, a["href"])
                    if any(k in url.lower() for k in ["giveaway", "free", "key", "code"]):
                        new_sites.add(url)
            except Exception as e:
                logging.error(f"Discovery failed for {agg}: {e}")
        self.websites = list(new_sites)[:50]  # limit explosion

    def extract_keys(self, text: str, source: str) -> dict:
        found = {"Steam": [], "Xbox": [], "PlayStation": []}
        timestamp = datetime.utcnow()

        for platform, pattern in PATTERNS.items():
            for key in pattern.findall(text):
                key = key.strip()
                if platform == "Steam" and len(key) != 17: continue
                if platform == "Xbox" and len(key) != 29: continue
                if platform == "PlayStation" and len(key) != 12: continue

                with db_lock:
                    try:
                        cursor.execute(
                            "INSERT INTO keys (key, platform, source, found_at) VALUES (?, ?, ?, ?)",
                            (key, platform, source, timestamp)
                        )
                        conn.commit()
                        found[platform].append(key)
                        logging.info(f"NEW KEY → {platform}: {key} [{source}]")
                    except sqlite3.IntegrityError:
                        pass  # already in DB
        return {k: v for k, v in found.items() if v}

    def scan_page(self, url: str) -> dict:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            r = requests.get(url, headers=headers, proxies=proxy_manager.get(), timeout=15)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            text = soup.get_text(separator=" ") + " " + " ".join(a.get("href", "") for a in soup.find_all("a"))
            return self.extract_keys(text, url)
        except Exception as e:
            logging.debug(f"Failed scanning {url}: {e}")
            return {}

    def scan_x(self) -> dict:
        if not x_client:
            return {}
        query = " OR ".join(CONFIG["x_keywords"]) + " -is:retweet lang:en"
        try:
            tweets = x_client.search_recent_tweets(query=query, max_results=100, tweet_fields=["text"])
            if not tweets.data:
                return {}
            text = " ".join(t.text for t in tweets.data)
            return self.extract_keys(text, "X/Twitter")
        except Exception as e:
            logging.error(f"X scan error: {e}")
            return {}

    def scan_cycle(self):
        logging.info("Starting scan cycle...")
        self.discover_sites()
        results = {}

        # Web pages
        threads = []
        for url in self.websites:
            t = threading.Thread(target=lambda u: results.update({u: self.scan_page(u)}), args=(url,), daemon=True)
            t.start()
            threads.append(t)

        # X in parallel
        x_thread = threading.Thread(target=lambda: results.update({"X": self.scan_x()}), daemon=True)
        x_thread.start()
        threads.append(x_thread)

        for t in threads:
            t.join(timeout=60)

        # Notify
        total_new = sum(len(v) for r in results.values() for v in r.values())
        if total_new > 0:
            message = f"Found {total_new} new key(s)!\n\n"
            for src, keys in results.items():
                if not keys: continue
                message += f"**{src}**\n"
                for plat, kl in keys.items():
                    message += f"• {plat}: {', '.join(kl)}\n"
                message += "\n"
            notifier.send(message.strip())
            logging.info(f"Scan complete — {total_new} new keys notified.")
        else:
            logging.info("Scan complete — no new keys.")

        # Adaptive interval
        self.scan_interval = max(60, min(1800, self.scan_interval * (0.95 if total_new == 0 else 0.8)))

    def run_forever(self):
        self.running = True
        while self.running:
            try:
                self.scan_cycle()
                logging.info(f"Next scan in {self.scan_interval // 60} minutes.")
                time.sleep(self.scan_interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                logging.exception(f"Unexpected error: {e}")
                time.sleep(60)

# ========================= FLASK DASHBOARD =========================
app = Flask(__name__)
bot = KeycodeBot()

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Keycode Bot</title>
    <meta http-equiv="refresh" content="30">
    <style>body{font-family: sans-serif; margin: 2em;} table{border-collapse: collapse;} td, th{padding: 8px; border: 1px solid #ccc;}</style>
</head>
<body>
    <h1>Keycode Bot Dashboard</h1>
    <p><strong>Status:</strong> <span style="color: {{ 'green' if running else 'red' }}">{{ 'Running' if running else 'Stopped' }}</span></p>
    <p><strong>Interval:</strong> {{ interval }} seconds</p>
    <p><button onclick="fetch('/start', {method:'POST'}).then(()=>location.reload())">Start</button>
       <button onclick="fetch('/stop', {method:'POST'}).then(()=>location.reload())">Stop</button></p>

    <h2>Unclaimed Keys (Total: {{ total }})</h2>
    <table>
        <tr><th>Platform</th><th>Count</th></tr>
        {% for plat, cnt in stats.items() %}
        <tr><td>{{ plat }}</td><td>{{ cnt }}</td></tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route("/")
def index():
    with db_lock:
        cursor.execute("SELECT platform, COUNT(*) FROM keys WHERE status='unclaimed' GROUP BY platform")
        stats = dict(cursor.fetchall() or [])
        total = sum(stats.values())
    return render_template_string(DASHBOARD_HTML, running=bot.running, interval=bot.scan_interval, stats=stats, total=total)

@app.route("/start", methods=["POST"])
def start():
    if not bot.running:
        bot.running = True
        threading.Thread(target=bot.run_forever, daemon=True).start()
    return jsonify({"status": "running"})

@app.route("/stop", methods=["POST"])
def stop():
    bot.running = False
    return jsonify({"status": "stopped"})

# ========================= MAIN =========================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Game Keycode Scanner Bot")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode (no web dashboard)")
    args = parser.parse_args()

    if args.cli:
        bot.run_forever()
    else:
        print("Dashboard: http://127.0.0.1:5000")
        app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
