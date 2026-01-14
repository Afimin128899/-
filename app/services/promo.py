async def apply_promo_code(conn, tg_id: int, code: str):
    promo = await conn.fetchrow(
        "SELECT reward, uses_left FROM promo_codes WHERE code=$1",
        code
    )
    if not promo or promo["uses_left"] <= 0:
        return False, "Промокод недействителен"

    used = await conn.fetchrow(
        "SELECT 1 FROM promo_used WHERE tg_id=$1 AND code=$2",
        tg_id, code
    )
    if used:
        return False, "Ты уже использовал этот промокод"

    await conn.execute(
        "UPDATE promo_codes SET uses_left = uses_left - 1 WHERE code=$1",
        code
    )
    await conn.execute(
        "INSERT INTO promo_used VALUES ($1,$2)",
        tg_id, code
    )
    await conn.execute(
        "UPDATE users SET balance = balance + $1 WHERE tg_id=$2",
        promo["reward"], tg_id
    )

    return True, f"+{promo['reward']} ⭐ начислено"
