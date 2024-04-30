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
        "dynamic": False,
        "properties": {
            "text_id": {"type": "keyword"},
            "level": {"type": "short"},
            "position": {"type": "integer"},
            "resources": {"type": "object"},
        },
        "dynamic_templates": [
            {
                "annotations": {
                    "path_match": "*.annotations.*",
                    "mapping": {
                        "type": "keyword",
                        "normalizer": "asciifolding_normalizer",
                        "fields": {"strict": {"type": "keyword"}},
                    },
                }
            }
        ],
    },
    "settings": {
        "index": {"number_of_shards": 1, "number_of_replicas": 0},
        "analysis": {
            "analyzer": {
                "standard_asciifolding": {
                    "tokenizer": "standard",
                    "filter": ["asciifolding", "lowercase"],
                },
            },
            "filter": {
                "asciifolding_preserve": {
                    "type": "asciifolding",
                    "preserve_original": True,
                }
            },
            "normalizer": {
                "asciifolding_normalizer": {
                    "type": "custom",
                    "char_filter": [],
                    "filter": ["asciifolding", "lowercase"],
                },
                "asciifolding_normalizer_preserve_case": {
                    "type": "custom",
                    "char_filter": [],
                    "filter": ["asciifolding"],
                },
            },
        },
    },
}

_GENERAL_SOURCE_INCLUDES = [
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


def get_source_includes(fields: list[str] = []) -> list[str]:
    return _GENERAL_SOURCE_INCLUDES + fields
