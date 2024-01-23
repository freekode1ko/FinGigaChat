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

2. Установите и настройте `pre-commit`:

```bash
pip install pre-commit
pre-commit install -f
pre-commit install -f --hook-type pre-push
pre-commit install -f --hook-type commit-msg
```

pre-commit будет запускать линтеры и проверки при каждом вызове `git commit`  
Также pre-commit можно запустить просто командой `pre-commit run`  
Подробнее про утилиту [тут](https://pre-commit.com/)

