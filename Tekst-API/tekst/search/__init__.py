import asyncio

from datetime import datetime
from typing import Any
from uuid import uuid4

from beanie.operators import Eq
from elasticsearch import Elasticsearch

from tekst import locks
from tekst.config import TekstConfig, get_config
from tekst.logging import log
from tekst.models.content import ContentBaseDocument
from tekst.models.location import LocationDocument
from tekst.models.resource import ResourceBaseDocument
from tekst.models.search import SearchResults, SearchSettings
from tekst.models.text import TextDocument
from tekst.resources import resource_types_mgr
from tekst.search.responses import IndexInfoResponse
from tekst.search.templates import (
    IDX_ALIAS,
    IDX_NAME_PATTERN,
    IDX_NAME_PATTERN_ANY,
    IDX_NAME_PREFIX,
    IDX_TEMPLATE,
    IDX_TEMPLATE_NAME,
    IDX_TEMPLATE_NAME_PATTERN,
)


_cfg: TekstConfig = get_config()
_es_client: Elasticsearch | None = None


async def init_es_client(
    es_uri: str | None = None,
    *,
    overwrite_existing_index: bool = False,
) -> Elasticsearch:
    global _es_client
    if _es_client is None:
        log.info("Initializing Elasticsearch client...")
        _es_client = Elasticsearch(es_uri or _cfg.es_uri)
        for i in range(_cfg.es_init_timeout_s):
            if _es_client.ping():
                break
            if i % 10 == 0:
                log.debug(
                    "Waiting for Elasticsearch service "
                    f"({i}/{_cfg.es_init_timeout_s} seconds)..."
                )
            await asyncio.sleep(1)
        else:
            raise RuntimeError("Timed out waiting for Elasticsearch service!")
        await _setup_index_template()
        await create_index(overwrite_existing_index=overwrite_existing_index)
    return _es_client


async def _get_es_client(es_uri: str | None = None) -> Elasticsearch:
    return await init_es_client(es_uri)


def close() -> None:
    global _es_client
    if _es_client is not None:
        _es_client.close()
        _es_client = None


async def _setup_index_template() -> None:
    client: Elasticsearch = await _get_es_client()
    log.debug(
        f'Setting up index template "{IDX_TEMPLATE_NAME}" '
        f'for pattern "{IDX_NAME_PATTERN}"...'
    )
    # delete possible existing index templates that could cause conflicts
    if client.indices.exists_index_template(name=IDX_TEMPLATE_NAME_PATTERN):
        client.indices.delete_index_template(name=IDX_TEMPLATE_NAME_PATTERN)
    # create index template
    client.indices.put_index_template(
        name=IDX_TEMPLATE_NAME,
        index_patterns=IDX_NAME_PATTERN,
        template=IDX_TEMPLATE,
        priority=500,
    )


async def create_index(*, overwrite_existing_index: bool = True) -> None:
    # prepare
    new_index_name = IDX_NAME_PREFIX + uuid4().hex
    log.info(f'Creating index "{new_index_name}"...')

    # check and set lock
    if await locks.is_locked(locks.LockKey.INDEX_CREATE_UPDATE):
        log.warning(
            'Aborting index creation because of active lock "index_create_update"'
        )
        return
    else:
        await locks.lock(locks.LockKey.INDEX_CREATE_UPDATE)

    try:
        # get existing search indices
        client: Elasticsearch = await _get_es_client()
        existing_indices = [
            idx for idx in client.indices.get(index=IDX_NAME_PATTERN_ANY)
        ]
        if existing_indices:
            if overwrite_existing_index:
                log.debug("The new index will overwrite the existing one...")
            else:
                log.warning("An index already exists. Aborting index creation.")
                return

        # create index (index template will be applied!)
        client.indices.create(
            index=new_index_name,
            aliases={IDX_ALIAS: {}},
        )

        # extend index mappings adding one extra field for each existing resource
        extra_properties = {}
        for res in await ResourceBaseDocument.find_all(
            with_children=True,
            lazy_parse=True,
        ).to_list():
            extra_properties[str(res.id)] = {
                "properties": resource_types_mgr.get(
                    res.resource_type
                ).index_doc_properties()
            }
        resp = client.indices.put_mapping(
            index=new_index_name,
            body={"properties": extra_properties},
        )
        if not resp or not resp.get("acknowledged"):
            raise RuntimeError("Failed to extend index mappings!")

        # populate newly created index
        await _populate_index(new_index_name)

        # delete all other/old indices matching the used index naming pattern
        if existing_indices:
            client.indices.delete(index=existing_indices)

        # perform initial bogus search (to initialize index stats)
        client.search(index=IDX_ALIAS, query={"match_all": {}})
    finally:
        # release lock
        await locks.release(locks.LockKey.INDEX_CREATE_UPDATE)


# async def _populate_index(index_name: str) -> None:
#     client: Elasticsearch = await _get_es_client()
#     log.debug(f'Populating index "{index_name}"...')

