from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from app.config import Settings
from app.data import PRODUCTS, REFERRAL_BONUS, TASKS
from app.db import Database
from app.keyboards import (
    main_menu_keyboard,
    profile_keyboard,
    referral_keyboard,
    shop_keyboard,
    shop_product_keyboard,
    subscribe_keyboard,
    task_action_keyboard,
    tasks_keyboard,
)

router = Router()


def _extract_referrer(start_arg: str | None) -> int | None:
    if not start_arg:
        return None
    try:
        return int(start_arg.strip())
    except ValueError:
        return None


async def is_subscribed(message_or_callback: Message | CallbackQuery, settings: Settings) -> bool:
    user_id = message_or_callback.from_user.id
    bot = message_or_callback.bot
    member = await bot.get_chat_member(settings.channel_username, user_id)
    return member.status in {"member", "administrator", "creator"}


async def show_main_menu(target: Message | CallbackQuery) -> None:
    text = "Главное меню. Выберите раздел:"
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text, reply_markup=main_menu_keyboard())
        await target.answer()
    else:
        await target.answer(text, reply_markup=main_menu_keyboard())


@router.message(CommandStart(deep_link=True))
@router.message(CommandStart())
async def start_handler(message: Message, db: Database, settings: Settings) -> None:
    command = message.text or "/start"
    parts = command.split(maxsplit=1)
    start_arg = parts[1] if len(parts) > 1 else None

    user = await db.get_user(message.from_user.id)
    referrer_id = _extract_referrer(start_arg)

    if not user:
        valid_referrer = referrer_id and referrer_id != message.from_user.id
        await db.create_user(
            telegram_id=message.from_user.id,
            referrer_id=referrer_id if valid_referrer else None,
        )
        if valid_referrer:
            referrer = await db.get_user(referrer_id)
            if referrer:
                await db.apply_referral_bonus(referrer_id, REFERRAL_BONUS)
    elif referrer_id and user.get("referrer_id") is None and referrer_id != message.from_user.id:
        referrer = await db.get_user(referrer_id)
        if referrer:
            await db.set_referrer(message.from_user.id, referrer_id)
            await db.apply_referral_bonus(referrer_id, REFERRAL_BONUS)

    if not await is_subscribed(message, settings):
        await message.answer(
            "Чтобы пользоваться ботом подпишитесь на канал.",
            reply_markup=subscribe_keyboard(settings.channel_username),
        )
        return

    await show_main_menu(message)


@router.callback_query(F.data == "check_subscription")
async def check_subscription_handler(
    callback: CallbackQuery, settings: Settings
) -> None:
    if not await is_subscribed(callback, settings):
        await callback.answer("Вы всё ещё не подписаны на канал.", show_alert=True)
        return
    await show_main_menu(callback)


@router.callback_query(F.data == "back_main")
async def back_main_handler(callback: CallbackQuery) -> None:
    await show_main_menu(callback)


@router.callback_query(F.data == "menu_referrals")
async def referral_menu_handler(
    callback: CallbackQuery, db: Database, settings: Settings
) -> None:
    user = await db.get_user(callback.from_user.id)
    bot_username = settings.bot_username or (await callback.bot.get_me()).username
    link = f"https://t.me/{bot_username}?start={callback.from_user.id}"

    text = (
        "Приглашайте друзей и получайте награды.\n\n"
        f"Ваша реферальная ссылка:\n{link}\n\n"
        f"Приглашено: {user['referrals_count']}\n"
        f"Бонус за приглашение: {REFERRAL_BONUS}"
    )
    await callback.message.edit_text(text, reply_markup=referral_keyboard())
    await callback.answer()


@router.callback_query(F.data == "menu_tasks")
async def tasks_menu_handler(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "Выполните задания и получите награды.",
        reply_markup=tasks_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("task:"))
