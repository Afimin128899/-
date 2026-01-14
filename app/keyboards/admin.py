from aiogram.utils.keyboard import InlineKeyboardBuilder

def admin_menu():
    kb = InlineKeyboardBuilder()

    kb.button(text="📋 Заявки на вывод", callback_data="admin:withdraws")
    kb.button(text="🎟 Промокоды", callback_data="admin:promo")

    kb.button(text="📣 Рассылка", callback_data="admin:broadcast")
    kb.button(text="📊 Статистика", callback_data="admin:stats")

    kb.button(text="🚫 Бан / Разбан", callback_data="admin:ban")
    kb.button(text="⬅️ Назад", callback_data="menu")

    kb.adjust(2)
    return kb.as_markup()
