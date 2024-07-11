import asyncio

from datetime import datetime, timezone
from time import process_time
from typing import Any
from uuid import uuid4

from beanie import PydanticObjectId
from beanie.operators import Eq, In
from elasticsearch import Elasticsearch

from tekst import db, tasks
from tekst.config import TekstConfig, get_config
from tekst.logs import log
from tekst.models.content import ContentBaseDocument
from tekst.models.location import LocationDocument
from tekst.models.resource import ResourceBaseDocument
from tekst.models.search import (
    AdvancedSearchSettings,
    GeneralSearchSettings,
    IndexInfo,
    QuickSearchSettings,
    SearchResults,
)
from tekst.models.text import TextDocument
from tekst.models.user import UserRead
from tekst.resources import (
    AnyResourceSearchQuery,
    init_resource_types_mgr,
    resource_types_mgr,
)
from tekst.search.templates import (
    IDX_ALIAS,
    IDX_NAME_PATTERN,
    IDX_NAME_PATTERN_ANY,
    IDX_NAME_PREFIX,
    IDX_TEMPLATE,
    IDX_TEMPLATE_NAME,
    IDX_TEMPLATE_NAME_PATTERN,
    QUERY_SOURCE_INCLUDES,
    SORTING_PRESETS,
)


_cfg: TekstConfig = get_config()
_es_client: Elasticsearch | None = None


async def init_es_client(
    es_uri: str = _cfg.es.uri,
) -> Elasticsearch:
    global _es_client
    if _es_client is None:
        log.info("Initializing Elasticsearch client...")
        _es_client = Elasticsearch(es_uri)
        for i in range(_cfg.es.init_timeout_s):
            if _es_client.ping():
                break
            if i % 10 == 0:
                log.debug(
                    f"Waiting for Elasticsearch service at {es_uri} "
                    f"({i}/{_cfg.es.init_timeout_s} seconds)..."
                )
            await asyncio.sleep(1)
        else:
            log.critical(f"Could not connect to Elasticsearch at {es_uri}!")
            raise RuntimeError("Timed out waiting for Elasticsearch service!")
    return _es_client


async def _get_es_client(es_uri: str = _cfg.es.uri) -> Elasticsearch:
    return await init_es_client(es_uri)


def get_es_status() -> dict[str, Any] | None:
    global _es_client
    return _es_client.info() if _es_client else None


def close() -> None:
    global _es_client
    if _es_client is not None:
        _es_client.close()
        _es_client = None


async def setup_elasticsearch() -> None:
    """This is called by the setup routine"""
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


async def task_create_indices(overwrite_existing_index: bool = True) -> dict[str, Any]:
    start_time = process_time()

    # get existing search indices
    client: Elasticsearch = await _get_es_client()
    existing_indices = [idx for idx in client.indices.get(index=IDX_NAME_PATTERN_ANY)]

    if existing_indices:
        if overwrite_existing_index:
            log.debug("The new index will overwrite the existing one...")
        else:
            log.warning("An index already exists. Aborting index creation.")
            return

    for text in await TextDocument.find_all().to_list():
        # create indices (index template will be applied!)
        new_index_name = f"{IDX_NAME_PREFIX}{text.slug}_{text.id}_{str(uuid4().hex)}"
        client.indices.create(
            index=new_index_name,
            aliases={IDX_ALIAS: {}},
        )

        # extend index mappings adding one extra field for each target resource
        extra_properties = {}
        for res in await ResourceBaseDocument.find(
            ResourceBaseDocument.text_id == text.id,
            Eq(ResourceBaseDocument.public, True),
            with_children=True,
        ).to_list():
            extra_properties[str(res.id)] = {
                "properties": resource_types_mgr.get(
                    res.resource_type
                ).index_doc_props(),
            }
        resp = client.indices.put_mapping(
            index=new_index_name,
            body={"properties": {"resources": {"properties": extra_properties}}},
        )
        if not resp or not resp.get("acknowledged"):
            raise RuntimeError("Failed to extend index mappings!")

        # populate newly created index
        await _populate_index(new_index_name, text)

    # delete all other/old indices matching the used index naming pattern
    if existing_indices:
        client.indices.delete(index=existing_indices)

    # perform initial bogus search (to initialize index stats)
    client.search(index=IDX_ALIAS, query={"match_all": {}})

    return {
        "took": f"{round(process_time() - start_time, 2)}",
    }


