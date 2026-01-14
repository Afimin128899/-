from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.keyboards.common import back_kb

router = Router()

@router.callback_query(F.data == "referrals")
async def referrals_handler(call: CallbackQuery, db):
    async with db.acquire() as conn:
        refs = await conn.fetch(
            "SELECT tg_id FROM users WHERE referrer_id=$1",
            call.from_user.id
        )

    text = "👥 <b>Рефералы</b>\n\n"
    if not refs:
        text += "У тебя пока нет рефералов."
    else:
        for r in refs:
            text += f"• <code>{r['tg_id']}</code>\n"

    await call.message.edit_text(text, reply_markup=back_kb())
