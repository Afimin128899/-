from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from app.keyboards.common import back_kb
from app.services.promo import apply_promo_code

router = Router()

@router.callback_query(F.data == "promo")
async def promo_start(call: CallbackQuery):
    await call.message.edit_text(
        "🎟 Введи промокод сообщением",
        reply_markup=back_kb()
    )

@router.message()
async def promo_enter(message: Message, db):
    code = message.text.strip().upper()
    async with db.acquire() as conn:
        ok, msg = await apply_promo_code(conn, message.from_user.id, code)

    await message.answer(msg)
