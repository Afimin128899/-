from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.keyboards.withdraw import withdraw_menu
from app.keyboards.common import back_kb
from app.config import ADMIN_IDS

router = Router()

@router.callback_query(F.data == "withdraw")
async def withdraw_menu_handler(call: CallbackQuery):
    await call.message.edit_text(
        "💸 Выбери сумму для вывода:",
        reply_markup=withdraw_menu()
    )

@router.callback_query(F.data.startswith("withdraw:"))
async def withdraw_request(call: CallbackQuery, db):
    amount = int(call.data.split(":")[1])

    async with db.acquire() as conn:
        balance = await conn.fetchval(
            "SELECT balance FROM users WHERE tg_id=$1",
            call.from_user.id
        )
        if balance < amount:
            await call.answer("Недостаточно ⭐", show_alert=True)
            return

        await conn.execute(
            "UPDATE users SET balance=balance-$1 WHERE tg_id=$2",
            amount, call.from_user.id
        )
        req = await conn.fetchrow(
            "INSERT INTO withdraws (tg_id,amount,status) "
            "VALUES ($1,$2,'pending') RETURNING id",
            call.from_user.id, amount
        )

    for admin in ADMIN_IDS:
        await call.bot.send_message(
            admin,
            f"💸 Заявка на вывод\nID заявки: {req['id']}\n"
            f"Пользователь: {call.from_user.id}\n"
            f"Сумма: {amount} ⭐\n\n"
            f"/approve {req['id']}\n/deny {req['id']}"
        )

    await call.message.edit_text(
        "✅ Заявка отправлена администратору",
        reply_markup=back_kb()
    )
