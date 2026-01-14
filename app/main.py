import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from app.config import BOT_TOKEN, FLYER_SYNC_INTERVAL
from app.database import init_db
from app.middlewares.db import DbMiddleware

# handlers
from app.handlers.start import router as start_router
from app.handlers.menu import router as menu_router
from app.handlers.profile import router as profile_router
from app.handlers.tasks import router as tasks_router
from app.handlers.referrals import router as referrals_router
from app.handlers.history import router as history_router
from app.handlers.support import router as support_router
from app.handlers.withdraw import router as withdraw_router
from app.handlers.admin import router as admin_router
from app.handlers.bonuses import router as bonuses_router
from app.handlers.promo import router as promo_router

# services
from app.services.flyer import sync_flyer_tasks
from app.database import get_pool


async def flyer_loop():
    """
    Фоновая синхронизация Flyer:
    - авто начисление
    - авто списание
    """
    pool = await get_pool()
    while True:
        try:
            await sync_flyer_tasks(pool)
        except Exception as e:
            print(f"[Flyer sync error] {e}")
        await asyncio.sleep(FLYER_SYNC_INTERVAL)


async def main():
    # 1️⃣ Инициализация БД
    await init_db()

    # 2️⃣ Бот и диспетчер
    bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    # 3️⃣ Middleware (БД в каждый handler)
    dp.message.middleware(DbMiddleware())
    dp.callback_query.middleware(DbMiddleware())

    # 4️⃣ Роутеры (ВАЖЕН ПОРЯДОК)
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(profile_router)
    dp.include_router(tasks_router)
    dp.include_router(referrals_router)
    dp.include_router(history_router)
    dp.include_router(bonuses_router)
    dp.include_router(promo_router)
    dp.include_router(withdraw_router)
    dp.include_router(admin_router)
    dp.include_router(support_router)

    # 5️⃣ Фоновый Flyer sync
    asyncio.create_task(flyer_loop())

    # 6️⃣ Запуск
    print("🚀 Flyer BOT запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