async def create_indices(
    *,
    user: UserRead | None = None,
    overwrite_existing_index: bool = True,
) -> tasks.TaskDocument:
    log.info("Creating search index ...")
    # create index task
    return await tasks.create_task(
        task_create_indices,
        tasks.TaskType.INDICES_CREATE_UPDATE,
        user_id=user.id if user else None,
        task_kwargs={
            "overwrite_existing_index": overwrite_existing_index,
        },
    )


async def util_create_indices():
    init_resource_types_mgr()
    await db.init_odm()
    await task_create_indices()


async def _populate_index(index_name: str, text: TextDocument) -> None:
    if text is None:
        raise ValueError("text is None!")
    client: Elasticsearch = await _get_es_client()
    bulk_index_max_size = 1000
    bulk_index_body = []
    errors = False
    target_resource_ids = [
        res.id
        for res in await ResourceBaseDocument.find(
            ResourceBaseDocument.text_id == text.id,
            Eq(ResourceBaseDocument.public, True),
            with_children=True,
        ).to_list()
    ]

    log.debug(f"Indexing resources for text '{text.title}'...")
    start_time = process_time()
    # Initialize stack with all level 0 locations (sorted) of the current text.
    # Each item on the stack is a tuple containing (1) the location labels from the
    # root level up to the current location and (2) the location itself.
    stack = [
        ([location.label], location)
        for location in await LocationDocument.find(
            LocationDocument.text_id == text.id,
            LocationDocument.level == 0,
        )
        .sort(+LocationDocument.position)
        .to_list()
    ]

    # abort if initial stack is empty
    if not stack:
        return

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
            "resources": {},
        }

        # add data for each content for this location
        for content in await ContentBaseDocument.find(
            Eq(ContentBaseDocument.location_id, location.id),
            In(ContentBaseDocument.resource_id, target_resource_ids),
            with_children=True,
        ).to_list():
            # add resource content document to location index document
            location_index_doc["resources"][str(content.resource_id)] = (
                resource_types_mgr.get(content.resource_type).index_doc_data(content)
            )

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
        log.info(
            f"Finished indexing resources for text '{text.title}' in "
            f"{(process_time() - start_time):.2f} seconds."
        )
    errors = False


def _bulk_index(client: Elasticsearch, reqest_body: dict[str, Any]) -> bool:
    resp = client.bulk(body=reqest_body)
    return bool(resp) and not resp.get("errors", False)


def _get_index_creation_time() -> datetime:
    """Returns the creation date of the index as a UTC datetime."""
    client: Elasticsearch = _es_client
    idx_settings = client.indices.get_settings(
        index=IDX_ALIAS, name="index.creation_date", flat_settings=True
    )
    try:
        ts = int(list(idx_settings.body.values())[0]["settings"]["index.creation_date"])
        return datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    except Exception:
        return datetime.now()


async def get_indices_info() -> list[IndexInfo]:
    client: Elasticsearch = await _get_es_client()
    info_resp = client.indices.stats(index=IDX_ALIAS, human=True).body
    info_data = {name: data["total"] for name, data in info_resp["indices"].items()}
    creation_time = _get_index_creation_time()
    return [
        IndexInfo(
            text_id=idx_name.split("_")[-2],
            documents=idx_info["docs"]["count"],
            size=idx_info["store"]["size"],
            searches=idx_info["search"]["query_total"],
            last_indexed=creation_time,
        )
        for idx_name, idx_info in info_data.items()
    ]


