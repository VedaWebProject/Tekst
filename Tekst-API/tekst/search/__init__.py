import asyncio

from datetime import datetime
from time import process_time
from typing import Any
from uuid import uuid4

from beanie.operators import Eq, In
from elasticsearch import Elasticsearch

from tekst import locks
from tekst.config import TekstConfig, get_config
from tekst.logging import log
from tekst.models.common import PydanticObjectId
from tekst.models.content import ContentBaseDocument
from tekst.models.location import LocationDocument
from tekst.models.resource import ResourceBaseDocument
from tekst.models.search import (
    AdvancedSearchSettings,
    GeneralSearchSettings,
    IndexInfoResponse,
    QuickSearchSettings,
    SearchResults,
)
from tekst.models.text import TextDocument
from tekst.models.user import UserRead
from tekst.resources import AnyResourceSearchQuery, resource_types_mgr
from tekst.search.templates import (
    IDX_ALIAS,
    IDX_NAME_PATTERN,
    IDX_NAME_PATTERN_ANY,
    IDX_NAME_PREFIX,
    IDX_TEMPLATE,
    IDX_TEMPLATE_NAME,
    IDX_TEMPLATE_NAME_PATTERN,
    SORTING_PRESETS,
    get_source_includes,
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
                ).index_doc_props(),
            }
        resp = client.indices.put_mapping(
            index=new_index_name,
            body={"properties": {"resources": {"properties": extra_properties}}},
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


async def _populate_index(index_name: str) -> None:
    client: Elasticsearch = await _get_es_client()
    bulk_index_max_size = 1000
    bulk_index_body = []
    errors = False

    # get all resources and map them from their ID
    # so we can easily access their title later
    resources = {
        res.id: res
        for res in await ResourceBaseDocument.find_all(
            with_children=True,
            lazy_parse=True,
        ).to_list()
    }

    for text in await TextDocument.find_all(lazy_parse=True).to_list():
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
                "resources": {},
            }

            # add data for each content for this location
            for content in await ContentBaseDocument.find(
                Eq(ContentBaseDocument.location_id, location.id),
                with_children=True,
            ).to_list():
                content_index_doc = resource_types_mgr.get(
                    content.resource_type
                ).index_doc_data(content)
                # add resource title to index document
                content_index_doc["resource_title"] = resources[
                    content.resource_id
                ].title
                # add resource content document to location index document
                location_index_doc["resources"][str(content.resource_id)] = (
                    content_index_doc
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
            log.debug(
                f"Indexing finished for '{text.title}' in "
                f"{(process_time() - start_time):.2f} seconds."
            )
        errors = False


def _bulk_index(client: Elasticsearch, reqest_body: dict[str, Any]) -> bool:
    resp = client.bulk(body=reqest_body)
    return bool(resp) and not resp.get("errors", False)


def _get_index_creation_time() -> datetime:
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
        last_indexed=_get_index_creation_time(),
    )


async def _get_target_resource_ids(
    *,
    user: UserRead | None = None,
    text_ids: list[PydanticObjectId] | None = None,
    resource_types: list[str] | None = None,
) -> list[str]:
    """
    Returns a contrained list of IDs for the target resources for a search request,
    based on the requesting user's permissions, target texts and resource types.
    """
    return [
        str(res.id)
        for res in await ResourceBaseDocument.find(
            In(ResourceBaseDocument.text_id, text_ids) if text_ids else {},
            In(ResourceBaseDocument.resource_type, resource_types)
            if resource_types
            else {},
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
        resource_types=["plainText", "richText"],  # contrain target resource types
    )

    # compose a list of target index fields based on the resources to search:
    field_pattern_suffix = ".*.strict" if settings_general.strict else ".*"
    fields = [
        f"resources.{res_id}{field_pattern_suffix}" for res_id in target_resource_ids
    ]
    source_includes = [
        f"resources.{res_id}.resource_title" for res_id in target_resource_ids
    ]

    # compose the query
    es_query = {
        "bool": {
            "must": [
                {
                    "terms": {
                        "text_id": [str(text_id) for text_id in settings_quick.texts],
                    }
                }
                if settings_quick.texts
                else None,
                {
                    "simple_query_string": {
                        "query": query_string or "*",  # fall back to '*' if empty
                        "fields": fields,
                        "default_operator": settings_quick.default_operator,
                        "analyze_wildcard": True,
                    }
                },
            ],
        }
    }

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
            source={"includes": get_source_includes(source_includes)},
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
    source_includes = [
        f"resources.{res_id}.resource_title" for res_id in target_resource_ids
    ]
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
            source={"includes": get_source_includes(source_includes)},
        ),
        index_creation_time=_get_index_creation_time(),
    )
