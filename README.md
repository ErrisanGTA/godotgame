# Telegram Bot (aiogram 3)

Бот с меню: задания, профиль, магазин и реферальная система.

## Стек
- Python 3.11+
- aiogram 3
- SQLite (через `aiosqlite`)

## Установка
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Заполните `.env`:
- `BOT_TOKEN` — токен бота
- `CHANNEL_USERNAME` — канал для обязательной подписки (`@channel_name`)
- `BOT_USERNAME` — username бота без `@` (можно оставить пустым, тогда берется из Telegram API)
- `DB_PATH` — путь к SQLite БД

## Запуск
```bash
python bot.py
```

## Архитектура
- `bot.py` — точка входа, инициализация `Dispatcher`, БД и polling.
- `app/config.py` — загрузка переменных окружения.
- `app/db.py` — работа с БД:
  - таблица `users`
  - таблица `completed_tasks`
- `app/data.py` — данные заданий, товаров и бонусы.
- `app/keyboards.py` — Inline клавиатуры для экранов.
- `app/handlers/common.py` — все обработчики:
  - `/start` + deep link `/start REFERRER_ID`
  - проверка подписки
  - меню разделов
  - логика заданий/проверок/наград
  - профиль
  - магазин и покупки
  - реферальная система

## Что реализовано
- Проверка подписки при `/start` и кнопке `Проверить подписку`
- Создание пользователя в БД
- Реферальная система с deep link и начислением бонуса
- Раздел заданий с защитой от повторного выполнения
- Профиль со статистикой
- Магазин со списанием баланса
- Навигация с кнопками `Назад`
