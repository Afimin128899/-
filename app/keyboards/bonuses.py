from aiogram.utils.keyboard import InlineKeyboardBuilder

def bonuses_menu():
    kb = InlineKeyboardBuilder()

    kb.button(text="🎁 Ежедневный бонус", callback_data="bonus:daily")
    kb.button(text="🔥 Серия дней", callback_data="bonus:streak")

    kb.button(text="⬅️ Назад", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()
