import asyncio

from uuid import uuid4

from beanie.operators import Eq
from elasticsearch import Elasticsearch

from tekst import locks
from tekst.config import TekstConfig, get_config
from tekst.logging import log
from tekst.models.content import ContentBaseDocument
from tekst.models.location import LocationDocument
from tekst.models.resource import ResourceBaseDocument
from tekst.resources import resource_types_mgr
from tekst.search.responses import IndexInfoResponse
from tekst.search.template import INDEX_TEMPLATE


_cfg: TekstConfig = get_config()
_es_client: Elasticsearch | None = None

_IDX_NAME_CORE = "locations"
_IDX_NAME_PREFIX = f"{_cfg.es_prefix}_{_IDX_NAME_CORE}_"
_IDX_NAME_PATTERN = f"{_IDX_NAME_PREFIX}*"
_IDX_NAME_PATTERN_ANY = f"*_{_IDX_NAME_CORE}_*"
_IDX_ALIAS = f"{_cfg.es_prefix}_{_IDX_NAME_CORE}"
_IDX_TEMPLATE_NAME = f"{_cfg.es_prefix}_{_IDX_NAME_CORE}_template"
_IDX_TEMPLATE_NAME_PATTERN = f"*_{_IDX_NAME_CORE}_template"


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
        f'Setting up index template "{_IDX_TEMPLATE_NAME}" '
        f'for pattern "{_IDX_NAME_PATTERN}"...'
    )
    # delete possible existing index templates that could cause conflicts
    if client.indices.exists_index_template(name=_IDX_TEMPLATE_NAME_PATTERN):
        client.indices.delete_index_template(name=_IDX_TEMPLATE_NAME_PATTERN)
    # create index template
    client.indices.put_index_template(
        name=_IDX_TEMPLATE_NAME,
        index_patterns=_IDX_NAME_PATTERN,
        template=INDEX_TEMPLATE,
        priority=500,
    )


async def create_index(*, overwrite_existing_index: bool = True) -> None:
    # prepare
    new_index_name = _IDX_NAME_PREFIX + uuid4().hex
    log.info(f'Creating index "{new_index_name}"...')

    # check and set lock
    if await locks.is_locked(locks.LockKey.INDEX_CREATE_UPDATE):
        log.warning(
            'Aborting index creation because of active lock "index_create_update"'
        )
        return
    else:
        await locks.lock(locks.LockKey.INDEX_CREATE_UPDATE)

    await asyncio.sleep(10)

    # get existing search indices
    client: Elasticsearch = await _get_es_client()
    existing_indices = [idx for idx in client.indices.get(index=_IDX_NAME_PATTERN_ANY)]
    if existing_indices:
        if overwrite_existing_index:
            log.debug("The new index will overwrite the existing one...")
        else:
            log.warning("An index already exists. Aborting index creation.")
            return
    # create new index
    # create index (index template will be applied!)
    client.indices.create(
        index=new_index_name,
        aliases={_IDX_ALIAS: {}},
    )
    # populate newly created index
    await _populate_index(new_index_name)
    # delete all other/old indices matching the used index naming pattern
    if existing_indices:
        client.indices.delete(index=existing_indices)
    # realse lock
    await locks.release(locks.LockKey.INDEX_CREATE_UPDATE)


async def _populate_index(index_name: str) -> None:
    client: Elasticsearch = await _get_es_client()
    log.debug(f'Populating index "{index_name}"...')

    # extend index mappings adding one extra field for each existing public resource
    extra_properties = {}
    for res in await ResourceBaseDocument.find(
        Eq(ResourceBaseDocument.public, True),
        with_children=True,
        lazy_parse=True,
    ).to_list():
        extra_properties[str(res.id)] = {
            "properties": resource_types_mgr.get(
                res.resource_type
            ).index_doc_properties()
        }
    resp = client.indices.put_mapping(
        index=index_name,
        body={"properties": extra_properties},
    )
    if not resp or not resp.get("acknowledged"):
        raise RuntimeError("Failed to extend index mappings!")

    # create one index document per location,
    # with data from resource contents for each respective location
    bulk_body = []
    for location in await LocationDocument.find_all(lazy_parse=True).to_list():
        location_index_doc = {
            "text_id": str(location.text_id),
            "level": location.level,
            "position": location.position,
        }
        for content in await ContentBaseDocument.find(
            Eq(ContentBaseDocument.location_id, location.id),
            with_children=True,
        ).to_list():
            location_index_doc[str(content.resource_id)] = resource_types_mgr.get(
                content.resource_type
            ).index_doc_data(content)

        bulk_body.append({"index": {"_index": index_name, "_id": str(location.id)}})
        bulk_body.append(location_index_doc)

    # bulk index
    resp = client.bulk(body=bulk_body)
    if resp and not resp.get("errors", False):
        log.debug(
            f'Successfully populated "{index_name}" (took {resp["took"]/1000} seconds).'
        )
    else:
        log.error(f"There were errors populating index '{index_name}'.")
        raise RuntimeError("Failed to populate index without errors!")


async def get_index_info():
    client: Elasticsearch = await _get_es_client()
    info = client.indices.stats(index=_IDX_ALIAS, human=True).body
    index_info = list(info["indices"].values())[0]["total"]
    return IndexInfoResponse(
        documents=index_info["docs"]["count"],
        size=index_info["store"]["size"],
        searches=index_info["search"]["query_total"],
    )
