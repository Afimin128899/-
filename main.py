бота telebot
from telebot import types

# Токен вашего бота
TOKEN = '8500994183:AAF6VjQKSqaZY74OkaFHYdTNHYGLg9nFKRw'
bot = telebot.TeleBot(TOKEN)

# Фиксированный код подарка
GIFT_CODE = "#Code5516#116"

# Словарь для отслеживания пользователей и их юзернеймов
activated_users = {}

# Стартовое сообщение
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    text = "🎉 С Новым годом! Вот твой подарок 🎁"

    # Кнопка «Получить подарок»
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Получить подарок", callback_data='get_gift')
    markup.add(button)

    bot.send_message(chat_id, text, reply_markup=markup)

# Обработка нажатия кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id

    if call.data == 'get_gift':
        if chat_id in activated_users:
            bot.send_message(chat_id, "⚠️ Вы уже активировали код!")
        else:
            bot.send_message(chat_id, "Введите код:")
            bot.register_next_step_handler_by_chat_id(chat_id, check_code)

# Функция проверки кода
def check_code(message):
    chat_id = message.chat.id
    user_code = message.text.strip()

    if chat_id in activated_users:
        bot.send_message(chat_id, "⚠️ Вы уже активировали код!")
        return

    if user_code == GIFT_CODE:
        bot.send_message(chat_id, "✅ Код верный! Теперь напишите свой юзернейм, чтобы получить подарок:")
        bot.register_next_step_handler_by_chat_id(chat_id, get_username)
    else:
        bot.send_message(chat_id, "❌ Код неверный. Попробуйте ещё раз.")
        bot.register_next_step_handler_by_chat_id(chat_id, check_code)

# Функция для получения юзернейма
def get_username(message):
    chat_id = message.chat.id
    username = message.text.strip()

    activated_users[chat_id] = username  # Сохраняем юзернейм пользователя
    bot.send_message(chat_id, f"🎉 Спасибо! Юзернейм @{username} зарегистрирован, вы получили 100 ⭐ Telegram!")

# Запуск бота
bot.infinity_polling()
