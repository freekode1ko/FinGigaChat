# Bot

## Для запуска бота необходимо: 
### 1. Переместить из корня проекта папки `data` и `sources` в `src/bot/`. Так же необходимо создать файл `.env` на основе `.env.example`
   ```commandline
   cp -r ./data/ ./src/bot/data/
   cp -r ./sources/ ./src/bot/source/
   cp ./.env.example ./src/bot/.env
   ```
### 2. Заполнить .env файл
   
   Не обязательные данные к заполнению при разработке
   ```dotenv
   SENTRY_CHAT_BOT_DSN=
   SENTRY_QUOTES_PARSER_DSN=
   SENTRY_RESEARCH_PARSER_DSN=
   SENTRY_POLYANALIST_PARSER_DSN=
   SENTRY_NEWS_PARSER_DSN=
   ```
   
   Необходимо проставить как тут
   ```dotenv
   SENTRY_FORCE_LOCAL=false
   ENV=local
   DEBUG=true
   ```
   
   Можно взять у [@BotFather](https://telegram.me/BotFather)
   ```dotenv
   BOT_API_TOKEN=  
   ```
   Ключ можно попросить у коллег
   ```dotenv
   GIGA_CREDENTIALS=
   ```
   Необходимо вписать данные от запущенного postgres
   ```dotenv
   DB_USER=
   DB_PASS=
   DB_HOST=
   DB_PORT=
   DB_NAME=
   ```
   
   Для разработки не обязательно к заполнению
   ```dotenv
   MONITORING_API_KEY=
   MONITORING_API_URL=
   ```

### 3. Установить `poetry`
   ```commandline
   python3 -m pip install poetry
   ```

### 4. Установить зависимости для проекта
   Перед этим необходимо перейти в папку `src/bot/`
   ```commandline
   poetry install 
   ```
### 5. Провести миграцию базы данных
   
   Для запуска миграций необходимо предварительно запустить postgres
   
   ```commandline
   poetry run alembic ubgrade head
   ```

### 6. Запустить проект
   Перед этим необходимо перейти в папку `src/bot/`
   ```commandline
   poetry run python main.py
   ```
