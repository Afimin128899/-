from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from app.keyboards.main import main_menu
from app.config import ADMIN_IDS

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message, db):
    args = message.text.split()
    ref_id = int(args[1]) if len(args) > 1 and args[1].isdigit() else None

    async with db.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT tg_id FROM users WHERE tg_id=$1",
            message.from_user.id
        )

        if not user:
            await conn.execute(
                "INSERT INTO users (tg_id, referrer_id) VALUES ($1,$2)",
                message.from_user.id,
                ref_id if ref_id != message.from_user.id else None
            )

            if ref_id:
                await conn.execute(
                    "UPDATE users SET balance = balance + 2 WHERE tg_id=$1",
                    ref_id
                )

    await message.answer(
        "👋 Добро пожаловать!",
        reply_markup=main_menu(message.from_user.id in ADMIN_IDS)
    )
