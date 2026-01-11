async def add_balance(conn, tg_id: int, amount: int, reason: str):
    await conn.execute(
        "UPDATE users SET balance = balance + $1 WHERE tg_id=$2",
        amount, tg_id
    )
    await conn.execute(
        "INSERT INTO balance_logs (tg_id, change, reason) VALUES ($1,$2,$3)",
        tg_id, amount, reason
    )


async def safe_subtract_balance(conn, tg_id: int, amount: int, reason: str):
    row = await conn.fetchrow(
        "SELECT balance FROM users WHERE tg_id=$1",
        tg_id
    )
    if not row:
        return

    balance = row["balance"]
    real = min(balance, amount)

    if real <= 0:
        return

    await conn.execute(
        "UPDATE users SET balance = balance - $1 WHERE tg_id=$2",
        real, tg_id
    )
    await conn.execute(
        "INSERT INTO balance_logs (tg_id, change, reason) VALUES ($1,$2,$3)",
        tg_id, -real, reason
    )
