import asyncio, os, time
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from flyerapi import Flyer, APIError as FlyerAPIError

from database import init_db, add_user, get_user, update_stars, set_flyer_rewarded, add_code_db, get_code, delete_code

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
FLYER_KEY = os.getenv("FLYER_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())
flyer = Flyer(FLYER_KEY)

# ====== CONSTANTS ======
FLYER_REWARD = 0.25
REFERRAL_REWARD = 1.5
SPAM_DELAY = 2
MAX_WARNINGS = 3
MUTE_TIME = 60
spam_control = {}

# ====== FSM ======
class CodeState(StatesGroup):
    code = State()
class WithdrawState(StatesGroup):
    amount = State()
    username = State()

# ====== АНТИСПАМ ======
def check_spam(user_id: int) -> bool:
    now = time.time()
    user = spam_control.setdefault(user_id, {"last":0, "warns":0, "mute_until":0})
    if now < user["mute_until"]:
        asyncio.create_task(log_admin(f"⚠️ Спам: {user_id} пытался действовать в муте"))
        return False
    if now - user["last"] < SPAM_DELAY:
        user["warns"] += 1
        asyncio.create_task(log_admin(f"⚠️ Предупреждение спама: {user_id}, warns {user['warns']}"))
        if user["warns"] >= MAX_WARNINGS:
            user["mute_until"] = now + MUTE_TIME
            user["warns"] = 0
            asyncio.create_task(log_admin(f"⏳ Мут {MUTE_TIME}s: {user_id}"))
        return False
    user["last"] = now
    return True

async def log_admin(text: str):
    try:
        await bot.send_message(ADMIN_ID, text)
    except:
        pass

# ====== РЕФЕРАЛЫ ======
async def handle_referral(new_user_id:int, ref_id:int):
    user = await get_user(new_user_id)
    if user and not user["referrer"]:
        if ref_id != new_user_id and await get_user(ref_id):
            user["referrer"]=ref_id
            ref_user = await get_user(ref_id)
            await update_stars(ref_id, ref_user["stars"] + REFERRAL_REWARD)
            await log_admin(f"👥 Реферал: {ref_id} получил +{REFERRAL_REWARD} ⭐ от {new_user_id}")

# ====== FLYER ======
INCOMPLETE = ("incomplete","abort")

async def flyer_check(user_id:int)->bool:
    try:
        tasks = await flyer.get_tasks(user_id=user_id)
    except FlyerAPIError:
        return True
    tasks = [t for t in tasks if t["status"] in INCOMPLETE]
    if not tasks:
        return True
    await asyncio.gather(*[flyer.check_task(user_id=user_id, signature=t["signature"]) for t in tasks])
    return True

async def flyer_reward_control(user_id:int):
    user = await get_user(user_id)
    completed = await flyer_check(user_id)
    if completed and not user["flyer_rewarded"]:
        new_stars = user["stars"] + FLYER_REWARD
        await update_stars(user_id,new_stars)
        await set_flyer_rewarded(user_id, True)
        await log_admin(f"✅ Flyer: {user_id} получил +{FLYER_REWARD} ⭐")
        await bot.send_message(user_id, f"✅ Задание выполнено\n⭐ +{FLYER_REWARD}")
    elif not completed and user["flyer_rewarded"]:
        new_stars = max(0,user["stars"] - FLYER_REWARD)
        await update_stars(user_id,new_stars)
        await set_flyer_rewarded(user_id, False)
        await log_admin(f"⚠️ Flyer: {user_id} потерял −{FLYER_REWARD} ⭐")
        await bot.send_message(user_id, f"⚠️ Задание отменено\n⭐ −{FLYER_REWARD}")

# ====== START ======
@dp.message(F.text.startswith("/start"))
async def start(message: Message):
    uid = message.from_user.id
    args = message.text.split()
    await add_user(uid)
    if len(args)==2:
        try: await handle_referral(uid,int(args[1]))
        except: pass
    kb=ReplyKeyboardMarkup(keyboard=[[KeyboardButton("👤 Профиль")],[KeyboardButton("🎁 Ввести код"),KeyboardButton("💸 Вывести")]],resize_keyboard=True)
    await message.answer("🎉 Добро пожаловать!\n⭐ Получай звёзды за активность\n👥 1 реферал = 1.5 ⭐\n💸 Минимальный вывод: 50 ⭐",reply_markup=kb)

# ====== ПРОФИЛЬ ======
@dp.message(F.text=="👤 Профиль")
async def profile(message: Message):
    user = await get_user(message.from_user.id)
    await message.answer(f"👤 Профиль\n⭐ Баланс: {user['stars']}\n👥 Реферал: {user['referrer']}")

# ====== КОД ======
@dp.message(F.text=="🎁 Ввести код")
async def enter_code(message:Message,state:FSMContext):
    await message.answer("🔑 Введите код:")
    await state.set_state(CodeState.code)

@dp.message(CodeState.code)
async def activate_code(message:Message,state:FSMContext):
    code = message.text.strip()
    stars = await get_code(code)
    if not stars:
        await message.answer("❌ Неверный код")
        return
    user_id = message.from_user.id
    user = await get_user(user_id)
    await update_stars(user_id,user["stars"]+stars)
    await delete_code(code)
    await log_admin(f"✅ Код активирован: {user_id} получил +{stars} ⭐ (код {code})")
    await message.answer(f"✅ Код активирован\n⭐ +{stars}")
    await state.clear()

# ====== ADD CODE ADMIN ======
@dp.message(F.text.startswith("/addcode"))
async def add_code(message:Message):
    if message.from_user.id != ADMIN_ID: return
    parts=message.text.split()
    if len(parts)!=3: await message.answer("/addcode CODE STARS"); return
    await add_code_db(parts[1],float(parts[2]))
    await message.answer(f"✅ Код {parts[1]} на {parts[2]} ⭐ добавлен")

# ====== RUN ======
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__=="__main__":
    asyncio.run(main())
