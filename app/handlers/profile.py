from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.keyboards.common import back_kb

router = Router()

@router.callback_query(F.data == "profile")
async def profile_handler(call: CallbackQuery, db):
    async with db.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT balance FROM users WHERE tg_id=$1",
            call.from_user.id
        )
        refs = await conn.fetchval(
            "SELECT COUNT(*) FROM users WHERE referrer_id=$1",
            call.from_user.id
        )

    text = (
        "👤 <b>Профиль</b>\n\n"
        f"🆔 ID: <code>{call.from_user.id}</code>\n"
        f"⭐ Баланс: <b>{user['balance']}</b>\n"
        f"👥 Рефералов: <b>{refs}</b>\n\n"
        f"🔗 Реф. ссылка:\n"
        f"https://t.me/{(await call.bot.get_me()).username}?start={call.from_user.id}"
    )

    await call.message.edit_text(text, reply_markup=back_kb())
