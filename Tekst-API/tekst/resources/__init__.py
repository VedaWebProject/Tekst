import importlib
import inspect
import json
import pkgutil

from abc import ABC, abstractmethod
from functools import lru_cache
from os.path import realpath
from pathlib import Path
from typing import Annotated, Any, Union

import jsonref

from fastapi import Body
from humps import camelize
from pydantic import Field, StringConstraints

from tekst.logging import log
from tekst.models.common import ModelBase, PydanticObjectId, ReadBase
from tekst.models.content import ContentBase, ContentBaseDocument, ContentBaseUpdate
from tekst.models.location import LocationDocument
from tekst.models.resource import (
    ResourceBase,
    ResourceBaseDocument,
    ResourceBaseUpdate,
    ResourceExportFormat,
    ResourceReadExtras,
)
from tekst.models.text import TextDocument
from tekst.utils import validators as val


# global variable to hold resource type manager instance
resource_types_mgr: "ResourceTypesManager" = None


@lru_cache
def get_resource_template_readme() -> dict[str, str]:
    _template_readme_lines = (
        (Path(realpath(__file__)).parent / "import_template_readme.txt")
        .read_text(encoding="utf-8")
        .splitlines()
    )
    return {
        str(i + 1): _template_readme_lines[i]
        for i in range(len(_template_readme_lines))
    }


async def call_contents_changed_hooks(text_id: PydanticObjectId) -> None:
    for resource in await ResourceBaseDocument.find(
        ResourceBaseDocument.text_id == text_id, with_children=True
    ).to_list():
        await resource_types_mgr.get(resource.resource_type).contents_changed_hook(
            resource.id
        )


class CommonResourceSearchQueryData(ModelBase):
    optional: Annotated[
        bool,
        Field(
            alias="opt",
            description=(
                "Whether this query matching is optional for the "
                "location to be considered a search hit"
            ),
        ),
    ] = True
    resource_id: Annotated[
        PydanticObjectId,
        Field(
            alias="res",
            description="ID of the resource to search in",
        ),
    ]
    comment: Annotated[
        str,
        Field(
            alias="cmt",
            description="Comment",
        ),
        StringConstraints(max_length=512, strip_whitespace=True),
        val.CleanupOneline,
    ] = ""


class ResourceSearchQuery(ModelBase):
    common: Annotated[
        CommonResourceSearchQueryData,
        Field(
            alias="cmn",
            description="Common resource search query data",
        ),
    ]
    resource_type_specific: Annotated[
        "AnyResourceSearchQuery",
        Field(
            alias="rts",
            description="Resource type-specific search query data",
        ),
    ]

    def get_set_fields(self) -> set[str]:
        set_fields = self.common.model_fields_set.union(
            self.resource_type_specific.model_fields_set
        )
        return {
            field
            for field in set_fields
            if field not in ["resource_id", "resource_type"]
        }


