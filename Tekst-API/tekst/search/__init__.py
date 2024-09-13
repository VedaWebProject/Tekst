import asyncio

from datetime import datetime
from typing import Any
from uuid import uuid4

from beanie import PydanticObjectId
from beanie.operators import Eq, In
from elasticsearch import Elasticsearch

from tekst import tasks
from tekst.config import TekstConfig, get_config
from tekst.logs import log, log_op_end, log_op_start
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
from tekst.state import update_state


_cfg: TekstConfig = get_config()
_es_client: Elasticsearch | None = None


async def _wait_for_es() -> bool:
    global _es_client
    if _es_client is not None:
        for i in range(_cfg.es.timeout_init_s):
            if _es_client.ping():
                return True
            if i % 10 == 0:
                log.debug(
                    f"Waiting for Elasticsearch service at {_cfg.es.uri} "
                    f"({i}/{_cfg.es.timeout_init_s} seconds)..."
                )
                await asyncio.sleep(1)
        else:
            log.critical(f"Could not connect to Elasticsearch at {_cfg.es.uri}!")
            return False
    else:
        await init_es_client()


async def init_es_client() -> Elasticsearch:
    global _es_client
    if _es_client is None:
        log.info("Initializing Elasticsearch client...")
        _es_client = Elasticsearch(_cfg.es.uri, timeout=_cfg.es.timeout_general_s)
        if not await _wait_for_es():
            raise RuntimeError("Waiting for Elasticsearch client exceeded timeout!")
    return _es_client


async def _get_es_client() -> Elasticsearch:
    return await init_es_client()


def get_es_status() -> dict[str, Any] | None:
    global _es_client
    return _es_client.info() if _es_client else None


def close() -> None:
    global _es_client
    if _es_client is not None:
        _es_client.close()
        _es_client = None


async def _setup_index_templates() -> None:
    """This is called by the setup routine and when re-indexing"""
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


async def create_indices_task(force: bool = False) -> dict[str, float]:
    op_id = log_op_start("Create search indices", level="INFO")
    await _wait_for_es()
    await _setup_index_templates()

    # get existing search indices
    client: Elasticsearch = await _get_es_client()
    old_idxs = [idx for idx in client.indices.get(index=IDX_NAME_PATTERN_ANY)]
    utd_idxs = []  # list of indices that are still up to date

    for text in await TextDocument.find_all().to_list():
        # get names of existing indices for this text
        old_txt_idxs = [idx for idx in old_idxs if str(text.id) in idx]

        # check if indexing is necessary and if not, remember the index that's still
        # in use for this text, then continue with the next text
        if old_txt_idxs and (
            text.index_created_at is not None
            and text.contents_changed_at < text.index_created_at
        ):
            # indexing is NOT necessary
            if force:
                log.debug(f"Index for '{text.title}' is up to date. Forcing re-index.")
            else:
                log.debug(f"Indexing is not necessary for text '{text.title}'.")
                utd_idxs.extend(old_txt_idxs)
                continue

        # generate new index name
        new_idx_name = f"{IDX_NAME_PREFIX}{text.slug}_{text.id}_{str(uuid4().hex)}"

        # create index (index template will be applied!)
        client.indices.create(
            index=new_idx_name,
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
            index=new_idx_name,
            body={"properties": {"resources": {"properties": extra_properties}}},
        )
        if not resp or not resp.get("acknowledged"):
            raise RuntimeError("Failed to extend index mappings!")

        # populate newly created index
        populate_op_id = log_op_start(f"Index resources for text '{text.title}'")
        try:
            await _populate_index(new_idx_name, text)
        except Exception as e:
            log_op_end(populate_op_id, failed=True, failed_msg=str(e))

        utd_idxs.append(new_idx_name)  # mark created index as "up to date"
        await text.index_updated_hook()  # update indexing time for text
        log_op_end(populate_op_id)

    # delete indices that are no longer in use
    to_delete = [idx for idx in old_idxs if idx not in utd_idxs]
    if to_delete:
        client.indices.delete(index=to_delete)

    # perform initial bogus search on all existing indices (to initialize index stats)
    client.search(
        index=IDX_ALIAS,
        query={"match_all": {}},
        timeout=_cfg.es.timeout_search_s,
    )

    # update last global indexing time
    await update_state(indices_updated_at=datetime.utcnow())

    return {
        "took": round(log_op_end(op_id), 2),
    }


async def create_indices(
    *,
    user: UserRead | None = None,
    force: bool = False,
) -> tasks.TaskDocument:
    log.info("Creating search indices ...")
    # create index task
    return await tasks.create_task(
        create_indices_task,
        tasks.TaskType.INDICES_CREATE_UPDATE,
        user_id=user.id if user else None,
        task_kwargs={
            "force": force,
        },
    )


async def _populate_index(
    index_name: str,
    text: TextDocument,
) -> None:
    if text is None:
        raise ValueError("text is None!")
    client: Elasticsearch = await _get_es_client()
    bulk_index_max_size = 500
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

    if errors:
        raise RuntimeError(f"Failed to index some documents for text '{text.title}'.")


