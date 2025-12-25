import telebot
from telebot import types

# ВСТАВЬ СЮДА ТОКЕН ОТ BotFather
TOKEN = "8500994183:AAF6VjQKSqaZY74OkaFHYdTNHYGLg9nFKRw"
bot = telebot.TeleBot(TOKEN)

GIFT_CODE = "#Code5516#116"
activated_users = {}

@bot.message_handler(commands=['start'])
def start(message):
    text = "🎉 С Новым годом! Вот твой подарок 🎁"

    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Получить подарок", callback_data="get_gift")
    markup.add(btn)

    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id

    if call.data == "get_gift":
        if chat_id in activated_users:
            bot.send_message(chat_id, "⚠️ Вы уже получили подарок")
        else:
            bot.send_message(chat_id, "Введите код:")
            bot.register_next_step_handler_by_chat_id(chat_id, check_code)

def check_code(message):
    chat_id = message.chat.id

    if message.text.strip() == GIFT_CODE:
        bot.send_message(chat_id, "✅ Код верный!\nНапишите свой юзернейм:")
        bot.register_next_step_handler_by_chat_id(chat_id, save_username)
    else:
        bot.send_message(chat_id, "❌ Код неверный. Попробуйте ещё раз:")
        bot.register_next_step_handler_by_chat_id(chat_id, check_code)

def save_username(message):
    chat_id = message.chat.id
    username = message.text.strip()

    activated_users[chat_id] = username
    bot.send_message(
        chat_id,
        f"🎉 Спасибо! Юзернейм @{username} принят.\nВы получили 100 ⭐ Telegram!"
    )

bot.infinity_polling()
