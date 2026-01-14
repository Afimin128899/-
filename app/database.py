import asyncpg
from app.config import (
    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
)

pool: asyncpg.Pool | None = None

async def init_db():
    global pool
    pool = await asyncpg.create_pool(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        min_size=1,
        max_size=10
    )

async def get_pool() -> asyncpg.Pool:
    return pool
