from __future__ import annotations

from datetime import datetime
from typing import Any

import aiosqlite


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init(self) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    balance INTEGER NOT NULL DEFAULT 0,
                    referrals_count INTEGER NOT NULL DEFAULT 0,
                    tasks_completed INTEGER NOT NULL DEFAULT 0,
                    referrer_id INTEGER,
                    registration_date TEXT NOT NULL
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS completed_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL,
                    task_id INTEGER NOT NULL,
                    completed_at TEXT NOT NULL,
                    UNIQUE(telegram_id, task_id)
                )
                """
            )
            await db.commit()

    async def get_user(self, telegram_id: int) -> dict[str, Any] | None:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def create_user(self, telegram_id: int, referrer_id: int | None = None) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO users (telegram_id, referrer_id, registration_date)
                VALUES (?, ?, ?)
                """,
                (telegram_id, referrer_id, datetime.utcnow().isoformat()),
            )
            await db.commit()

    async def set_referrer(self, telegram_id: int, referrer_id: int) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET referrer_id = ? WHERE telegram_id = ?",
                (referrer_id, telegram_id),
            )
            await db.commit()

    async def apply_referral_bonus(self, referrer_id: int, amount: int) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                UPDATE users
                SET referrals_count = referrals_count + 1,
                    balance = balance + ?
                WHERE telegram_id = ?
                """,
                (amount, referrer_id),
            )
            await db.commit()

    async def has_completed_task(self, telegram_id: int, task_id: int) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT 1 FROM completed_tasks WHERE telegram_id = ? AND task_id = ?",
                (telegram_id, task_id),
            )
            return await cursor.fetchone() is not None

    async def complete_task(self, telegram_id: int, task_id: int, reward: int) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("BEGIN")
            await db.execute(
                """
                INSERT INTO completed_tasks (telegram_id, task_id, completed_at)
                VALUES (?, ?, ?)
                """,
                (telegram_id, task_id, datetime.utcnow().isoformat()),
            )
            await db.execute(
                """
                UPDATE users
                SET tasks_completed = tasks_completed + 1,
                    balance = balance + ?
                WHERE telegram_id = ?
                """,
                (reward, telegram_id),
            )
            await db.commit()

    async def spend_balance(self, telegram_id: int, amount: int) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT balance FROM users WHERE telegram_id = ?", (telegram_id,)
            )
            row = await cursor.fetchone()
            if row is None or row[0] < amount:
                return False
            await db.execute(
                "UPDATE users SET balance = balance - ? WHERE telegram_id = ?",
                (amount, telegram_id),
            )
            await db.commit()
            return True
