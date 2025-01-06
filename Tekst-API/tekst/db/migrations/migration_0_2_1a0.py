from tekst.db import Database


async def migration(db: Database) -> None:
    # delete platform state field "register_intro_text"
    await db.state.update_many({}, {"$unset": {"register_intro_text": ""}})
