from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.data import PRODUCTS, TASKS


def subscribe_keyboard(channel_username: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Подписаться",
                    url=f"https://t.me/{channel_username.lstrip('@')}",
                )
            ],
            [InlineKeyboardButton(text="Проверить подписку", callback_data="check_subscription")],
        ]
    )


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Задания", callback_data="menu_tasks")],
            [InlineKeyboardButton(text="👤 Профиль", callback_data="menu_profile")],
            [InlineKeyboardButton(text="🏪 Магазин", callback_data="menu_shop")],
            [
                InlineKeyboardButton(
                    text="👥 Реферальная система", callback_data="menu_referrals"
                )
            ],
        ]
    )


def referral_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Моя статистика", callback_data="menu_profile")],
            [InlineKeyboardButton(text="Назад", callback_data="back_main")],
        ]
    )


def tasks_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=task.title, callback_data=f"task:{task.task_id}")]
        for task in TASKS.values()
    ]
    rows.append([InlineKeyboardButton(text="Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def task_action_keyboard(task_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Выполнить", callback_data=f"task_do:{task_id}")],
            [InlineKeyboardButton(text="Проверить", callback_data=f"task_check:{task_id}")],
            [InlineKeyboardButton(text="Назад", callback_data="menu_tasks")],
        ]
    )


def profile_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Статистика", callback_data="menu_profile")],
            [InlineKeyboardButton(text="Назад", callback_data="back_main")],
        ]
    )


def shop_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=product.title, callback_data=f"shop:{product.product_id}")]
        for product in PRODUCTS.values()
    ]
    rows.append([InlineKeyboardButton(text="Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def shop_product_keyboard(product_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Купить", callback_data=f"buy:{product_id}")],
            [InlineKeyboardButton(text="Назад", callback_data="menu_shop")],
        ]
    )
