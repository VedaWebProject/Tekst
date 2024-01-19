import importlib
import inspect
import pkgutil

from abc import ABC, abstractmethod
from functools import lru_cache
from os.path import realpath
from pathlib import Path
from typing import Annotated, Union

from fastapi import Body
from humps import decamelize

from tekst.logging import log
from tekst.models.common import ReadBase
from tekst.models.content import ContentBase, ContentBaseDocument, ContentBaseUpdate
from tekst.models.resource import (
    ResourceBase,
    ResourceBaseDocument,
    ResourceBaseUpdate,
    ResourceReadExtras,
)


class ResourceTypeABC(ABC):
    """Abstract base class for defining a resource type"""

    __EXCLUDE_FROM_CONTENT_TEMPLATES: set[str] = {
        "id",
        "resourceId",
        "resourceType",
        "nodeId",
    }

    @classmethod
    def get_name(cls) -> str:
        """Returns the name of this resource type"""
        return cls.__name__

    @classmethod
    def get_key(cls) -> str:
        """Returns the key identifying this resource type"""
        return decamelize(cls.__name__)

    @classmethod
    @abstractmethod
    def resource_model(cls) -> type[ResourceBase]:
        """Returns the resource base model for this type of resource"""
        raise NotImplementedError(
            "Classmethod 'resource_model' must be "
            f"implemented in subclasses of {cls.__name__}"
        )  # pragma: no cover

    @classmethod
    @abstractmethod
    def content_model(cls) -> type[ContentBase]:
        """Returns the content base model for contents of this type of resource"""
        raise NotImplementedError(
            "Classmethod 'content_model' must be "
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
        for prop, val in schema.get("properties", {}).items():
            if prop not in cls.__EXCLUDE_FROM_CONTENT_TEMPLATES:
                prop_schema = {k: v for k, v in val.items()}
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
        self.__resource_types[resource_type_name.lower()] = resource_type_class()

    def get(self, resource_type_name: str) -> ResourceTypeABC:
        return self.__resource_types.get(resource_type_name.lower())

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
    lt_modules = [mod.name.lower() for mod in pkgutil.iter_modules(__path__)]
    for lt_module in lt_modules:
        module = importlib.import_module(f"{__name__}.{lt_module.lower()}")
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


# global variable to hold resource type manager instance
resource_types_mgr: ResourceTypesManager = None
init_resource_types_mgr()


# ### create union type aliases for models of any resource type model

# CREATE
AnyResourceCreate = Union[  # noqa: UP007
    tuple(
        [
            lt.resource_model().create_model()
            for lt in resource_types_mgr.get_all().values()
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
            lt.resource_model().read_model()
            for lt in resource_types_mgr.get_all().values()
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
            lt.resource_model().update_model()
            for lt in resource_types_mgr.get_all().values()
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
            lt.resource_model().document_model()
            for lt in resource_types_mgr.get_all().values()
        ]
    )
]


# ### create union type aliases for models of any content type model

# CREATE
AnyContentCreate = Union[  # noqa: UP007
    tuple(
        [
            lt.content_model().create_model()
            for lt in resource_types_mgr.get_all().values()
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
            lt.content_model().read_model()
            for lt in resource_types_mgr.get_all().values()
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
            lt.content_model().update_model()
            for lt in resource_types_mgr.get_all().values()
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
            lt.content_model().document_model()
            for lt in resource_types_mgr.get_all().values()
        ]
    )
]


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
