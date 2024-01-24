## FinGigaChat (Финансовый помощник для ГКМ)

### Инструкция по локальному запуску проекта:

1. Обновите pip до актуальной версии.
    ```shell
    pip install -U pip
    ```

2. Установите необходимые пакеты:

    ```shell
    pip install -r requirements.txt
    ```
    
    Установите и настройте `pre-commit`:
    
    ```bash
    pip install pre-commit
    pre-commit install -f
    pre-commit install -f --hook-type pre-push
    pre-commit install -f --hook-type commit-msg
    ```
    
    pre-commit будет запускать линтеры и проверки при каждом вызове `git commit`  
    Также pre-commit можно запустить просто командой `pre-commit run`  
    Подробнее про утилиту [тут](https://pre-commit.com/)

3. Создайте файл `.env` в корне проекта и скопируйте содержимое из `.env.example`

### Инструкция по работе с Sentry:
1. Для просмотра Sentry запросите у команды учетку и перейдите [сюда](https://giga-ai.sentry.io/projects/)
2. Для записи в Sentry с локальной среды поставьте в .env `SENTRY_FORCE_LOCAL=true` **(Внимание!!! Это стоит делать только для дебага интеграции Sentry)**
3. Для дебага интеграции Sentry выполнить пункт 2 и попросить переменные `SENTRY_CHAT_BOT_DSN` и `SENTRY_PARSER_DSN` у коллег
