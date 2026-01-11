from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.keyboards.main import main_menu
from app.config import ADMIN_IDS

router = Router()

@router.callback_query(F.data == "menu")
async def menu_handler(call: CallbackQuery):
    await call.message.edit_text(
        "🏠 Главное меню",
        reply_markup=main_menu(call.from_user.id in ADMIN_IDS)
    )
