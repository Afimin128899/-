from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.keyboards.common import back_kb

router = Router()

@router.callback_query(F.data == "history")
async def history_handler(call: CallbackQuery, db):
    async with db.acquire() as conn:
        logs = await conn.fetch(
            """
            SELECT change, reason, created_at
            FROM balance_logs
            WHERE tg_id=$1
            ORDER BY created_at DESC
            LIMIT 10
            """,
            call.from_user.id
        )

    text = "📜 <b>История операций</b>\n\n"
    if not logs:
        text += "История пуста."
    else:
        for l in logs:
            sign = "+" if l["change"] > 0 else ""
            text += f"{sign}{l['change']} ⭐ — {l['reason']}\n"

    await call.message.edit_text(text, reply_markup=back_kb())
