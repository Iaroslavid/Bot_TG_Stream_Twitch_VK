import os
import time
import threading
import requests
from dotenv import load_dotenv
from obswebsocket import obsws, events

# === Загружаем переменные из .env ===
load_dotenv()

# === Telegram ===
# В .env нужно указать:
# TELEGRAM_BOT_TOKEN=твой_токен_бота
# TELEGRAM_CHAT_ID=айди_твоей_группы_или_чата
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# === Twitch ===
# В .env нужно указать:
# TWITCH_USER=твой_ник_на_twitch
# TWITCH_CLIENT_ID=твой_client_id
# TWITCH_ACCESS_TOKEN=твой_access_token
TWITCH_USER = os.getenv("TWITCH_USER")
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_ACCESS_TOKEN = os.getenv("TWITCH_ACCESS_TOKEN")

# === OBS / VK Play ===
# В .env нужно указать:
# OBS_HOST=localhost
# OBS_PORT=4455
# OBS_PASSWORD=пароль_websocket_из_OBS
# VKPLAY_USER=твой_ник_на_vkplay
OBS_HOST = os.getenv("OBS_HOST", "localhost")
OBS_PORT = int(os.getenv("OBS_PORT", "4455"))
OBS_PASSWORD = os.getenv("OBS_PASSWORD", "")
VKPLAY_USER = os.getenv("VKPLAY_USER", "your_vkplay_username")  # ← сюда вставь свой ник

# === Общие настройки ===
# В .env можно указать CHECK_INTERVAL_SECONDS=30
INTERVAL = int(os.getenv("CHECK_INTERVAL_SECONDS", "30"))

# === Telegram: функция отправки сообщений ===
def tg_send_html(text: str):
    """Отправка HTML-сообщений в Telegram"""
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": False,  # предпросмотр включен
            },
            timeout=10,
        )
        if r.status_code != 200:
            print(f"[TG] Ошибка {r.status_code}: {r.text}")
    except Exception as e:
        print("Ошибка Telegram:", e)

# === Twitch ===
def twitch_info(user_login: str):
    """Проверяет, идёт ли стрим на Twitch"""
    url = f"https://api.twitch.tv/helix/streams?user_login={user_login}"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {TWITCH_ACCESS_TOKEN}",
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return None
        data = r.json().get("data", [])
        if not data:
            return None
        stream = data[0]
        title = stream.get("title", "Без названия")
        game = stream.get("game_name", "Не указана")
        return {"title": title, "game": game, "url": f"https://twitch.tv/{user_login}"}
    except Exception as e:
        print("Ошибка Twitch:", e)
        return None

def twitch_checker():
    """Проверяет Twitch каждые N секунд и отправляет уведомление"""
    print(f"✅ Проверяю Twitch каждые {INTERVAL} секунд.")
    was_live = False
    while True:
        twitch_data = twitch_info(TWITCH_USER)
        live = twitch_data is not None
        if live and not was_live:
            twitch_msg = f"""
🟣 <b>Трансляция началась на Twitch!</b>  
🎥 <b>{twitch_data['title']}</b>  
👤 Стример: {TWITCH_USER}

🔴 Присоединяйся к стриму прямо сейчас!  
👉 <a href="{twitch_data['url']}">Смотреть на Twitch</a>
"""
            tg_send_html(twitch_msg.strip())
        was_live = live
        time.sleep(INTERVAL)

# === VK Play / OBS ===
vk_was_live = False

def notify_vkplay_online():
    """Отправка уведомления о начале стрима VK Play"""
    global vk_was_live
    if vk_was_live:
        return
    vk_was_live = True

    vk_url = f"https://vkplay.live/{VKPLAY_USER}"
    vk_msg = f"""
💙 <b>Прямая трансляция на VK Play!</b>  
📺 Стример: {VKPLAY_USER}

🔥 Присоединяйся и смотри прямо здесь 👇  
<a href="{vk_url}">Смотреть на VK Play</a>
"""
    tg_send_html(vk_msg.strip())

def notify_vkplay_offline():
    """Отправка уведомления о завершении стрима"""
    global vk_was_live
    if not vk_was_live:
        return
    vk_was_live = False

    msg = """
🔴 <b>Стрим завершён</b>  
🕹️ Спасибо, что были с нами 💫  
💬 Поддержи стримера и не пропусти следующий эфир!  
📅 Следи за обновлениями — скоро снова в эфире 💥
"""
    tg_send_html(msg.strip())

def on_any_event(message):
    """Обрабатывает события OBS о трансляции"""
    try:
        data = message.__dict__
        if data.get("name") != "StreamStateChanged":
            return

        payload = data.get("datain", {})
        state = payload.get("outputState")
        active = payload.get("outputActive")

        if active and state == "OBS_WEBSOCKET_OUTPUT_STARTED":
            notify_vkplay_online()
        elif not active and state == "OBS_WEBSOCKET_OUTPUT_STOPPED":
            notify_vkplay_offline()
    except Exception as e:
        print("Ошибка OBS:", e)

def connect_obs():
    """Подключается к OBS WebSocket и слушает события"""
    while True:
        try:
            print(f"🔌 Подключаюсь к OBS WebSocket ({OBS_HOST}:{OBS_PORT})...")
            ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
            ws.connect()
            print("✅ Подключено к OBS WebSocket.")

            ws.register(on_any_event)
            ws.register(on_any_event, events.StreamStarted)
            ws.register(on_any_event, events.StreamStopped)

            while True:
                time.sleep(1)
        except Exception as e:
            print("❌ Ошибка OBS:", e)
            print("🔁 Повторное подключение через 5 сек...")
            time.sleep(5)

# === Запуск ===
if __name__ == "__main__":
    print("🚀 Бот запущен: Twitch + VK Play интеграция")
    threading.Thread(target=twitch_checker, daemon=True).start()
    connect_obs()
