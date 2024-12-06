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
from tekst.state import get_state, update_state


_cfg: TekstConfig = get_config()
_es_client: Elasticsearch | None = None


async def _wait_for_es() -> bool:
    global _es_client
    if _es_client is not None:
        for i in range(_cfg.es.timeout_init_s):
            if _es_client.ping():
                return True
            if i % 10 == 0:  # pragma: no cover
                log.debug(
                    f"Waiting for Elasticsearch service at {_cfg.es.uri} "
                    f"({i}/{_cfg.es.timeout_init_s} seconds)..."
                )
                await asyncio.sleep(1)
        else:  # pragma: no cover
            log.critical(f"Could not connect to Elasticsearch at {_cfg.es.uri}!")
            return False
    else:  # pragma: no cover
        await init_es_client()


async def init_es_client() -> Elasticsearch:
    global _es_client
    if _es_client is None:
        log.info("Initializing Elasticsearch client...")
        _es_client = Elasticsearch(
            _cfg.es.uri,
            request_timeout=_cfg.es.timeout_general_s,
        )
        if not await _wait_for_es():  # pragma: no cover
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
    state = await get_state()

    # get existing search indices
    client: Elasticsearch = await _get_es_client()
    old_idxs = [idx for idx in client.indices.get(index=IDX_NAME_PATTERN_ANY)]
    utd_idxs = []  # list of indices that are still up to date

    for text in await TextDocument.find_all().to_list():
        # get names of existing indices for this text
        old_txt_idxs = [idx for idx in old_idxs if str(text.id) in idx]

        # check if indexing is necessary and if not, remember the index that's still
        # in use for this text, then continue with the next text
        if old_txt_idxs and text.index_utd:
            # indexing is NOT necessary
            if force:
                log.debug(f"Index for '{text.title}' is up to date, forcing re-index.")
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
        only_public_res = (
            {}
            if state.index_unpublished_resources
            else Eq(ResourceBaseDocument.public, True)
        )
        for res in await ResourceBaseDocument.find(
            ResourceBaseDocument.text_id == text.id,
            only_public_res,
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
        if not resp or not resp.get("acknowledged"):  # pragma: no cover
            raise RuntimeError("Failed to extend index mappings!")

        # populate newly created index
        populate_op_id = log_op_start(f"Index resources for text '{text.title}'")
        try:
            await _populate_index(new_idx_name, text)
        except Exception as e:  # pragma: no cover
            log_op_end(populate_op_id, failed=True, failed_msg=str(e))

        utd_idxs.append(new_idx_name)  # mark created index as "up to date"
        text.index_utd = True
        await text.replace()
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
    client: Elasticsearch = await _get_es_client()

    def _bulk_index(
        reqest_body: dict[str, Any],
        req_no: int = None,
    ) -> bool:
        resp = client.bulk(
            body=reqest_body,
            timeout=f"{_cfg.es.timeout_general_s}s",
            refresh="wait_for",
        )
        req_no_str = f"#{req_no} " if req_no is not None else ""
        log.debug(f"Bulk index request {req_no_str}took: {resp.get('took', '???')}ms")
        return bool(resp) and not resp.get("errors", False)

    bulk_index_max_size = 200
    bulk_index_body = []
    errors = False
    state = await get_state()
    only_public_res = (
        {}
        if state.index_unpublished_resources
        else Eq(ResourceBaseDocument.public, True)
    )
    target_resource_ids = [
        res.id
        for res in await ResourceBaseDocument.find(
            ResourceBaseDocument.text_id == text.id,
            only_public_res,
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
    if not stack:  # pragma: no cover
        return
    bulk_req_count = 0

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
        if len(bulk_index_body) / 2 >= bulk_index_max_size:  # pragma: no cover
            bulk_req_count += 1
            errors |= not _bulk_index(bulk_index_body, bulk_req_count)
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
    errors |= not _bulk_index(bulk_index_body, bulk_req_count + 1)
    bulk_index_body = []

    if errors:  # pragma: no cover
        raise RuntimeError(f"Failed to index some documents for text '{text.title}'.")


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
                    "fields": await _get_mapped_fields_count(idx_name),
                    "up_to_date": text.index_utd,
                    **await _get_index_stats(idx_name),
                }
            )
        return [IndexInfo(**idx_info) for idx_info in data]
    except Exception as e:  # pragma: no cover
        log.error(f"Error getting/processing indices info: {str(e)}")
        return []


async def _get_target_resources(
    *,
    user: UserRead | None = None,
    text_ids: list[PydanticObjectId] | None = None,
) -> dict[str, ResourceBaseDocument]:
    """
    Returns a constrained list of target resources for a search request,
    based on the requesting user's permissions, target texts and resource types.
    """
    state = await get_state()
    only_public_res = (
        {}
        if state.index_unpublished_resources
        else Eq(ResourceBaseDocument.public, True)
    )
    return {
        str(res.id): res
        for res in await ResourceBaseDocument.find(
            In(ResourceBaseDocument.text_id, text_ids) if text_ids else {},
            only_public_res,
            await ResourceBaseDocument.access_conditions_read(user),
            with_children=True,
        ).to_list()
    }


async def search_quick(
    user: UserRead | None,
    query_string: str | None = None,
    settings_general: GeneralSearchSettings = GeneralSearchSettings(),
    settings_quick: QuickSearchSettings = QuickSearchSettings(),
) -> SearchResults:
    client: Elasticsearch = _es_client
    target_resources = await _get_target_resources(
        user=user,
        text_ids=settings_quick.texts,  # constrain target texts
    )

    # compose a list of target index fields based on the resources to search:
    field_pattern_suffix = ".strict" if settings_general.strict else ""
    fields = []
    for res_id, res in target_resources.items():
        if res.config.common.quick_searchable:
            for field in res.quick_search_fields():
                fields.append(f"resources.{res_id}.{field}{field_pattern_suffix}")

    # compose the query
    if not settings_quick.regexp or not query_string:
        es_query = {
            "simple_query_string": {
                "query": query_string or "*",  # fall back to '*' if empty
                "fields": fields,
                "default_operator": settings_quick.default_operator,
                "analyze_wildcard": True,
            }
        }
    else:
        es_query = {
            "bool": {
                "should": [
                    {
                        "regexp": {
                            field: {
                                "value": query_string,
                                "flags": "ALL",
                                "case_insensitive": True,
                            }
                        }
                    }
                    for field in fields
                ]
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
    target_resources = await _get_target_resources(user=user)

    # construct all the sub-queries
    sub_queries_must = []
    sub_queries_should = []
    sub_queries_must_not = []
    highlights_generators = {}

    # for each query block in the advanced search request...
    for query in queries:
        if str(query.common.resource_id) not in target_resources:  # pragma: no cover
            continue
        res_type = resource_types_mgr.get(query.resource_type_specific.resource_type)
        txt_id = str(target_resources[str(query.common.resource_id)].text_id)

        # construct resource type-specific query
        res_es_query = {
            "bool": {
                "must": [
                    # actual, resource-specific queries
                    *res_type.es_queries(
                        query=query,
                        strict=settings_general.strict,
                    ),
                    # ensure the query is run against the correct index
                    {"term": {"_index": f"*_{txt_id}_*"}},
                ]
            }
        }

        # collect highlights generators for custom, resource-type-specific highlighting
        if (hl_gen := res_type.highlights_generator()) is not None:
            highlights_generators[str(query.common.resource_id)] = hl_gen

        # add individual sub-queries to the root query based on the selected occurrence
        if query.common.occurrence == "must":
            sub_queries_must.append(res_es_query)
        elif query.common.occurrence == "not":
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
    if not es_query.get("bool"):  # pragma: no cover
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


async def set_index_ood(
    text_id: PydanticObjectId,
    *,
    by_public_resource: bool = True,
):
    print(by_public_resource)
    """Set the index_utd flag for this text, considering the given parameters"""
    if by_public_resource or (await get_state()).index_unpublished_resources:
        print(text_id)
        text = await TextDocument.get(text_id)
        text.index_utd = False
        await text.replace()
