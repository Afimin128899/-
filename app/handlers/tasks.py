from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.keyboards.common import back_kb

router = Router()

@router.callback_query(F.data == "tasks")
async def tasks_handler(call: CallbackQuery, db):
    async with db.acquire() as conn:
        tasks = await conn.fetch(
            """
            SELECT t.title, t.reward, ut.status
            FROM tasks t
            LEFT JOIN user_tasks ut
            ON ut.task_key=t.task_key AND ut.tg_id=$1
            """,
            call.from_user.id
        )

    text = "✅ <b>Задания</b>\n\n"
    for t in tasks:
        status = "✅" if t["status"] == "done" else "❌"
        text += f"{status} {t['title']} (+{t['reward']}⭐)\n"

    await call.message.edit_text(text, reply_markup=back_kb())
