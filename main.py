usernamemememeйм telebot
from telebot import types

TOKEN = "8500994183:AAF6VjQKSqaZY74OkaFHYdTNHYGLg9nFKRw"
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 548858090
GIFT_CODE = "#Code5516#116"

activated_users = {}
banned_users = {}

def safe_send(chat_id, text, markup=None):
    try:
        bot.send_message(chat_id, text, reply_markup=markup)
    except:
        pass  # пользователь заблокировал бота

# ===== START =====
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id

    if chat_id in banned_users:
        safe_send(chat_id, f"🚫 Вы заблокированы.\nПричина: {banned_users[chat_id]}")
        return

    text = "🎉 С Новым годом! Вот твой подарок 🎁"

    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Получить подарок", callback_data="get_gift")
    markup.add(btn)

    safe_send(chat_id, text, markup)

# ===== КНОПКА =====
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id

    if chat_id in banned_users:
        safe_send(chat_id, f"🚫 Вы заблокированы.\nПричина: {banned_users[chat_id]}")
        return

    if call.data == "get_gift":
        if chat_id in activated_users:
            safe_send(chat_id, "⚠️ Вы уже получили подарок")
        else:
            safe_send(chat_id, "Введите код:")
            bot.register_next_step_handler_by_chat_id(chat_id, check_code)

# ===== ПРОВЕРКА КОДА =====
def check_code(message):
    chat_id = message.chat.id

    if chat_id in banned_users:
        return

    if message.text.strip() == GIFT_CODE:
        safe_send(chat_id, "✅ Код верный!\nНапишите свой юзернейм без @:")
        bot.register_next_step_handler_by_chat_id(chat_id, save_username)
    else:
        safe_send(chat_id, "❌ Код неверный. Попробуйте ещё раз:")
        bot.register_next_step_handler_by_chat_id(chat_id, check_code)

# ===== ЮЗЕРНЕЙМ =====
def save_username(message):
    chat_id = message.chat.id
    username = message.text.replace("@", "").strip()

    activated_users[chat_id] = username

    safe_send(
        chat_id,
        f"🎉 Спасибо! Юзернейм @{username} принят.\nВы получили 50 ⭐ Telegram! До 12:00 30 декабря 2025 года.В    )

# ===== БАН =====
@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.from_user.id != ADMIN_ID:
        safe_send(message.chat.id, "❌ У вас нет прав")
        return

    parts = message.text.split(maxsplit=2)

    if len(parts) < 3:
        safe_send(message.chat.id, "❗ Использование:\n/ban USER_ID причина")
        return

    user_id = int(parts[1])
    reason = parts[2]

    banned_users[user_id] = reason

    safe_send(message.chat.id, f"✅ Пользователь {user_id} забанен\nПричина: {reason}")
    safe_send(user_id, f"🚫 Вы были заблокированы.\nПричина: {reason}")

# ===== ЗАПУСК =====
bot.infinity_polling(skip_pending=True)
