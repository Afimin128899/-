from aiogram.utils.keyboard import InlineKeyboardBuilder

WITHDRAW_AMOUNTS = [15, 25, 50, 100]

def withdraw_menu():
    kb = InlineKeyboardBuilder()

    for amount in WITHDRAW_AMOUNTS:
        kb.button(
            text=f"💸 {amount} ⭐",
            callback_data=f"withdraw:select:{amount}"
        )

    kb.button(text="⬅️ Назад", callback_data="menu")
    kb.adjust(2)
    return kb.as_markup()

def withdraw_confirm(amount: int):
    kb = InlineKeyboardBuilder()
    kb.button(
        text=f"💸 Вывести {amount} ⭐",
        callback_data=f"withdraw:confirm:{amount}"
    )
    kb.button(text="⬅️ Назад", callback_data="withdraw")
    kb.adjust(1)
    return kb.as_markup()
