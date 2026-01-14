async def is_suspicious(conn, tg_id: int):
    actions = await conn.fetchval(
        """
        SELECT COUNT(*) FROM balance_logs
        WHERE tg_id=$1 AND created_at > NOW() - INTERVAL '10 minutes'
        """,
        tg_id
    )
    return actions > 20
