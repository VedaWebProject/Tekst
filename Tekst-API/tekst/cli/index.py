async def run() -> None:
    from tekst import db, search

    await db.init_odm()
    await search.create_indices_task()
    await search.close()
    await db.close()
