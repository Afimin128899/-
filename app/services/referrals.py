async def process_referral(conn, user_id: int):
    user = await conn.fetchrow(
        "SELECT referrer_id FROM users WHERE tg_id=$1",
        user_id
    )
    if not user or not user["referrer_id"]:
        return

    # проверяем: выполнил ли хотя бы 1 задание
    done = await conn.fetchval(
        """
        SELECT COUNT(*) FROM user_tasks
        WHERE tg_id=$1 AND status='done'
        """,
        user_id
    )
    if done < 1:
        return

    ref1 = user["referrer_id"]

    # 1 линия
    await conn.execute(
        "UPDATE users SET balance = balance + 2 WHERE tg_id=$1",
        ref1
    )

    # 2 линия
    ref2 = await conn.fetchval(
        "SELECT referrer_id FROM users WHERE tg_id=$1",
        ref1
    )
    if ref2:
        await conn.execute(
            "UPDATE users SET balance = balance + 1 WHERE tg_id=$1",
            ref2
        )