async def _get_target_resource_ids(
    *,
    user: UserRead | None = None,
    text_ids: list[PydanticObjectId] | None = None,
    resource_types: list[str] | None = None,
) -> list[str]:
    """
    Returns a constrained list of IDs for the target resources for a search request,
    based on the requesting user's permissions, target texts and resource types.
    """
    return [
        str(res.id)
        for res in await ResourceBaseDocument.find(
            In(ResourceBaseDocument.text_id, text_ids) if text_ids else {},
            In(ResourceBaseDocument.resource_type, resource_types)
            if resource_types
            else {},
            Eq(ResourceBaseDocument.public, True),
            await ResourceBaseDocument.access_conditions_read(user),
            with_children=True,
        ).to_list()
    ]


async def search_quick(
    user: UserRead | None,
    query_string: str | None = None,
    settings_general: GeneralSearchSettings = GeneralSearchSettings(),
    settings_quick: QuickSearchSettings = QuickSearchSettings(),
) -> SearchResults:
    client: Elasticsearch = _es_client
    target_resource_ids = await _get_target_resource_ids(
        user=user,
        text_ids=settings_quick.texts,  # constrain target texts
        resource_types=[
            "plainText",
            "richText",
            "audio",
            "images",
            "externalReferences",
        ],  # constrain target resource types for quick search
    )

    # compose a list of target index fields based on the resources to search:
    field_pattern_suffix = ".*.strict" if settings_general.strict else ".*"
    fields = [
        f"resources.{res_id}{field_pattern_suffix}" for res_id in target_resource_ids
    ]

    # compose the query
    es_query = {
        "simple_query_string": {
            "query": query_string or "*",  # fall back to '*' if empty
            "fields": fields,
            "default_operator": settings_quick.default_operator,
            "analyze_wildcard": True,
        }
    }

    log.debug(f"Running ES query: {es_query}")

    # perform the search
    return SearchResults.from_es_results(
        results=client.search(
            index=IDX_ALIAS,
            query=es_query,
            highlight={
                "fields": {"resources.*": {}},
            },
            from_=settings_general.pagination.es_from(),
            size=settings_general.pagination.es_size(),
            track_scores=True,
            sort=SORTING_PRESETS.get(settings_general.sorting_preset),
            source={"includes": QUERY_SOURCE_INCLUDES},
        ),
        index_creation_time=_get_index_creation_time(),
    )


async def search_advanced(
    user: UserRead | None,
    queries: list[AnyResourceSearchQuery],
    settings_general: GeneralSearchSettings = GeneralSearchSettings(),
    settings_advanced: AdvancedSearchSettings = AdvancedSearchSettings(),
) -> SearchResults:
    client: Elasticsearch = _es_client
    target_resource_ids = await _get_target_resource_ids(user=user)

    # construct all the sub-queries
    sub_queries_must = []
    sub_queries_should = []

    for q in queries:
        if str(q.common.resource_id) in target_resource_ids:
            resource_es_queries = resource_types_mgr.get(
                q.resource_type_specific.resource_type
            ).es_queries(
                query=q,
                strict=settings_general.strict,
            )
            if q.common.optional:
                sub_queries_should.extend(resource_es_queries)
            else:
                sub_queries_must.extend(resource_es_queries)

    # compose the overall compound query
    es_query = {
        "bool": dict(
            **({"must": sub_queries_must} if sub_queries_must else {}),
            **({"should": sub_queries_should} if sub_queries_should else {}),
        )
    }

    # if the search request didn't resolve to any valid ES queries, match nothing
    if not es_query.get("bool"):
        es_query = {"match_none": {}}

    log.debug(f"Running ES query: {es_query}")

    # perform the search
    return SearchResults.from_es_results(
        results=client.search(
            index=IDX_ALIAS,
            query=es_query,
            highlight={
                "fields": {"*": {}},
            },
            from_=settings_general.pagination.es_from(),
            size=settings_general.pagination.es_size(),
            track_scores=True,
            sort=SORTING_PRESETS.get(settings_general.sorting_preset),
            source={"includes": QUERY_SOURCE_INCLUDES},
        ),
        index_creation_time=_get_index_creation_time(),
    )
