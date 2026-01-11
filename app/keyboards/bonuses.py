from datetime import date

async def daily_bonus(conn, tg_id: int):
    today = date.today()

    row = await conn.fetchrow(
        "SELECT created_at FROM balance_logs "
        "WHERE tg_id=$1 AND reason='Daily bonus' "
        "ORDER BY created_at DESC LIMIT 1",
        tg_id
    )

    if row and row["created_at"].date() == today:
        return False

    await conn.execute(
        "UPDATE users SET balance = balance + 1 WHERE tg_id=$1",
        tg_id
    )
    await conn.execute(
        "INSERT INTO balance_logs (tg_id, change, reason) VALUES ($1,1,'Daily bonus')",
        tg_id
    )
    return True
