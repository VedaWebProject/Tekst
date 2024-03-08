from tekst.config import TekstConfig, get_config


_cfg: TekstConfig = get_config()

IDX_NAME_CORE = "locations"
IDX_NAME_PREFIX = f"{_cfg.es_prefix}_{IDX_NAME_CORE}_"
IDX_NAME_PATTERN = f"{IDX_NAME_PREFIX}*"
IDX_NAME_PATTERN_ANY = f"*_{IDX_NAME_CORE}_*"
IDX_ALIAS = f"{_cfg.es_prefix}_{IDX_NAME_CORE}"
IDX_TEMPLATE_NAME = f"{_cfg.es_prefix}_{IDX_NAME_CORE}_template"
IDX_TEMPLATE_NAME_PATTERN = f"*_{IDX_NAME_CORE}_template"


IDX_TEMPLATE = {
    "aliases": {IDX_ALIAS: {}},
    "mappings": {
        "dynamic": "false",
        "properties": {
            "text_id": {"type": "keyword"},
            "level": {"type": "short"},
            "position": {"type": "integer"},
        },
    },
    "settings": {
        "index": {"number_of_shards": 1, "number_of_replicas": 0},
        "analysis": {
            "analyzer": {
                "standard_asciifolding": {
                    "tokenizer": "standard",
                    "filter": ["asciifolding", "lowercase"],
                },
                "standard_htmlstrip": {
                    "tokenizer": "standard",
                    "filter": ["lowercase"],
                    "char_filter": ["html_strip"],
                },
                "standard_htmlstrip_asciifolding": {
                    "tokenizer": "standard",
                    "filter": ["asciifolding", "lowercase"],
                    "char_filter": ["html_strip"],
                },
            },
            "filter": {
                "asciifolding_preserve": {
                    "type": "asciifolding",
                    "preserve_original": True,
                }
            },
        },
    },
}
