INDEX_TEMPLATE = {
    "mappings": {
        "dynamic": "false",
        "properties": {
            "text_id": {"type": "keyword"},
            "level": {"type": "short"},
            "position": {"type": "integer"},
        },
    },
    "settings": {
        "analysis": {
            "analyzer": {
                "htmlStripAnalyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase"],
                    "char_filter": ["html_strip"],
                }
            }
        }
    },
}
