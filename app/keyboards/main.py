from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu(is_admin: bool = False):
    kb = InlineKeyboardBuilder()

    kb.button(text="👤 Профиль", callback_data="profile")
    kb.button(text="✅ Задания", callback_data="tasks")

    kb.button(text="👥 Рефералы", callback_data="referrals")
    kb.button(text="🎁 Бонусы", callback_data="bonuses")

    kb.button(text="🎟 Промокод", callback_data="promo")
    kb.button(text="💸 Вывод", callback_data="withdraw")

    kb.button(text="📜 История", callback_data="history")
    kb.button(text="🆘 Поддержка", callback_data="support")

    if is_admin:
        kb.button(text="🛠 Админка", callback_data="admin")

    kb.adjust(2)
    return kb.as_markup()
