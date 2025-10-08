from tekst.db import Database


async def migration(db: Database) -> None:
    async for state in db.state.find({}):
        state["nav_translations"] = {
            "browse": state.pop("nav_browse_entry", []),
            "search": state.pop("nav_search_entry", []),
            "info": state.pop("nav_info_entry", []),
        }
        await db.state.replace_one({"_id": state["_id"]}, state)
