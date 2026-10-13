async def run() -> None:
    from tekst import db, platform

    await db.init_odm()
    await platform.cleanup_task()
    await db.close()
