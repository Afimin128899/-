from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.keyboards.bonuses import bonuses_menu
from app.keyboards.common import back_kb
from app.services.bonuses import daily_bonus

router = Router()

@router.callback_query(F.data == "bonuses")
async def bonuses_menu_handler(call: CallbackQuery):
    await call.message.edit_text(
        "🎁 Бонусы",
        reply_markup=bonuses_menu()
    )

@router.callback_query(F.data == "bonus:daily")
async def daily_bonus_handler(call: CallbackQuery, db):
    async with db.acquire() as conn:
        ok = await daily_bonus(conn, call.from_user.id)

    if ok:
        await call.message.edit_text(
            "🎉 Ты получил ежедневный бонус +1 ⭐",
            reply_markup=back_kb()
        )
    else:
        await call.answer("Сегодня уже получал 🙂", show_alert=True)
