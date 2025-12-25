import logging, hashlib, random, string
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ============ CONFIG ============
API_TOKEN = "8593306321:AAFP3lo0Rn2Mae36mwt77ShiLQS9zYFfyEo"
ADMIN_ID = 8332885829

START_BALANCE = 10
BET = 3
# ================================

logging.basicConfig(level=logging.INFO)
bot = Bot(API_TOKEN)
dp = Dispatcher(bot)

balances = {}
games = {}
checks = {}

# ============ UTILS ============
def sha256(t): return hashlib.sha256(t.encode()).hexdigest()
def gen_code(): return ''.join(random.choices(string.ascii_uppercase+string.digits,k=10))

def get_balance(uid): return balances.get(uid, START_BALANCE)
def add_balance(uid,a): balances[uid]=get_balance(uid)+a
def sub_balance(uid,a):
    if get_balance(uid)>=a:
        balances[uid]-=a
        return True
    return False

# ============ CARDS ============
def deck():
    r=['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    s=['♠','♥','♦','♣']
    return [x+y for x in r for y in s]

def shuffle(d,seed):
    d=d[:]; out=[]
    for i in range(len(d)):
        h=sha256(seed+str(i))
        out.append(d.pop(int(h,16)%len(d)))
    return out

def value(h):
    v,a=0,0
    for c in h:
        r=c[:-1]
        if r in ['J','Q','K']: v+=10
        elif r=='A': v+=11; a+=1
        else: v+=int(r)
    while v>21 and a: v-=10; a-=1
    return v

# ============ KEYBOARDS ============
def main_kb():
    kb=InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("🃏 Играть",callback_data="play"),
        InlineKeyboardButton("👤 Профиль",callback_data="profile")
    )
    kb.add(InlineKeyboardButton("💳 Активировать чек",callback_data="check"))
    return kb

def game_kb(double=True):
    kb=InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("➕ Взять",callback_data="hit"),
        InlineKeyboardButton("⏹ Стоп",callback_data="stand")
    )
    if double:
        kb.add(InlineKeyboardButton("✖️2 Удвоить",callback_data="double"))
    return kb

# ============ START ============
@dp.message_handler(commands=['start'])
async def start(m):
    balances.setdefault(m.from_user.id,START_BALANCE)
    await m.answer("🎰 Казино-бот\n\nВыбери действие:",reply_markup=main_kb())

# ============ PROFILE ============
@dp.callback_query_handler(lambda c:c.data=="profile")
async def profile(c):
    await c.message.edit_text(
        f"👤 Профиль\n\n"
        f"🆔 ID: {c.from_user.id}\n"
        f"⭐ Баланс: {get_balance(c.from_user.id)}",
        reply_markup=main_kb()
    )

# ============ BLACKJACK ============
@dp.callback_query_handler(lambda c:c.data=="play")
async def play(c):
    uid=c.from_user.id
    if not sub_balance(uid,BET):
        await c.answer("❌ Недостаточно ⭐",show_alert=True)
        return

    seed=sha256(str(random.random()))
    d=shuffle(deck(),seed)
    p=[d.pop(),d.pop()]
    dl=[d.pop(),d.pop()]

    games[uid]={
        "deck":d,"p":p,"d":dl,
        "seed":seed,"bet":BET,"double":True
    }

    await c.message.edit_text(
        f"🔐 Hash:\n`{sha256(seed)}`\n\n"
        f"🃏 Ты: {p} ({value(p)})\n"
        f"🃏 Дилер: {dl[0]} ?",
        parse_mode="Markdown",
        reply_markup=game_kb()
    )

@dp.callback_query_handler(lambda c:c.data=="hit")
async def hit(c):
    g=games[c.from_user.id]
    g["double"]=False
    g["p"].append(g["deck"].pop())
    if value(g["p"])>21:
        await bust(c)
    else:
        await c.message.edit_text(
            f"🃏 Ты: {g['p']} ({value(g['p'])})\n"
            f"🃏 Дилер: {g['d'][0]} ?",
            reply_markup=game_kb(False)
        )

@dp.callback_query_handler(lambda c:c.data=="stand")
async def stand(c): await finish(c)

@dp.callback_query_handler(lambda c:c.data=="double")
async def double(c):
    g=games[c.from_user.id]
    if not g["double"] or not sub_balance(c.from_user.id,g["bet"]):
        await c.answer("❌ Нельзя",show_alert=True)
        return
    g["bet"]*=2
    g["p"].append(g["deck"].pop())
    if value(g["p"])>21:
        await bust(c)
    else:
        await finish(c)

async def finish(c):
    g=games[c.from_user.id]
    while value(g["d"])<17:
        g["d"].append(g["deck"].pop())
    p,d=value(g["p"]),value(g["d"])

    if d>21 or p>d:
        add_balance(c.from_user.id,g["bet"]*2); r="🎉 Победа"
    elif p==d:
        add_balance(c.from_user.id,g["bet"]); r="🤝 Ничья"
    else: r="❌ Проигрыш"

    await c.message.edit_text(
        f"{r}\n\n"
        f"🃏 Ты: {g['p']} ({p})\n"
        f"🃏 Дилер: {g['d']} ({d})\n\n"
        f"🔓 Seed:\n`{g['seed']}`\n"
        f"⭐ Баланс: {get_balance(c.from_user.id)}",
        parse_mode="Markdown",
        reply_markup=main_kb()
    )
    del games[c.from_user.id]

async def bust(c):
    g=games[c.from_user.id]
    await c.message.edit_text(
        f"💥 Перебор\n\n🃏 {g['p']}\n\n🔓 `{g['seed']}`",
        parse_mode="Markdown",
        reply_markup=main_kb()
    )
    del games[c.from_user.id]

# ============ CHECKS ============
@dp.callback_query_handler(lambda c:c.data=="check")
async def ask_check(c):
    await c.message.edit_text("💳 Введи чек код:")

@dp.message_handler(lambda m:m.text in checks)
async def activate(m):
    amt=checks.pop(m.text)
    add_balance(m.from_user.id,amt)
    await m.answer(f"✅ Чек активирован: +{amt} ⭐",reply_markup=main_kb())

# ============ ADMIN ============
@dp.message_handler(commands=['add'])
async def admin_add(m):
    if m.from_user.id!=ADMIN_ID: return
    _,uid,amt=m.text.split()
    add_balance(int(uid),int(amt))
    await m.answer("✅ Валюта выдана")

@dp.message_handler(commands=['check'])
async def admin_check(m):
    if m.from_user.id!=ADMIN_ID: return
    _,amt=m.text.split()
    code=gen_code()
    checks[code]=int(amt)
    await m.answer(f"💳 Чек: `{code}` (+{amt} ⭐)",parse_mode="Markdown")

# ============ RUN ============
if __name__=="__main__":
    executor.start_polling(dp)
