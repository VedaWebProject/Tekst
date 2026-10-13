async def run(force: bool) -> None:
    from tekst import db, resources

    await db.init_odm()
    await resources.call_resource_precompute_hooks(force=force)
    await db.close()
