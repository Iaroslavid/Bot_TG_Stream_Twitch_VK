# Bot_TG_Stream_Twitch_VK
Это Telegram-бот, который автоматически уведомляет зрителей о начале и завершении твоих стримов на Twitch и VK Play. Он присылает сообщения с названием трансляции, ссылками и предпросмотром видео в Telegram-чате. Поддерживает автоматический запуск при включении ПК, работает с OBS, полностью автономен и не требует серверов.
## Установка

### 1. Клонирование проекта

``` bash
git clone https://github.com/<твой_ник>/StreamTwitch.git
cd StreamTwitch
```

### 2. Установка зависимостей

``` bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

------------------------------------------------------------------------

## Настройка .env

Открой файл `.env` и введи недостающие значения :

``` env
TELEGRAM_BOT_TOKEN=твой_токен_бота
TELEGRAM_CHAT_ID=...

TWITCH_USER=...
TWITCH_CLIENT_ID=...
TWITCH_ACCESS_TOKEN=...

OBS_HOST=localhost(пример)
OBS_PORT=4455(пример)
OBS_PASSWORD=...
VKPLAY_USER=...

CHECK_INTERVAL_SECONDS=30(проверяет твич каждые 30 секунд, можно уменьшить/увеличить)
```

------------------------------------------------------------------------

## Получение токенов

### Telegram

1.  Создай бота через [@BotFather](https://t.me/BotFather)
2.  Получи токен (`TELEGRAM_BOT_TOKEN`)
3.  Добавь бота в группу и узнай `chat_id` через
    [@RawDataBot](https://t.me/RawDataBot)

### Twitch

1.  [Создай приложение](https://dev.twitch.tv/console/apps)

2.  Скопируй `Client ID` и `Client Secret`

3.  Получи токен:

    ``` bash
    curl -X POST "https://id.twitch.tv/oauth2/token" ^
    -d "client_id=ВАШ_CLIENT_ID" ^
    -d "client_secret=ВАШ_CLIENT_SECRET" ^
    -d "grant_type=client_credentials"
    ```

### 🔹 OBS WebSocket (для VK Play)

1.  В OBS включи сервер WebSocket:

    -   Порт: `4455`
    -   Пароль: `.......`

2.  Проверь порт:

    ``` bash
    netstat -ano | find "4455"
    ```

### VK Play

Ссылка для уведомления:

    https://....../<твой_ник>

------------------------------------------------------------------------

## Первый запуск

``` bash
.venv\Scripts\activate
python app.py
```

Если видишь:

    🚀 Бот запущен: Twitch + VK Play
    ✅ Проверяю Twitch каждые 30 секунд.
    🔌 Подключаюсь к OBS WebSocket (localhost:4455)...
    ✅ Подключено к OBS WebSocket.

--- бот работает 🎉

------------------------------------------------------------------------

## Автозапуск при включении ПК

1.  Помести файл `start_bot.vbs` в папку автозагрузки:

        Win + R → shell:startup

2.  После перезагрузки бот запустится в фоне.

------------------------------------------------------------------------

## Структура проекта

    StreamTwitchBot/
    ├── app.py
    ├── requirements.txt
    ├── .env.example
    ├── start_bot.bat
    ├── start_bot.vbs
    └── README.md

------------------------------------------------------------------------

##  Автор

Разработано Ярославом Васканом 
