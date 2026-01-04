import telebot
from telebot import types

# ===== НАСТРОЙКИ =====
TOKEN = "8500994183:AAF6VjQKSqaZY74OkaFHYdTNHYGLg9nFKRw"
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 548858090

# code: {"stars": int, "uses": int}
codes = {}
activated_users = {}
banned_users = {}

# ===== SAFE SEND =====
def safe_send(chat_id, text, markup=None):
    try:
        bot.send_message(chat_id, text, reply_markup=markup)
    except:
        pass

# ===== START =====
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id

    if chat_id in banned_users:
        safe_send(chat_id, f"🚫 Вы заблокированы\nПричина: {banned_users[chat_id]}")
        return

    text = (
        "🎁 **Хочешь получить подарок?**\n\n"
        "Ты можешь получить ⭐ **15 звёзд Telegram бесплатно** за простое задание.\n\n"
        "📌 **Что нужно сделать:**\n"
        "• Написать в ЛС 👉 @ShardenFoot\n"
        "• Получить задание\n"
        "• Выполнить его и получить код\n"
        "• Активировать код в этом боте\n\n"
        "⏳ Количество подарков ограничено!"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎉 Получить подарок", callback_data="get_gift"))

    safe_send(chat_id, text, markup)

# ===== BUTTON =====
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id

    if chat_id in banned_users:
        safe_send(chat_id, f"🚫 Вы заблокированы\nПричина: {banned_users[chat_id]}")
        return

    if call.data == "get_gift":
        if chat_id in activated_users:
            safe_send(chat_id, "⚠️ Вы уже получали подарок")
        else:
            safe_send(chat_id, "🔑 Введите код:")
            bot.register_next_step_handler_by_chat_id(chat_id, check_code)

# ===== CHECK CODE =====
def check_code(message):
    chat_id = message.chat.id
    code = message.text.strip()

    if code not in codes:
        safe_send(chat_id, "❌ Код неверный или не существует")
        return

    if codes[code]["uses"] <= 0:
        safe_send(chat_id, "❌ Лимит активаций этого кода исчерпан")
        return

    stars = codes[code]["stars"]
    codes[code]["uses"] -= 1
    activated_users[chat_id] = {"code": code, "stars": stars}

    safe_send(
        chat_id,
        f"✅ Код активирован!\n\n"
        f"⭐ Количество звёзд: {stars}\n"
        f"📍 Получение подарка: Telegram Gifts\n\n"
        f"✍️ Напишите свой юзернейм **без @**:"
    )

    bot.register_next_step_handler_by_chat_id(chat_id, save_username)

# ===== SAVE USERNAME =====
def save_username(message):
    chat_id = message.chat.id
    username = message.text.replace("@", "").strip()
    stars = activated_users[chat_id]["stars"]

    safe_send(
        chat_id,
        f"🎉 Спасибо!\n\n"
        f"👤 Юзернейм: {username}\n"
        f"⭐ Вы получите: {stars} ⭐ Telegram\n\n"
        f"⏳ Подарок будет начислен в ближайшее время."
    )

# ===== ADMIN PANEL =====
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return

    text = (
        "👑 **Админ-панель**\n\n"
        "/addcode КОД ЗВЁЗДЫ АКТИВАЦИИ\n"
        "/codes — список кодов\n"
        "/ban ID причина"
    )
    safe_send(message.chat.id, text)

# ===== ADD CODE =====
@bot.message_handler(commands=['addcode'])
def add_code(message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split()
    if len(parts) != 4:
        safe_send(message.chat.id, "❗ Использование:\n/addcode КОД ЗВЁЗДЫ АКТИВАЦИИ")
        return

    code = parts[1]
    stars = int(parts[2])
    uses = int(parts[3])

    codes[code] = {"stars": stars, "uses": uses}
    safe_send(message.chat.id, f"✅ Код добавлен\nКод: {code}\n⭐ {stars}\n🔁 {uses}")

# ===== LIST CODES =====
@bot.message_handler(commands=['codes'])
def list_codes(message):
    if message.from_user.id != ADMIN_ID:
        return

    if not codes:
        safe_send(message.chat.id, "Кодов нет")
        return

    text = "📦 **Коды:**\n\n"
    for c, d in codes.items():
        text += f"{c} → ⭐ {d['stars']} | 🔁 {d['uses']}\n"

    safe_send(message.chat.id, text)

# ===== BAN =====
@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        safe_send(message.chat.id, "/ban ID причина")
        return

    user_id = int(parts[1])
    reason = parts[2]
    banned_users[user_id] = reason

    safe_send(message.chat.id, f"🚫 Пользователь {user_id} забанен")
    safe_send(user_id, f"🚫 Вы заблокированы\nПричина: {reason}")

# ===== RUN =====
bot.infinity_polling(skip_pending=True)
