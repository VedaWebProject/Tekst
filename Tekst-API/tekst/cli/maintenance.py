async def run() -> None:
    from tekst import db, platform, resources, search

    await db.init_odm()
    await search.create_indices_task()
    await resources.call_resource_precompute_hooks()
    await platform.cleanup_task()
    await search.close()
    await db.close()
