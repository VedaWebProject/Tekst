from tekst.db import Database


async def migration(db: Database) -> None:
    for res in await db.resources.find({}).to_list():
        if res.get("citation"):
            res["citation"] = (
                str(res["citation"])
                .replace(r"<curr-date>", r"{{curr_date}}")
                .replace(r"<res-url>", r"{{res_url}}")
            )
            await db.resources.replace_one({"_id": res["_id"]}, res)

    pf_state = await db.state.find_one()
    if pf_state and pf_state.get("global_citation_suffix"):
        pf_state["global_citation_suffix"] = (
            pf_state["global_citation_suffix"]
            .replace(r"<curr-date>", r"{{curr_date}}")
            .replace(r"<res-url>", r"{{res_url}}")
        )
        await db.state.replace_one({"_id": pf_state["_id"]}, pf_state)
