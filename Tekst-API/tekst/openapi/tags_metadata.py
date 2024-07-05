from typing import Any


def get_tags_metadata(documentation_url: str) -> list[dict[str, Any]]:
    return [
        {
            "name": "texts",
            "description": "Texts configured on this platform",
            "externalDocs": {
                "description": "View full documentation",
                "url": documentation_url,
            },
        },
        {
            "name": "locations",
            "description": "Text locations (the structural units of a text)",
            "externalDocs": {
                "description": "View full documentation",
                "url": documentation_url,
            },
        },
        {
            "name": "resources",
            "description": "Resources related to certain texts",
            "externalDocs": {
                "description": "View full documentation",
                "url": documentation_url,
            },
        },
        {
            "name": "contents",
            "description": "Contents of resources",
            "externalDocs": {
                "description": "View full documentation",
                "url": documentation_url,
            },
        },
        {
            "name": "corrections",
            "description": "Correction notes from user to users",
            "externalDocs": {
                "description": "View full documentation",
                "url": documentation_url,
            },
        },
        {
            "name": "search",
            "description": "Search operations and search index maintenance",
            "externalDocs": {
                "description": "View full documentation",
                "url": documentation_url,
            },
        },
        {
            "name": "browse",
            "description": "Endpoints for effectively browsing the plaform data",
            "externalDocs": {
                "description": "View full documentation",
                "url": documentation_url,
            },
        },
        {
            "name": "platform",
            "description": "Platform-specific data, infos and operations",
            "externalDocs": {
                "description": "View full documentation",
                "url": documentation_url,
            },
        },
        {
            "name": "users",
            "description": "Registered users and their accounts",
            "externalDocs": {
                "description": "View full documentation",
                "url": documentation_url,
            },
        },
        {
            "name": "messages",
            "description": "Messages users send and receive on the platform",
            "externalDocs": {
                "description": "View full documentation",
                "url": documentation_url,
            },
        },
        {
            "name": "bookmarks",
            "description": "The current user's bookmarks",
            "externalDocs": {
                "description": "View full documentation",
                "url": documentation_url,
            },
        },
        {
            "name": "auth",
            "description": "Registration, authentication and security",
            "externalDocs": {
                "description": "View full documentation",
                "url": documentation_url,
            },
        },
        {
            "name": "status",
            "description": "The status of the API and its services",
            "externalDocs": {
                "description": "View full documentation",
                "url": documentation_url,
            },
        },
    ]
