TEXTS = {
    "rigveda": {
        "text": {
            "title": "Rigveda",
            "slug": "rigveda",
            "subtitle": [
                {
                    "locale": "enUS",
                    "subtitle": "An ancient Indian collection of Vedic Sanskrit hymns",
                },
                {
                    "locale": "deDE",
                    "subtitle": "Eine altindische Sammlung vedischer Sanskrit-Hymnen",
                },
            ],
            "levels": [
                [
                    {"locale": "enUS", "label": "Book"},
                    {"locale": "deDE", "label": "Buch"},
                ],
                [
                    {"locale": "enUS", "label": "Hymn"},
                    {"locale": "deDE", "label": "Hymnus"},
                ],
                [
                    {"locale": "enUS", "label": "Stanza"},
                    {"locale": "deDE", "label": "Strophe"},
                ],
            ],
            "accentColor": "#D43A35",
            "locDelim": ".",
            "defaultLevel": 2,
            "labeledLocation": False,
            "isActive": False,
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
                                "label": "001",
                            },
                            {
                                "level": 2,
                                "position": 3,
                                "label": "002",
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
                        "label": "01",
                        "children": [
                            {
                                "level": 2,
                                "position": 4,
                                "label": "001",
                            },
                            {
                                "level": 2,
                                "position": 5,
                                "label": "002",
                            },
                        ],
                    },
                    {
                        "level": 1,
                        "position": 3,
                        "label": "02",
                        "children": [
                            {
                                "level": 2,
                                "position": 6,
                                "label": "001",
                            },
                            {
                                "level": 2,
                                "position": 7,
                                "label": "002",
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
            "subtitle": [
                {"locale": "enUS", "subtitle": "An old German folk song"},
                {"locale": "deDE", "subtitle": "Ein altdeutsches Volkslied"},
            ],
            "levels": [
                [
                    {"locale": "enUS", "label": "Stanza"},
                    {"locale": "deDE", "label": "Strophe"},
                ],
                [
                    {"locale": "enUS", "label": "Line"},
                    {"locale": "deDE", "label": "Vers"},
                ],
            ],
            "accent_color": "#43895F",
            "locDelim": " > ",
            "defaultLevel": 1,
            "isActive": True,
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
            "public": True,
            "units": [
                {"sampleNodePosition": 0, "text": "Foo Bar"},
                {"sampleNodePosition": 1, "text": "Foo Bar"},
                {"sampleNodePosition": 2, "text": "Foo Bar"},
                {"sampleNodePosition": 3, "text": "Foo Bar"},
                {"sampleNodePosition": 4, "text": "Foo Bar"},
                {"sampleNodePosition": 5, "text": "Foo Bar"},
                {"sampleNodePosition": 6, "text": "Foo Bar"},
                {"sampleNodePosition": 7, "text": "Foo Bar"},
            ],
            "meta": {"author": "Van Nooten & Holland", "year": "1995"},
            "comment": "This is\na comment\nwith line breaks.",
        },
    ],
    "fdhdgg": [
        {
            "title": "Originalfassung",
            "level": 1,
            "layerType": "plaintext",
            "public": True,
            "units": [
                {
                    "sampleNodePosition": 0,
                    "text": "Fuchs, du hast die Gans gestohlen,",
                },
                {
                    "sampleNodePosition": 1,
                    "text": "|: gib sie wieder her! :|",
                },
                {
                    "sampleNodePosition": 2,
                    "text": "|: Sonst wird sie der Jäger holen",
                },
                {
                    "sampleNodePosition": 3,
                    "text": "mit dem Schießgewehr. :|",
                },
                {
                    "sampleNodePosition": 4,
                    "text": "Seine große, lange Flinte",
                },
                {
                    "sampleNodePosition": 5,
                    "text": "|: schießt auf dich den Schrot, :|",
                },
                {
                    "sampleNodePosition": 6,
                    "text": "|: dass dich färbt die rote Tinte",
                },
                {
                    "sampleNodePosition": 7,
                    "text": "und dann bist du tot. :|",
                },
                {
                    "sampleNodePosition": 8,
                    "text": "Liebes Füchslein, lass dir raten,",
                },
                {
                    "sampleNodePosition": 9,
                    "text": "|: sei doch nur kein Dieb; :|",
                },
                {
                    "sampleNodePosition": 10,
                    "text": "|: nimm, du brauchst nicht Gänsebraten,",
                },
                {
                    "sampleNodePosition": 11,
                    "text": "mit der Maus vorlieb. :|",
                },
            ],
            "meta": {
                "author": "Ernst Anschütz",
                "year": "1824",
                "original title": "Warnung",
                "language": "DE",
            },
            "comment": "This version includes repetition markers.",
            "config": {
                "deeplLinks": {
                    "enabled": True,
                    "languages": ["EN", "FR"],
                    "sourceLanguage": "DE",
                }
            },
        }
    ],
}