#     # populate index
#     for text in await TextDocument.find_all(lazy_parse=True).to_list():
#         for level in range(len(text.levels)):
#             bulk_req_body = []
#             # get resources for this text and level
#             resources = await ResourceBaseDocument.find(
#                 ResourceBaseDocument.text_id == text.id,
#                 ResourceBaseDocument.level == level,
#                 with_children=True,
#                 lazy_parse=True,
#             ).to_list()
#             # create one index document per location
#             for location in await LocationDocument.find(
#                 LocationDocument.text_id == text.id,
#                 LocationDocument.level == level,
#                 lazy_parse=True,
#             ).to_list():
#                 location_index_doc = {
#                     "label": location.label,
#                     "text_id": str(location.text_id),
#                     "level": location.level,
#                     "position": location.position,
#                 }
#                 # add data for each content for this location
#                 for content in await ContentBaseDocument.find(
#                     Eq(ContentBaseDocument.location_id, location.id),
#                     In(
#                         ContentBaseDocument.resource_id,
#                         [res.id for res in resources],
#                     ),
#                     with_children=True,
#                 ).to_list():
#                     location_index_doc[str(content.resource_id)] = (
#                         resource_types_mgr.get(
#                             content.resource_type
#                         ).index_doc_data(content)
#                     )

#                 bulk_req_body.append(
#                     {"index": {"_index": index_name, "_id": str(location.id)}}
#                 )
#                 bulk_req_body.append(location_index_doc)

#             # bulk index documents representing this text's locations
#             resp = client.bulk(body=bulk_req_body)
#             if resp and not resp.get("errors", False):
#                 log.debug(
#                     f'Indexing finished for "{text.title}", '
#                     f'level "{pick_translation(text.levels[level])}".'
#                 )
#             else:
#                 log.error(
#                     f"There were errors populating index '{index_name}' "
#                     f"with documents for text '{text.title}'."
#                 )


async def _populate_index(index_name: str) -> None:
    client: Elasticsearch = await _get_es_client()
    bulk_index_max_size = 1000
    bulk_index_body = []
    errors = False

    for text in await TextDocument.find_all(lazy_parse=True).to_list():
        # Initialize stack with all level 0 locations (sorted) of the current text.
        # Each item on the stack is a tuple containing (1) the location labels from the
        # root level up to the current location and (2) the location itself.
        stack = [
            ([location.label], location)
            for location in await LocationDocument.find(
                LocationDocument.text_id == text.id,
                LocationDocument.level == 0,
                lazy_parse=True,
            )
            .sort(+LocationDocument.position)
            .to_list()
        ]

        # abort if stack is empty
        if not stack:
            continue

        while stack:
            labels, location = stack.pop(0)
            full_label = text.loc_delim.join(labels)

            # create index document for this location
            location_index_doc = {
                "label": location.label,
                "full_label": full_label,
                "text_id": str(location.text_id),
                "level": location.level,
                "position": location.position,
            }

            # add data for each content for this location
            for content in await ContentBaseDocument.find(
                Eq(ContentBaseDocument.location_id, location.id),
                with_children=True,
            ).to_list():
                location_index_doc[str(content.resource_id)] = resource_types_mgr.get(
                    content.resource_type
                ).index_doc_data(content)

            # add index document to bulk index request body
            bulk_index_body.append(
                {"index": {"_index": index_name, "_id": str(location.id)}}
            )
            bulk_index_body.append(location_index_doc)

            # check bulk request body size, fire bulk request if necessary
            if len(bulk_index_body) / 2 >= bulk_index_max_size:
                errors |= not _bulk_index(client, bulk_index_body)
                bulk_index_body = []

            # add all child locations to the stack
            stack.extend(
                [
                    (labels + [child.label], child)
                    for child in await LocationDocument.find(
                        LocationDocument.parent_id == location.id,
                        lazy_parse=True,
                    )
                    .sort(+LocationDocument.position)
                    .to_list()
                ]
            )

        # index the remaining documents
        errors |= not _bulk_index(client, bulk_index_body)
        bulk_index_body = []

        # log the results (very superficially)
        if errors:
            log.error(f"There were errors populating index for '{text.title}'.")
        else:
            log.debug(f"Indexing finished for '{text.title}'.")
        errors = False


def _bulk_index(client: Elasticsearch, reqest_body: dict[str, Any]) -> bool:
    resp = client.bulk(body=reqest_body)
    return bool(resp) and not resp.get("errors", False)


def get_index_creation_time() -> datetime:
    client: Elasticsearch = _es_client
    idx_settings = client.indices.get_settings(
        index=IDX_ALIAS, name="index.creation_date", flat_settings=True
    )
    try:
        ts = int(list(idx_settings.body.values())[0]["settings"]["index.creation_date"])
        return datetime.fromtimestamp(ts / 1000)
    except Exception:
        return datetime.now()


async def get_index_info():
    client: Elasticsearch = await _get_es_client()
    info = client.indices.stats(index=IDX_ALIAS, human=True).body
    index_info = list(info["indices"].values())[0]["total"]
    return IndexInfoResponse(
        documents=index_info["docs"]["count"],
        size=index_info["store"]["size"],
        searches=index_info["search"]["query_total"],
    )


def search_quick(
    query: str,
    settings: SearchSettings = SearchSettings(),
) -> SearchResults:
    client: Elasticsearch = _es_client
    return SearchResults.from_es_results(
        results=client.search(
            index=IDX_ALIAS,
            query={
                "simple_query_string": {
                    "query": query,
                    "fields": ["*.strict" if settings.strict else "*"],
                    "default_operator": settings.default_operator,
                }
            },
        ),
        index_creation_time=get_index_creation_time(),
    )
