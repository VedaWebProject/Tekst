from tekst import db


async def counter_incr(counter_id: str, amount: int = 1) -> None:
    """Increment a counter by a given amount."""
    await db.get_db()["counters"].update_one(
        {"_id": counter_id},
        {"$inc": {"value": amount}},
        upsert=True,
    )


async def counter_get(counter_id: str) -> int:
    """Get the value of a counter."""
    counter = await db.get_db()["counters"].find_one({"_id": counter_id})
    return counter["value"] if counter else 0
