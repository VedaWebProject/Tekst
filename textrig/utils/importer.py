from collections import deque

from textrig.db.io import DbIO
from textrig.models.text import Node, NodeRead, Text, TextRead


async def import_text(data: dict, db_io: DbIO) -> TextRead | None:
    # create and save text object
    text = await Text(**data).create(db_io)
    stack = deque()
    indices = [0]

    # push nodes of first structure level onto stack
    for node in data.get("nodes", []):
        node["parentId"] = None
        node["textSlug"] = text.slug
        node["level"] = 0
        node["index"] = indices[0]
        stack.append(node)
        indices[0] += 1

    # process stack
    while stack:
        node_data = stack.pop()
        node: NodeRead = await Node(**node_data).create(db_io)

        for u in node_data.get("nodes", []):
            u["parentId"] = node.id
            u["textSlug"] = text.slug
            u["level"] = node.level + 1
            if len(indices) <= u["level"]:
                indices.append(0)
            u["index"] = indices[u["level"]]
            indices[u["level"]] += 1
            stack.append(u)

    return text
