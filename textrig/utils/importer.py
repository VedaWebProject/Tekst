from collections import deque

from textrig.models.text import NodeDocument, TextDocument, TextRead


async def import_text(data: dict) -> TextRead | None:
    # create and save text object
    text = await TextDocument(**data).create()
    stack = deque()
    indices = [0]

    # push nodes of first structure level onto stack
    for node in data.get("nodes", []):
        node["parentId"] = None
        node["textId"] = text.id
        node["level"] = 0
        node["index"] = indices[0]
        stack.append(node)
        indices[0] += 1

    # process stack
    while stack:
        node_data = stack.pop()
        node = await NodeDocument(**node_data).create()

        for u in node_data.get("nodes", []):
            u["parentId"] = node.id
            u["textId"] = text.id
            u["level"] = node.level + 1
            if len(indices) <= u["level"]:
                indices.append(0)
            u["index"] = indices[u["level"]]
            indices[u["level"]] += 1
            stack.append(u)

    return text
