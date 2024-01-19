# from collections import deque

# from tekst.models.location import TextDocument, TextRead
# from tekst.models.location import LocationDocument


# async def import_text(data: dict) -> TextRead | None:
#     # create and save text object
#     text = await TextDocument(**data).create()
#     stack = deque()
#     positions = [0]

#     # push locations of first structure level onto stack
#     for location in data.get("locations", []):
#         location["parentId"] = None
#         location["textId"] = text.id
#         location["level"] = 0
#         location["position"] = positions[0]
#         stack.append(location)
#         positions[0] += 1

#     # process stack
#     while stack:
#         location_data = stack.pop()
#         location = await LocationDocument(**location_data).create()

#         for u in location_data.get("locations", []):
#             u["parentId"] = location.id
#             u["textId"] = text.id
#             u["level"] = location.level + 1
#             if len(positions) <= u["level"]:
#                 positions.append(0)
#             u["position"] = positions[u["level"]]
#             positions[u["level"]] += 1
#             stack.append(u)

#     return text
