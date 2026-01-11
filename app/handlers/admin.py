from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from app.keyboards.admin import admin_menu
from app.keyboards.common import back_kb
from app.config import ADMIN_IDS

router = Router()

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

@router.callback_query(F.data == "admin")
async def admin_panel(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    await call.message.edit_text(
        "🛠 Админка",
        reply_markup=admin_menu()
    )

@router.message(F.text.startswith("/approve"))
async def approve_withdraw(message: Message, db):
    if not is_admin(message.from_user.id):
        return

    req_id = int(message.text.split()[1])
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT tg_id,amount FROM withdraws "
            "WHERE id=$1 AND status='pending'",
            req_id
        )
        if not row:
            await message.answer("Заявка не найдена")
            return

        await conn.execute(
            "UPDATE withdraws SET status='approved' WHERE id=$1",
            req_id
        )

    await message.bot.send_message(
        row["tg_id"],
        f"✅ Вывод {row['amount']} ⭐ одобрен"
    )
    await message.answer("Готово")

@router.message(F.text.startswith("/deny"))
async def deny_withdraw(message: Message, db):
    if not is_admin(message.from_user.id):
        return

    req_id = int(message.text.split()[1])
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT tg_id,amount FROM withdraws "
            "WHERE id=$1 AND status='pending'",
            req_id
        )
        if not row:
            await message.answer("Заявка не найдена")
            return

        await conn.execute(
            "UPDATE withdraws SET status='denied' WHERE id=$1",
            req_id
        )
        await conn.execute(
            "UPDATE users SET balance=balance+$1 WHERE tg_id=$2",
            row["amount"], row["tg_id"]
        )

    await message.bot.send_message(
        row["tg_id"],
        f"❌ Вывод {row['amount']} ⭐ отклонён, средства возвращены"
    )
    await message.answer("Отклонено")
