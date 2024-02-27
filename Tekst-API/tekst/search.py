from time import sleep

from elasticsearch import Elasticsearch

from tekst.config import TekstConfig, get_config
from tekst.logging import log


_es_client: Elasticsearch | None = None


def init_es_client(es_uri: str | None = None) -> Elasticsearch:
    global _es_client
    if _es_client is None:
        log.info("Initializing Elasticsearch client...")
        cfg: TekstConfig = get_config()
        _es_client = Elasticsearch(es_uri or cfg.es_uri)
        for i in range(cfg.es_init_timeout_s):
            if _es_client.ping():
                break
            if i % 10 == 0:
                log.debug(
                    "Waiting for Elasticsearch service "
                    f"({i}/{cfg.es_init_timeout_s} seconds)..."
                )
            sleep(1)
        else:
            raise RuntimeError("Timed out waiting for Elasticsearch service!")
    return _es_client


def _get_es_client(es_uri: str | None = None) -> Elasticsearch:
    return init_es_client(es_uri)


def close() -> None:
    global _es_client
    if _es_client is not None:
        _es_client.close()
        _es_client = None
