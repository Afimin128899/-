import os
from flyerapi import Flyer
from app.services.balance import add_balance, safe_subtract_balance

flyer = Flyer(os.getenv("FLYER_API_KEY"))

async def sync_flyer_tasks(pool):
    async with pool.acquire() as conn:
        users = await conn.fetch("SELECT tg_id FROM users")
        tasks = await conn.fetch("SELECT task_key, reward FROM tasks")

        for user in users:
            uid = user["tg_id"]

            for task in tasks:
                completed = await flyer.check_task(
                    user_id=uid,
                    signature=task["task_key"]
                )

                row = await conn.fetchrow(
                    "SELECT status FROM user_tasks WHERE tg_id=$1 AND task_key=$2",
                    uid, task["task_key"]
                )

                # выполнено → начислить
                if completed and not row:
                    await conn.execute(
                        "INSERT INTO user_tasks VALUES ($1,$2,'done')",
                        uid, task["task_key"]
                    )
                    await add_balance(
                        conn,
                        uid,
                        task["reward"],
                        f"Flyer: {task['task_key']} completed"
                    )

                # отписался → списать
                if not completed and row and row["status"] == "done":
                    await conn.execute(
                        "UPDATE user_tasks SET status='revoked' WHERE tg_id=$1 AND task_key=$2",
                        uid, task["task_key"]
                    )
                    await safe_subtract_balance(
                        conn,
                        uid,
                        task["reward"],
                        f"Flyer: {task['task_key']} revoked"
                    )
