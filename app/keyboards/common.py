from aiogram.utils.keyboard import InlineKeyboardBuilder

def back_kb(target: str = "menu"):
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Назад", callback_data=target)
    return kb.as_markup()
