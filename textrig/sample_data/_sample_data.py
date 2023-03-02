TEXTS = {
    "rigveda": {
        "text": {
            "title": "Rigveda",
            "slug": "rigveda",
            "subtitle": "An ancient Indian collection of Vedic Sanskrit hymns",
            "levels": ["Book", "Hymn", "Stanza"],
            "accentColor": "#bc243b",
        },
        "nodes": [
            {
                "level": 0,
                "position": 0,
                "label": "001",
                "children": [
                    {
                        "level": 1,
                        "position": 0,
                        "label": "01",
                        "children": [
                            {
                                "level": 2,
                                "position": 0,
                                "label": "001",
                            },
                            {
                                "level": 2,
                                "position": 1,
                                "label": "002",
                            },
                        ],
                    },
                    {
                        "level": 1,
                        "position": 1,
                        "label": "02",
                        "children": [
                            {
                                "level": 2,
                                "position": 2,
                                "label": "003",
                            },
                            {
                                "level": 2,
                                "position": 3,
                                "label": "004",
                            },
                        ],
                    },
                ],
            },
            {
                "level": 0,
                "position": 1,
                "label": "002",
                "children": [
                    {
                        "level": 1,
                        "position": 2,
                        "label": "03",
                        "children": [
                            {
                                "level": 2,
                                "position": 4,
                                "label": "005",
                            },
                            {
                                "level": 2,
                                "position": 5,
                                "label": "006",
                            },
                        ],
                    },
                    {
                        "level": 1,
                        "position": 3,
                        "label": "04",
                        "children": [
                            {
                                "level": 2,
                                "position": 6,
                                "label": "007",
                            },
                            {
                                "level": 2,
                                "position": 7,
                                "label": "008",
                            },
                        ],
                    },
                ],
            },
        ],
    },
    "fdhdgg": {
        "text": {
            "title": "Fuchs, du hast die Gans gestohlen",
            "slug": "fdhdgg",
            "subtitle": "An old German folk song",
            "levels": ["Stanza", "Line"],
            "accent_color": "#334195",
        },
        "nodes": [
            {
                "level": 0,
                "position": 0,
                "label": "1",
                "children": [
                    {
                        "level": 1,
                        "position": 0,
                        "label": "1",
                    },
                    {
                        "level": 1,
                        "position": 1,
                        "label": "2",
                    },
                    {
                        "level": 1,
                        "position": 2,
                        "label": "3",
                    },
                    {
                        "level": 1,
                        "position": 3,
                        "label": "4",
                    },
                ],
            },
            {
                "level": 0,
                "position": 1,
                "label": "2",
                "children": [
                    {
                        "level": 1,
                        "position": 4,
                        "label": "1",
                    },
                    {
                        "level": 1,
                        "position": 5,
                        "label": "2",
                    },
                    {
                        "level": 1,
                        "position": 6,
                        "label": "3",
                    },
                    {
                        "level": 1,
                        "position": 7,
                        "label": "4",
                    },
                ],
            },
            {
                "level": 0,
                "position": 2,
                "label": "3",
                "children": [
                    {
                        "level": 1,
                        "position": 8,
                        "label": "1",
                    },
                    {
                        "level": 1,
                        "position": 9,
                        "label": "2",
                    },
                    {
                        "level": 1,
                        "position": 10,
                        "label": "3",
                    },
                    {
                        "level": 1,
                        "position": 11,
                        "label": "4",
                    },
                ],
            },
        ],
    },
}

LAYERS = {
    "rigveda": [
        {
            "title": "Van Nooten & Holland",
            "level": 2,
            "layerType": "plaintext",
            "units": [
                {"sample_node_level": 2, "sample_node_position": 0, "text": "Foo Bar"},
                {"sample_node_level": 2, "sample_node_position": 1, "text": "Foo Bar"},
                {"sample_node_level": 2, "sample_node_position": 2, "text": "Foo Bar"},
                {"sample_node_level": 2, "sample_node_position": 3, "text": "Foo Bar"},
                {"sample_node_level": 2, "sample_node_position": 4, "text": "Foo Bar"},
                {"sample_node_level": 2, "sample_node_position": 5, "text": "Foo Bar"},
                {"sample_node_level": 2, "sample_node_position": 6, "text": "Foo Bar"},
                {"sample_node_level": 2, "sample_node_position": 7, "text": "Foo Bar"},
            ],
        }
    ],
    "fdhdgg": [
        {
            "title": "Originaltext",
            "level": 1,
            "layerType": "plaintext",
            "units": [
                {"sample_node_level": 1, "sample_node_position": 0, "text": "Foo Bar"},
                {"sample_node_level": 1, "sample_node_position": 1, "text": "Foo Bar"},
                {"sample_node_level": 1, "sample_node_position": 2, "text": "Foo Bar"},
                {"sample_node_level": 1, "sample_node_position": 3, "text": "Foo Bar"},
                {"sample_node_level": 1, "sample_node_position": 4, "text": "Foo Bar"},
                {"sample_node_level": 1, "sample_node_position": 5, "text": "Foo Bar"},
                {"sample_node_level": 1, "sample_node_position": 6, "text": "Foo Bar"},
                {"sample_node_level": 1, "sample_node_position": 7, "text": "Foo Bar"},
                {"sample_node_level": 1, "sample_node_position": 8, "text": "Foo Bar"},
                {"sample_node_level": 1, "sample_node_position": 9, "text": "Foo Bar"},
                {"sample_node_level": 1, "sample_node_position": 10, "text": "Foo Bar"},
                {"sample_node_level": 1, "sample_node_position": 11, "text": "Foo Bar"},
            ],
        }
    ],
}
