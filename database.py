import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# ====== ИНИЦИАЛИЗАЦИЯ БД ======
async def init_db():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            stars REAL DEFAULT 0,
            referrer BIGINT,
            flyer_rewarded BOOLEAN DEFAULT FALSE
        );
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS codes (
            code TEXT PRIMARY KEY,
            stars REAL
        );
    """)
    await conn.close()

# ====== ПОЛЬЗОВАТЕЛИ ======
async def add_user(user_id: int, referrer: int = None):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        INSERT INTO users(user_id, referrer)
        VALUES($1,$2)
        ON CONFLICT (user_id) DO NOTHING
    """, user_id, referrer)
    await conn.close()

async def get_user(user_id: int):
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow("SELECT * FROM users WHERE user_id=$1", user_id)
    await conn.close()
    if row:
        return dict(row)
    return None

async def update_stars(user_id:int, stars:float):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("UPDATE users SET stars=$1 WHERE user_id=$2", stars, user_id)
    await conn.close()

async def set_flyer_rewarded(user_id:int, rewarded:bool):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("UPDATE users SET flyer_rewarded=$1 WHERE user_id=$2", rewarded, user_id)
    await conn.close()

# ====== КОДЫ ======
async def add_code_db(code:str, stars:float):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("INSERT INTO codes(code, stars) VALUES($1,$2) ON CONFLICT (code) DO UPDATE SET stars=$2", code, stars)
    await conn.close()

async def get_code(code:str):
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow("SELECT stars FROM codes WHERE code=$1", code)
    await conn.close()
    if row: return row["stars"]
    return None

async def delete_code(code:str):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("DELETE FROM codes WHERE code=$1", code)
    await conn.close()
