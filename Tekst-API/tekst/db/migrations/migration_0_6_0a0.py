from tekst.db import Database


async def migration(db: Database) -> None:
    # remove field "always_show_text_info" from platform state
    await db.state.update_many({}, {"$unset": {"always_show_text_info": 1}})