def _bulk_index(
    client: Elasticsearch,
    reqest_body: dict[str, Any],
) -> bool:
    resp = client.bulk(body=reqest_body)
    log.debug(f"Bulk index response took: {resp.get('took', '???')}ms")
    return bool(resp) and not resp.get("errors", False)


async def _get_mapped_fields_count(index: str) -> int:
    client: Elasticsearch = await _get_es_client()
    return len(
        client.field_caps(
            index=index,
            fields="*",
            human=True,
            include_empty_fields=True,
            include_unmapped=False,
        )["fields"]
    )


async def _get_index_stats(index: str) -> dict[str, Any]:
    client: Elasticsearch = await _get_es_client()
    data = client.indices.stats(
        index=IDX_ALIAS,
        human=True,
    ).body["indices"][index]["total"]
    return {
        "documents": data["docs"]["count"],
        "size": data["store"]["size"],
        "searches": data["search"]["query_total"],
    }


async def get_indices_info() -> list[IndexInfo]:
    client: Elasticsearch = await _get_es_client()
    idx_names = client.indices.get_alias(index=IDX_ALIAS)
    data = []
    try:
        for idx_name in idx_names:
            text_id = idx_name.split("_")[-2]
            text = await TextDocument.get(text_id)
            data.append(
                {
                    "text_id": text_id if text else None,
                    "created_at": text.index_created_at if text else None,
                    "fields": await _get_mapped_fields_count(idx_name),
                    "up_to_date": text.index_created_at > text.contents_changed_at,
                    **await _get_index_stats(idx_name),
                }
            )
        return [IndexInfo(**idx_info) for idx_info in data]
    except Exception:
        log.error("Error getting/processing indices info.")
        return []


async def _get_target_resources(
    *,
    user: UserRead | None = None,
    text_ids: list[PydanticObjectId] | None = None,
    resource_types: list[str] | None = None,
) -> list[ResourceBaseDocument]:
    """
    Returns a constrained list of target resources for a search request,
    based on the requesting user's permissions, target texts and resource types.
    """
    return await ResourceBaseDocument.find(
        In(ResourceBaseDocument.text_id, text_ids) if text_ids else {},
        In(ResourceBaseDocument.resource_type, resource_types)
        if resource_types
        else {},
        Eq(ResourceBaseDocument.public, True),
        await ResourceBaseDocument.access_conditions_read(user),
        with_children=True,
    ).to_list()


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
        for res in await _get_target_resources(
            user=user,
            text_ids=text_ids,
            resource_types=resource_types,
        )
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
                "fields": [{field: {}} for field in fields],
            },
            from_=settings_general.pagination.es_from(),
            size=settings_general.pagination.es_size(),
            track_scores=True,
            sort=SORTING_PRESETS.get(settings_general.sorting_preset),
            source={"includes": QUERY_SOURCE_INCLUDES},
            timeout=_cfg.es.timeout_search_s,
        ),
    )


async def search_advanced(
    user: UserRead | None,
    queries: list[AnyResourceSearchQuery],
    settings_general: GeneralSearchSettings = GeneralSearchSettings(),
    settings_advanced: AdvancedSearchSettings = AdvancedSearchSettings(),
) -> SearchResults:
    client: Elasticsearch = _es_client
    target_resources = {
        str(res.id): res for res in await _get_target_resources(user=user)
    }

    # construct all the sub-queries
    sub_queries_must = []
    sub_queries_should = []
    sub_queries_must_not = []
    highlights_generators = {}
    for q in queries:
        if str(q.common.resource_id) not in target_resources:
            continue
        res_type = resource_types_mgr.get(q.resource_type_specific.resource_type)
        txt_id = str(target_resources[str(q.common.resource_id)].text_id)
        res_es_query = {
            "bool": {
                "must": [
                    # actual, resource-specific queries
                    *res_type.es_queries(
                        query=q,
                        strict=settings_general.strict,
                    ),
                    # ensure the query is run against the correct index
                    {"term": {"_index": f"*_{txt_id}_*"}},
                ]
            }
        }
        # collect highlights generators for custom, resource-type-specific highlighting
        if (hl_gen := res_type.highlights_generator()) is not None:
            highlights_generators[str(q.common.resource_id)] = hl_gen
        # add individual sub-queries to the root query based on the selected occurrence
        if q.common.occurrence == "must":
            sub_queries_must.append(res_es_query)
        elif q.common.occurrence == "not":
            sub_queries_must_not.append(res_es_query)
        else:
            sub_queries_should.append(res_es_query)

    # compose the overall compound query
    es_query = {
        "bool": dict(
            **({"must": sub_queries_must} if sub_queries_must else {}),
            **({"should": sub_queries_should} if sub_queries_should else {}),
            **({"must_not": sub_queries_must_not} if sub_queries_must_not else {}),
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
            timeout=_cfg.es.timeout_search_s,
        ),
        highlights_generators=highlights_generators,
    )