class ResourceTypeABC(ABC):
    """Abstract base class for defining a resource type"""

    # fields to exclude from content import schema
    _EXCLUDE_FROM_CONTENT_IMPORT_SCHEMA: set[str] = {
        "id",
        "resource_id",
        "resource_type",
        "location_id",
    }

    # fields to exclude from content export data
    _EXCLUDE_FROM_CONTENT_EXPORT_DATA: set[str] = {
        "_id",
        "id",
        "resource_id",
        "resource_type",
    }

    @classmethod
    def get_name(cls) -> str:
        """Returns the name of this resource type"""
        return cls.__name__

    @classmethod
    def get_key(cls) -> str:
        """Returns the key identifying this resource type"""
        return camelize(cls.__name__)

    @classmethod
    def index_doc_props(cls) -> dict[str, Any]:
        """
        Returns the mappings properties for ES search index
        documents for contents of this resource type
        """
        return dict(
            comment={
                "type": "text",
                "analyzer": "standard_asciifolding",
                "fields": {"strict": {"type": "text"}},
            },
            **cls.rtype_index_doc_props(),
        )

    @classmethod
    def index_doc_data(cls, content: ContentBase) -> dict[str, Any]:
        """
        Returns the content for the ES index document for this type of resource content
        """
        return dict(
            comment=content.comment,
            **cls.rtype_index_doc_data(content),
        )

    @classmethod
    def es_queries(
        cls,
        *,
        query: "ResourceSearchQuery",
        strict: bool = False,
    ) -> list[dict[str, Any]]:
        es_queries = []
        set_fields = query.get_set_fields()
        strict_suffix = ".strict" if strict else ""
        if "comment" in set_fields:
            es_queries.append(
                {
                    "simple_query_string": {
                        "fields": [
                            f"resources.{query.common.resource_id}.comment{strict_suffix}"
                        ],
                        "query": query.common.comment,
                    }
                }
            )
        return [
            *es_queries,
            *cls.rtype_es_queries(query=query, strict=strict),
        ]

    @classmethod
    def prepare_import_template(cls) -> dict:
        """Returns the base template for import data for this resource type"""
        schema = jsonref.replace_refs(
            cls.content_model().create_model().model_json_schema()
        )
        required = schema.get("required", [])
        template = {
            "_contentSchema": {},  # will be populated in the next step
        }
        # generate content schema for the template
        excludes = camelize(cls._EXCLUDE_FROM_CONTENT_IMPORT_SCHEMA)
        for prop, value in schema.get("properties", {}).items():
            if prop not in excludes:
                prop_schema = {k: v for k, v in value.items()}
                prop_schema["required"] = prop in required
                template["_contentSchema"][prop] = prop_schema
        return template

    @classmethod
    async def export_tekst_json(
        cls,
        *,
        resource: ResourceBaseDocument,
        contents: list[ContentBaseDocument],
    ) -> str:
        """
        Exports the given contents of the given resource as JSON, compatible for
        re-import in Tekst.
        """
        return json.dumps(
            {
                "resourceId": str(resource.id),
                "contents": [
                    c.model_dump(
                        by_alias=True,
                        exclude_unset=True,
                        exclude_none=True,
                        exclude=cls._EXCLUDE_FROM_CONTENT_EXPORT_DATA,
                    )
                    for c in contents
                ],
            },
            ensure_ascii=False,
        )

    @classmethod
    async def export_universal_json(
        cls,
        *,
        resource: ResourceBaseDocument,
        contents: list[ContentBaseDocument],
    ) -> str:
        """
        Exports the given contents of the given resource as JSON, in a form that
        aims to be as comprehensive as possible.
        """
        # prepare (root) resource object
        text: TextDocument = await TextDocument.get(resource.text_id)
        res = camelize(
            resource.model_dump(
                include={
                    "title",
                    "description",
                    "level",
                    "citation",
                    "meta",
                    "comment",
                },
                exclude_none=True,
                exclude_unset=True,
            )
        )
        res["description"] = {
            desc_trans["locale"]: desc_trans["translation"]
            for desc_trans in res["description"]
        }
        res["level"] = {
            lvl_trans["locale"]: lvl_trans["translation"]
            for lvl_trans in text.levels[res["level"]]
        }
        res["comment"] = {
            comment["locale"]: comment["translation"] for comment in res["comment"]
        }
        res["meta"] = {meta["key"]: meta["value"] for meta in res["meta"]}

        # construct content objects
        contents = [
            camelize(
                c.model_dump(
                    by_alias=True,
                    exclude_unset=True,
                    exclude_none=True,
                    exclude=cls._EXCLUDE_FROM_CONTENT_EXPORT_DATA,
                )
            )
            for c in contents
        ]
        # construct labels of all locations on the resource's level
        full_location_labels = await LocationDocument.full_location_labels(
            text_id=resource.text_id,
            for_level=resource.level,
        )
        for content in contents:
            content["location"] = full_location_labels[content["locationId"]]
            del content["locationId"]
        res["contents"] = contents

        return json.dumps(
            res,
            ensure_ascii=False,
        )

    @classmethod
    async def contents_changed_hook(cls, resource_id: PydanticObjectId) -> None:
        """
        Will be called whenever the contents of the resource with the given ID changes.
        This may be overridden by concrete resource implementations to run arbitrary
        maintenance procedures. Otherwise it is juust a no-op.
        """

    @classmethod
    @abstractmethod
    def resource_model(cls) -> type[ResourceBase]:
        """Returns the resource model for this type of resource"""

    @classmethod
    @abstractmethod
    def content_model(cls) -> type[ContentBase]:
        """Returns the content model for contents of this type of resource"""

    @classmethod
    @abstractmethod
    def search_query_model(cls) -> type["ResourceSearchQuery"] | None:
        """
        Returns the search query model for search
        queries targeting this type of resource
        """

    @classmethod
    @abstractmethod
    def rtype_index_doc_props(cls) -> dict[str, Any]:
        """
        Returns the mappings properties for ES search index
        documents unique for this type of resource content
        """

    @classmethod
    @abstractmethod
    def rtype_index_doc_data(cls, content: ContentBase) -> dict[str, Any]:
        """
        Returns the content for the ES index document
        for this type of resource content that is unique to this resource type
        """

    @classmethod
    @abstractmethod
    def rtype_es_queries(
        cls, *, query: "ResourceSearchQuery", strict: bool = False
    ) -> list[dict[str, Any]]:
        """
        Constructs an Elasticsearch search query for each field
        in the given resource search query instance.
        Common content fields are not included in the returned queries.
        """

    @classmethod
    @abstractmethod
    async def export(
        cls,
        *,
        resource: ResourceBaseDocument,
        contents: list[ContentBaseDocument],
        export_format: ResourceExportFormat,
    ) -> str:
        """
        Prepares export data and returns a temporary file object.
        Raises ValueError if the export format is not supported by this resource type.
        """


