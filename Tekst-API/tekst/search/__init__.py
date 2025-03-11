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
from tekst.search.utils import (
    add_analysis_settings,
    add_mappings,
    quick_qstr_query,
    quick_regexp_query,
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
        create=True,
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
        if old_txt_idxs and text.index_utd:
            # indexing is NOT necessary
            if force:
                log.debug(f"Index for '{text.title}' is up to date, forcing re-index.")
            else:
                log.debug(f"Indexing is not necessary for text '{text.title}'.")
                utd_idxs.extend(old_txt_idxs)
                continue

        # collect special mappings and analysis settings for each target resource
        mappings = {}
        analysis = {}
        for resource in await _get_resources(
            text_ids=[text.id],
            check_read_access=False,
        ):
            # add resource type-specific mappings
            add_mappings(
                for_resource=resource,
                to_mappings=mappings,
            )
            # add resource-specific analysis settings
            add_analysis_settings(
                for_resource=resource,
                to_analysis=analysis,
            )

        # create index (index template will be applied!)
        new_idx_name = f"{IDX_NAME_PREFIX}{text.slug}_{text.id}_{str(uuid4().hex)}"
        client.indices.create(
            index=new_idx_name,
            aliases={IDX_ALIAS: {}},
            mappings={"properties": {"resources": {"properties": mappings}}},
            settings={"index": {"analysis": analysis}},
        )

        # populate newly created index
        populate_op_id = log_op_start(f"Index resources for text '{text.title}'")
        try:
            await _populate_index(new_idx_name, text)
        except Exception as e:  # pragma: no cover
            log_op_end(populate_op_id, failed=True, failed_msg=str(e))
            client.indices.delete(index=new_idx_name)  # delete broken/unfinished index
            raise e

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
        target_id=tasks.TaskType.INDICES_CREATE_UPDATE.value,
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
    ) -> None:
        resp = client.bulk(
            body=reqest_body,
            timeout=f"{_cfg.es.timeout_general_s}s",
            refresh="wait_for",
        )
        if resp.get("errors", False):  # pragma: no cover
            for error in resp["items"]:
                log.error(str(error))
            raise RuntimeError(f"Failed to index documents for text '{text.title}'.")
        req_no_str = f"#{req_no} " if req_no is not None else ""
        log.debug(f"Bulk index request {req_no_str}took: {resp.get('took', '???')}ms")

    bulk_index_max_size = 200
    bulk_index_body = []

    target_resource_ids = [
        res.id
        for res in await _get_resources(
            text_ids=[text.id],
            check_read_access=False,
        )
    ]

    # Initialize stack with all level 0 locations (sorted) of the current text.
    # Each item on the stack is a tuple containing
    # (0) the location itself as LocationDocument
    # (1) location labels from the root level up to the current location as list[str],
    stack = [
        (location, [location.label])
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

    # cache mapping of location IDs to index doc contents
    # for re-use in child location index docs
    parent_idx_contents: dict[str, dict[str, Any]] = {}

    # keep track of number of bulk index requests
    bulk_req_count = 0

    while len(stack):
        loc, labels = stack.pop(0)
        loc_id_str = str(loc.id)

        # create index document for this location
        loc_idx_doc = {
            "label": loc.label,
            "full_label": text.loc_delim.join(labels),
            "text_id": str(loc.text_id),
            "level": loc.level,
            "position": loc.position,
            "default_level": loc.level == text.default_level,
            "resources": {},
        }

        # add parent contents
        if str(loc.parent_id) in parent_idx_contents:
            loc_idx_doc["resources"].update(parent_idx_contents[str(loc.parent_id)])

        # add data for each content for this location
        for content in await ContentBaseDocument.find(
            Eq(ContentBaseDocument.location_id, loc.id),
            In(ContentBaseDocument.resource_id, target_resource_ids),
            with_children=True,
        ).to_list():
            # add resource level and content to location index document
            loc_idx_doc["resources"][str(content.resource_id)] = resource_types_mgr.get(
                content.resource_type
            ).index_doc(content=content, native=True)

        # add location contents to cached parent contents
        # (only if the current location's level is < max level,
        # otherwise there won't be any child locations we need that content for)
        # but set "native" to False, as these contents aren't native to child locations
        if loc.level < len(text.levels) - 1:
            parent_idx_contents[loc_id_str] = {}
            for res_id in loc_idx_doc["resources"]:
                parent_idx_contents[loc_id_str][res_id] = {
                    **loc_idx_doc["resources"][res_id],
                    "native": False,
                }

        # add index document to bulk index request body
        bulk_index_body.append({"index": {"_index": index_name, "_id": loc_id_str}})
        bulk_index_body.append(loc_idx_doc)

        # check bulk request body size, fire bulk request if necessary
        if len(bulk_index_body) / 2 >= bulk_index_max_size:  # pragma: no cover
            bulk_req_count += 1
            _bulk_index(bulk_index_body, bulk_req_count)
            bulk_index_body = []

        # add all child locations to the processing stack
        stack.extend(
            [
                (
                    child,  # the target location document
                    labels + [child.label],  # all the labels
                )
                for child in await LocationDocument.find(
                    LocationDocument.parent_id == loc.id,
                )
                .sort(+LocationDocument.position)
                .to_list()
            ]
        )

    # index the remaining documents
    _bulk_index(bulk_index_body, bulk_req_count + 1)
    bulk_index_body = []


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


async def _get_resources(
    *,
    user: UserRead | None = None,
    text_ids: list[PydanticObjectId] | None = None,
    check_read_access: bool = True,
) -> list[ResourceBaseDocument]:
    """
    Returns a constrained list of target resources for a search request,
    based on the requesting user's permissions, target texts and publication status.
    """
    state = await get_state()
    # prepare DB query restrictions
    texts_restr = In(ResourceBaseDocument.text_id, text_ids) if text_ids else {}
    publication_restr = (
        Eq(ResourceBaseDocument.public, True)
        if not state.index_unpublished_resources
        else {}
    )
    access_restr = (
        await ResourceBaseDocument.access_conditions_read(user)
        if check_read_access
        else {}
    )
    return await ResourceBaseDocument.find(
        texts_restr,
        publication_restr,
        access_restr,
        with_children=True,
    ).to_list()


async def search_quick(
    user: UserRead | None,
    user_query: str | None = None,
    settings_general: GeneralSearchSettings = GeneralSearchSettings(),
    settings_quick: QuickSearchSettings = QuickSearchSettings(),
) -> SearchResults:
    client: Elasticsearch = _es_client

    # get (pre-)selection of target resources
    target_resources = await _get_resources(
        user=user,
        text_ids=settings_quick.texts,  # constrain target texts
    )

    # remove resources that aren't quick-searchable
    target_resources = [
        res for res in target_resources if res.config.common.searchable_quick
    ]

    # compose a list of target index fields based on the resources to search:
    field_pattern_suffix = ".strict" if settings_general.strict else ""
    fields = []  # list of tuples of (res_id, field_path)
    for res in target_resources:
        for field in res.quick_search_fields():
            fields.append(
                (
                    str(res.id),
                    f"resources.{str(res.id)}.{field}{field_pattern_suffix}",
                )
            )

    # create ES content query
    if not settings_quick.regexp or not user_query:
        # use q query string query
        es_query = quick_qstr_query(
            user_query,
            fields,
            default_op=settings_quick.default_operator,
            inherited_contents=settings_quick.inherited_contents,
        )
    else:
        # use regexp query
        es_query = quick_regexp_query(
            user_query,
            fields,
            inherited_contents=settings_quick.inherited_contents,
        )

    # if "all_levels" is set to `False`, modify ES query to
    # only find locations on their text's default level
    if not settings_quick.all_levels:
        # wrap in new query
        es_query = {
            "bool": {
                "must": [
                    es_query,  # original content query from above
                ],
                "filter": [
                    {
                        "term": {
                            "default_level": {
                                "value": True,
                            }
                        }
                    }
                ],
            }
        }

    log.debug(f"Running ES query: {es_query}")

    # perform the search
    return SearchResults.from_es_results(
        results=client.search(
            index=IDX_ALIAS,
            query=es_query,
            highlight={
                "fields": [{field_path: {}} for _, field_path in fields],
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
    accessible_resources_by_id = {
        str(res.id): res for res in await _get_resources(user=user)
    }

    # construct all the sub-queries
    sub_queries_must = []
    sub_queries_should = []
    sub_queries_must_not = []
    highlights_generators = {}

    # for each query block in the advanced search request...
    for query in queries:
        res_id = str(query.common.resource_id)
        res_doc = accessible_resources_by_id.get(res_id)
        if not res_doc or res_doc.config.common.searchable_adv is False:
            continue  # pragma: no cover
        res_type = resource_types_mgr.get(query.resource_type_specific.resource_type)
        txt_id = str(res_doc.text_id)

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
            highlights_generators[res_id] = hl_gen

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
    """Set the index_utd flag for this text, considering the given parameters"""
    if by_public_resource or (await get_state()).index_unpublished_resources:
        text = await TextDocument.get(text_id)
        text.index_utd = False
        await text.replace()
