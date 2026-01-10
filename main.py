import random
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "8500994183:AAFDTPI7vaxMT1KS_33dJb1INn7_JIQHU8g"
ADMIN_ID = 548858090
CHANNEL_USERNAME = "@Sband_Gift_Giveaway"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

used_spins = set()
winners = []

def spin_slots():
    symbols = ["🍒", "🍋", "🍉", "⭐", "7️⃣"]
    return [random.choice(symbols) for _ in range(3)]

async def check_sub(user_id):
    member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
    return member.status in ["member", "administrator", "creator"]

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🎰 Крутить", callback_data="spin")
    )
    await msg.answer(
        "🎰 Слот-розыгрыш\n\n"
        "🎯 Выигрыш ТОЛЬКО если выпадет 7️⃣7️⃣7️⃣\n"
        "💵 Приз: 0.33$\n"
        "👤 1 аккаунт = 1 прокрут\n\n"
        f"📢 Подпишись на канал: {CHANNEL_USERNAME}",
        reply_markup=kb
    )

@dp.callback_query_handler(text="spin")
async def spin(call: types.CallbackQuery):
    user_id = call.from_user.id

    if user_id in used_spins:
        await call.answer("❌ Ты уже крутил", show_alert=True)
        return

    if not await check_sub(user_id):
        await call.answer("❗ Подпишись на канал", show_alert=True)
        return

    used_spins.add(user_id)
    result = spin_slots()

    text = f"🎰 Результат:\n{' '.join(result)}\n\n"

    if result == ["7️⃣", "7️⃣", "7️⃣"] and len(winners) < 3:
        winners.append(user_id)
        text += "🎉 ПОЗДРАВЛЯЮ!\nТы выиграл 0.33$"

        await bot.send_message(
            ADMIN_ID,
            f"✅ ВЫИГРЫШ\n"
            f"👤 @{call.from_user.username}\n"
            f"ID: {user_id}\n"
            f"🎰 7️⃣7️⃣7️⃣"
        )
    else:
        text += "❌ Не выбил 777"

        await bot.send_message(
            ADMIN_ID,
            f"❌ ПРОИГРЫШ\n"
            f"👤 @{call.from_user.username}\n"
            f"ID: {user_id}\n"
            f"🎰 {' '.join(result)}"
        )

    await call.message.answer(text)
    await call.answer()

executor.start_polling(dp)