class ResourceTypesManager:
    __resource_types: dict[str, ResourceTypeABC] = dict()

    def register(
        self, resource_type_class: type[ResourceTypeABC], resource_type_name: str
    ):
        # create resource/content document models
        resource_type_class.resource_model().document_model(ResourceBaseDocument)
        resource_type_class.resource_model().update_model(ResourceBaseUpdate)
        resource_type_class.content_model().document_model(ContentBaseDocument)
        resource_type_class.content_model().update_model(ContentBaseUpdate)
        # register instance
        self.__resource_types[resource_type_name] = resource_type_class()

    def get(self, resource_type_name: str) -> ResourceTypeABC:
        return self.__resource_types.get(resource_type_name)

    def get_all(self) -> dict[str, ResourceTypeABC]:
        return self.__resource_types

    def list_names(self) -> list[str]:
        return list(self.__resource_types.keys())


def init_resource_types_mgr() -> None:
    global resource_types_mgr
    if resource_types_mgr is not None:
        return resource_types_mgr
    log.info("Initializing resource types...")
    # init manager
    manager = ResourceTypesManager()
    # get internal resource type module names
    lt_modules = [mod.name for mod in pkgutil.iter_modules(__path__)]
    for lt_module in lt_modules:
        module = importlib.import_module(f"{__name__}.{lt_module}")
        resource_types_from_module = inspect.getmembers(
            module, lambda o: inspect.isclass(o) and issubclass(o, ResourceTypeABC)
        )
        for resource_type_impl in resource_types_from_module:
            # exclude ResourceTypeABC class (which is weirdly picked up here)
            if resource_type_impl[1] is not ResourceTypeABC:
                resource_type_class = resource_type_impl[1]
                # init resource/content type CRUD models
                # (don't init document models here!)
                resource_type_class.resource_model().create_model()
                resource_type_class.resource_model().read_model(
                    (ResourceReadExtras, ReadBase)
                )
                resource_type_class.resource_model().update_model()
                resource_type_class.content_model().create_model()
                resource_type_class.content_model().read_model()
                resource_type_class.content_model().update_model()
                # register resource type instance with resource type manager
                log.info(f"Registering resource type: {resource_type_class.get_name()}")
                manager.register(resource_type_class, resource_type_class.get_key())
    resource_types_mgr = manager


init_resource_types_mgr()


# ### create union type aliases for models of any resource type model

# CREATE
AnyResourceCreate = Union[  # noqa: UP007
    tuple(
        [
            rt.resource_model().create_model()
            for rt in resource_types_mgr.get_all().values()
        ]
    )
]
AnyResourceCreateBody = Annotated[
    AnyResourceCreate,
    Body(discriminator="resource_type"),
]

# READ
AnyResourceRead = Union[  # noqa: UP007
    tuple(
        [
            rt.resource_model().read_model()
            for rt in resource_types_mgr.get_all().values()
        ]
    )
]
AnyResourceReadBody = Annotated[
    AnyResourceRead,
    Body(discriminator="resource_type"),
]

# UPDATE
AnyResourceUpdate = Union[  # noqa: UP007
    tuple(
        [
            rt.resource_model().update_model()
            for rt in resource_types_mgr.get_all().values()
        ]
    )
]
AnyResourceUpdateBody = Annotated[
    AnyResourceUpdate,
    Body(discriminator="resource_type"),
]

# DOCUMENT
AnyResourceDocument = Union[  # noqa: UP007
    tuple(
        [
            rt.resource_model().document_model()
            for rt in resource_types_mgr.get_all().values()
        ]
    )
]


# ### create union type aliases for models of any content type model

# CREATE
AnyContentCreate = Union[  # noqa: UP007
    tuple(
        [
            rt.content_model().create_model()
            for rt in resource_types_mgr.get_all().values()
        ]
    )
]
AnyContentCreateBody = Annotated[
    AnyContentCreate,
    Body(discriminator="resource_type"),
]

# READ
AnyContentRead = Union[  # noqa: UP007
    tuple(
        [
            rt.content_model().read_model()
            for rt in resource_types_mgr.get_all().values()
        ]
    )
]
AnyContentReadBody = Annotated[
    AnyContentRead,
    Body(discriminator="resource_type"),
]

# UPDATE
AnyContentUpdate = Union[  # noqa: UP007
    tuple(
        [
            rt.content_model().update_model()
            for rt in resource_types_mgr.get_all().values()
        ]
    )
]
AnyContentUpdateBody = Annotated[
    AnyContentUpdate,
    Body(discriminator="resource_type"),
]

# DOCUMENT
AnyContentDocument = Union[  # noqa: UP007
    tuple(
        [
            rt.content_model().document_model()
            for rt in resource_types_mgr.get_all().values()
        ]
    )
]

# ANY RESOURCE SEARCH QUERY
AnyResourceSearchQuery = Annotated[
    Union[  # noqa: UP007
        tuple([rt.search_query_model() for rt in resource_types_mgr.get_all().values()])
    ],
    Field(discriminator="resource_type"),
]
