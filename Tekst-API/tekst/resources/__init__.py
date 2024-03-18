import importlib
import inspect
import pkgutil

from abc import ABC, abstractmethod
from functools import lru_cache
from os.path import realpath
from pathlib import Path
from typing import Annotated, Any, Union

from fastapi import Body
from humps import camelize
from pydantic import Field, StringConstraints

from tekst.logging import log
from tekst.models.common import ModelBase, PydanticObjectId, ReadBase
from tekst.models.content import ContentBase, ContentBaseDocument, ContentBaseUpdate
from tekst.models.resource import (
    ResourceBase,
    ResourceBaseDocument,
    ResourceBaseUpdate,
    ResourceReadExtras,
)
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


class CommonResourceSearchQueryData(ModelBase):
    required: Annotated[
        bool,
        Field(
            alias="req",
            description=(
                "Whether this query is required to match for the "
                "location to be considered a search hit"
            ),
        ),
    ] = False
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

    __EXCLUDE_FROM_CONTENT_TEMPLATES: set[str] = {
        "id",
        "resourceId",
        "resourceType",
        "locationId",
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
    @abstractmethod
    def resource_model(cls) -> type[ResourceBase]:
        """Returns the resource model for this type of resource"""
        raise NotImplementedError(
            "Classmethod 'resource_model' must be "
            f"implemented in subclasses of {cls.__name__}"
        )  # pragma: no cover

    @classmethod
    @abstractmethod
    def content_model(cls) -> type[ContentBase]:
        """Returns the content model for contents of this type of resource"""
        raise NotImplementedError(
            "Classmethod 'content_model' must be "
            f"implemented in subclasses of {cls.__name__}"
        )  # pragma: no cover

    @classmethod
    @abstractmethod
    def search_query_model(cls) -> type["ResourceSearchQuery"] | None:
        """
        Returns the search query model for search
        queries targeting this type of resource
        """
        raise NotImplementedError(
            "Classmethod 'search_query_model' must be "
            f"implemented in subclasses of {cls.__name__}"
        )  # pragma: no cover

    @classmethod
    @abstractmethod
    def construct_es_queries(
        cls, query: "ResourceSearchQuery", *, strict: bool = False
    ) -> tuple[list[dict[str, Any]], list[str]]:
        """
        Constructs an Elasticsearch search query for each field
        in the given resource search query model instance and returns
        a tuple of said queries and a list of the relevant field names
        """
        raise NotImplementedError(
            "Classmethod 'construct_es_query' must be "
            f"implemented in subclasses of {cls.__name__}"
        )  # pragma: no cover

    @classmethod
    @abstractmethod
    def index_doc_properties(cls) -> dict[str, Any]:
        """
        Returns the mappings properties for ES search index
        documents for this type of resource content
        """
        raise NotImplementedError(
            "Classmethod 'index_doc_properties' must be "
            f"implemented in subclasses of {cls.__name__}"
        )  # pragma: no cover

    @classmethod
    @abstractmethod
    def index_doc_data(cls, content: ContentBase) -> dict[str, Any]:
        """
        Returns the content for the ES index document
        for this type of resource content
        """
        raise NotImplementedError(
            "Classmethod 'index_doc_data' must be "
            f"implemented in subclasses of {cls.__name__}"
        )  # pragma: no cover

    @classmethod
    def prepare_import_template(cls) -> dict:
        """Returns the base template for import data for this resource type"""
        schema = cls.content_model().create_model().schema()
        required = schema.get("required", [])
        template = {
            "_contentSchema": {},  # will be populated in the next step
        }
        # generate content schema for the template
        for prop, value in schema.get("properties", {}).items():
            if prop not in cls.__EXCLUDE_FROM_CONTENT_TEMPLATES:
                prop_schema = {k: v for k, v in value.items()}
                prop_schema["required"] = prop in required
                template["_contentSchema"][prop] = prop_schema
        return template


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
