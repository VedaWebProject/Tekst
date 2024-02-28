from time import sleep
from uuid import uuid4

from elasticsearch import Elasticsearch
from beanie.operators import Eq

from tekst.config import TekstConfig, get_config
from tekst.logging import log
from tekst.models.location import LocationDocument
from tekst.models.resource import ResourceBaseDocument
from tekst.models.content import ContentBaseDocument


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
            sleep(1)
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
        template=_get_index_template(),
        priority=500,
    )


def _get_index_template() -> dict:
    return {
        "mappings": {
            "properties": {
                "text_id": {"type": "keyword"},
                "level": {"type": "short"},
                "position": {"type": "integer"},
            }
        }
    }


async def create_index(*, overwrite_existing_index: bool = True) -> None:
    client: Elasticsearch = await _get_es_client()
    # check if index already exists
    if client.indices.exists(index=_IDX_NAME_PATTERN_ANY):
        if overwrite_existing_index:
            log.warning("The new index will overwrite the existing one.")
        else:
            log.warning("An index already exists. Aborting index creation.")
            return
    new_index_name = _IDX_NAME_PREFIX + uuid4().hex
    log.debug(f'Creating index "{new_index_name}"...')
    # create index (index template will be applied!)
    client.indices.create(
        index=new_index_name,
        aliases={_IDX_ALIAS: {}},
        mappings={
            "properties": {
                "bar": {"type": "keyword"},
            }
        },
    )
    # populate newly created index
    await _populate_index(new_index_name)
    # delete all other/old indices matching the used index naming pattern
    client.indices.delete(
        index=[
            idx
            for idx in client.indices.get(index=_IDX_NAME_PATTERN_ANY)
            if idx != new_index_name
        ]
    )


async def _populate_index(name: str) -> None:
    client: Elasticsearch = await _get_es_client()
    log.debug(f'Populating index "{name}"...')

    # extend index mappings adding one extra field for each existing public resource
    resources = {
        res.id: res
        for res in await ResourceBaseDocument.find(
            Eq(ResourceBaseDocument.public, True),
            with_children=True,
            lazy_parse=True,
        ).to_list()
    }
    # TODO ...

    # create one index document per location,
    # with data from resource contents for each respective location
    for location in await LocationDocument.find_all(lazy_parse=True).to_list():
        for content in await ContentBaseDocument.find(
            Eq(ContentBaseDocument.location_id, location.id),
            with_children=True,
            lazy_parse=True,
        ).to_list():
            # TODO!
            log.debug(content.text)
