from tekst.config import TekstConfig, get_config


_cfg: TekstConfig = get_config()

IDX_NAME_CORE = "locations"
IDX_NAME_PREFIX = f"{_cfg.es.prefix}_{IDX_NAME_CORE}_"
IDX_NAME_PATTERN = f"{IDX_NAME_PREFIX}*"
IDX_NAME_PATTERN_ANY = f"*_{IDX_NAME_CORE}_*"
IDX_ALIAS = f"{_cfg.es.prefix}_{IDX_NAME_CORE}"
IDX_TEMPLATE_NAME = f"{_cfg.es.prefix}_{IDX_NAME_CORE}_template"
IDX_TEMPLATE_NAME_PATTERN = f"*_{IDX_NAME_CORE}_template"


IDX_TEMPLATE = {
    "aliases": {IDX_ALIAS: {}},
    "settings": {
        "index": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "mapping": {
                "total_fields": {
                    "limit": 3000,
                    "ignore_dynamic_beyond_limit": False,
                }
            },
        },
        "analysis": {
            "analyzer": {
                "standard_no_diacritics": {
                    "tokenizer": "standard",
                    "filter": ["no_diacritics", "lowercase"],
                },
            },
            "filter": {
                "no_diacritics": {
                    "type": "icu_transform",
                    "id": "NFD; [:Nonspacing Mark:] Remove; NFC",
                }
            },
            "normalizer": {
                "no_diacritics_normalizer": {
                    "type": "custom",
                    "filter": ["no_diacritics", "lowercase"],
                },
                "lowercase_normalizer": {
                    "type": "custom",
                    "filter": ["lowercase"],
                },
            },
        },
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "resources": {"type": "object"},
            "text_id": {"type": "keyword"},
            "level": {"type": "byte"},
            "position": {"type": "integer"},
            "default_level": {"type": "boolean"},
            "label": {"type": "keyword", "index": False},
            "full_label": {"type": "keyword", "index": False},
        },
    },
}

QUERY_SOURCE_INCLUDES = [
    "text_id",
    "level",
    "position",
    "label",
    "full_label",
]

SORTING_PRESETS = {
    "relevance": None,
    "text_level_position": [
        {"text_id": {"order": "desc"}},
        {"level": {"order": "asc"}},
        {"position": {"order": "asc"}},
    ],
    "text_level_relevance": [
        {"text_id": {"order": "desc"}},
        {"level": {"order": "asc"}},
        "_score",
    ],
}