async def task_details_handler(callback: CallbackQuery, db: Database) -> None:
    task_id = int(callback.data.split(":", maxsplit=1)[1])
    task = TASKS.get(task_id)
    if not task:
        await callback.answer("Задание не найдено", show_alert=True)
        return

    done = await db.has_completed_task(callback.from_user.id, task_id)
    status = "✅ Уже выполнено" if done else "⌛ Не выполнено"
    text = (
        f"{task.title}\n\n"
        f"Описание: {task.description}\n"
        f"Награда: {task.reward}\n"
        f"Статус: {status}"
    )
    await callback.message.edit_text(text, reply_markup=task_action_keyboard(task_id))
    await callback.answer()


@router.callback_query(F.data.startswith("task_do:"))
async def task_do_handler(callback: CallbackQuery) -> None:
    task_id = int(callback.data.split(":", maxsplit=1)[1])
    task = TASKS.get(task_id)
    if not task:
        await callback.answer("Задание не найдено", show_alert=True)
        return
    await callback.answer(
        f"Выполните: {task.description} Потом нажмите 'Проверить'.",
        show_alert=True,
    )


@router.callback_query(F.data.startswith("task_check:"))
async def task_check_handler(
    callback: CallbackQuery, db: Database, settings: Settings
) -> None:
    task_id = int(callback.data.split(":", maxsplit=1)[1])
    task = TASKS.get(task_id)
    if not task:
        await callback.answer("Задание не найдено", show_alert=True)
        return

    if await db.has_completed_task(callback.from_user.id, task_id):
        await callback.answer("Это задание уже выполнено.", show_alert=True)
        return

    user = await db.get_user(callback.from_user.id)
    checks = {
        1: await is_subscribed(callback, settings),
        2: user["referrals_count"] >= 1,
        3: True,
    }
    if not checks.get(task_id, False):
        await callback.answer("Условия задания пока не выполнены.", show_alert=True)
        return

    await db.complete_task(callback.from_user.id, task_id, task.reward)
    await callback.message.edit_text(
        "Задание выполнено.\nВы получили награду.",
        reply_markup=tasks_keyboard(),
    )
    await callback.answer("Награда зачислена!")


@router.callback_query(F.data == "menu_profile")
async def profile_handler(callback: CallbackQuery, db: Database) -> None:
    user = await db.get_user(callback.from_user.id)
    text = (
        "Ваш профиль:\n\n"
        f"ID пользователя: {user['telegram_id']}\n"
        f"Баланс: {user['balance']}\n"
        f"Количество приглашённых пользователей: {user['referrals_count']}\n"
        f"Количество выполненных заданий: {user['tasks_completed']}"
    )
    await callback.message.edit_text(text, reply_markup=profile_keyboard())
    await callback.answer()


@router.callback_query(F.data == "menu_shop")
async def shop_menu_handler(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "Добро пожаловать в магазин.",
        reply_markup=shop_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("shop:"))
async def shop_item_handler(callback: CallbackQuery) -> None:
    product_id = callback.data.split(":", maxsplit=1)[1]
    product = PRODUCTS.get(product_id)
    if not product:
        await callback.answer("Товар не найден", show_alert=True)
        return

    text = (
        f"{product.title}\n\n"
        f"Описание: {product.description}\n"
        f"Цена: {product.price}"
    )
    await callback.message.edit_text(text, reply_markup=shop_product_keyboard(product_id))
    await callback.answer()


@router.callback_query(F.data.startswith("buy:"))
async def buy_handler(callback: CallbackQuery, db: Database) -> None:
    product_id = callback.data.split(":", maxsplit=1)[1]
    product = PRODUCTS.get(product_id)
    if not product:
        await callback.answer("Товар не найден", show_alert=True)
        return

    success = await db.spend_balance(callback.from_user.id, product.price)
    if not success:
        await callback.answer("Недостаточно средств для покупки.", show_alert=True)
        return

    await callback.answer("Покупка успешна!")
    await callback.message.edit_text(
        f"Вы купили: {product.title}\nСписано: {product.price}",
        reply_markup=shop_keyboard(),
    )
