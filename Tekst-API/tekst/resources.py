import importlib
import inspect
import json
import pkgutil

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any

import jsonref

from beanie.operators import In
from humps import camelize

from tekst import resource_types
from tekst.logs import log, log_op_end, log_op_start
from tekst.models.common import (
    PydanticObjectId,
)
from tekst.models.content import (
    ContentBase,
    ContentBaseDocument,
)
from tekst.models.resource import (
    ResourceBase,
    ResourceBaseDocument,
    ResourceExportFormat,
)
from tekst.models.text import TextDocument
from tekst.utils import ensure


if TYPE_CHECKING:
    from tekst.models.search import ResourceSearchQuery


# resource base model fields to exclude from export/import
RES_EXCLUDE_EXP_IMP = {
    "text_id",
    "level",
    "resource_type",
    "patch_for",
    "owner_ids",
    "shared_read",
    "shared_write",
    "public",
    "proposed",
    "contents_changed_at",
}


IMPORT_README_TXT = """
This is a JSONL file (JSON lines). It contains one valid JSON object per line:
(1.) A README object. It is purely for your informational purposes
and can be omitted in the actual import file. You are reading it right now.
(2.) A number of content template objects, one per subsequent line.
You have to fill them with the actual content to import.
Properties prefixed with an underscore are purely for informational purposes
and can be omitted in the actual import file.
Important: The '_contentSchema' object in this very README object gives you
a schema and description each content object has to follow to be valid.
Additionally, every content you provide MUST keep the exact 'locationId'
property from this template!
Already existing contents will be archived. The imported content will become
the current version. To skip import for specific locations,
omit the respective contents/lines from the import file.
"""


async def call_resource_precompute_hooks(
    text_id: PydanticObjectId | None = None,
    *,
    force: bool = False,
) -> dict[str, float]:
    op_id = log_op_start(
        f"Refresh precomputed cache for resource data (forced: {force})",
        level="INFO",
    )
    for resource in await ResourceBaseDocument.find(
        In(
            ResourceBaseDocument.text_id,
            [txt.id for txt in await TextDocument.all().to_list()]
            if not text_id
            else [text_id],
        ),
        with_children=True,
    ).to_list():
        await resource.resource_precompute_hook(force=force)

    return {"took": round(log_op_end(op_id), 2)}


class ResourceTypeBase:
    """Abstract base class for defining a resource type"""

    # fields to exclude from content export data
    _EXCLUDE_FROM_CONTENT_EXPORT_DATA: set[str] = {
        "_id",
        "id",
        "resource_id",
        "resource_type",
        "archived",
        "created_at",
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
    def index_mappings(
        cls,
        lenient_analyzer: str,
        strict_analyzer: str,
    ) -> dict[str, Any]:
        """
        Returns the mappings properties for ES search index
        documents for contents of this resource type
        """
        # get resource type-specific mappings
        rtype_mappings = cls._rtype_index_mappings(
            lenient_analyzer=lenient_analyzer,
            strict_analyzer=strict_analyzer,
        )
        return dict(
            native={"type": "boolean"},
            comment={
                "type": "text",
                "analyzer": "standard_no_diacritics",
                "fields": {"strict": {"type": "text"}},
            },
            **(rtype_mappings or {}),
        )

    @classmethod
    def index_doc(
        cls,
        content: ContentBase,
        *,
        native: bool = True,
    ) -> dict[str, Any]:
        """
        Returns the content for the ES index document for this type of resource content
        """
        return dict(
            native=native,
            comment=" ".join([cmt["comment"] for cmt in content.comments])
            if content.comments
            else "" or None,
            **(cls._rtype_index_doc(content) or {}),
        )

    @classmethod
    def es_queries(
        cls,
        *,
        query: "ResourceSearchQuery",
        strict: bool = False,
    ) -> list[dict[str, Any]]:
        es_queries = []
        strict_suffix = ".strict" if strict else ""
        res_id_str = str(query.common.resource_id)
        if query.common.comment:
            cmt_field = f"resources.{res_id_str}.comment{strict_suffix}"
            if query.common.comment.strip() == "*":
                # we construct a match-all regex query to
                # force highlighting on the entire field value
                es_queries.append({"regexp": {f"{cmt_field}": r"[\s\S]*"}})
            elif query.common.comment.strip():
                es_queries.append(
                    {
                        "simple_query_string": {
                            "fields": [cmt_field],
                            "query": query.common.comment,
                            "analyze_wildcard": True,
                        }
                    }
                )
        return [
            *es_queries,
            *(cls.rtype_es_queries(query=query, strict=strict) or []),
            # ensure we only find locations that
            # the target resource potentially has data for
            {"exists": {"field": f"resources.{res_id_str}"}},
        ]

    @classmethod
    def get_res_import_readme_obj(cls) -> dict:
        """Returns the "README" object for import data for this resource type"""
        content_schema = jsonref.replace_refs(
            cls.content_model().create_model().model_json_schema(),
            proxies=False,
            lazy_load=False,
        )
        schema_excludes = camelize(["id", "resource_id", "resource_type"])
        return {
            "__README": " ".join(IMPORT_README_TXT.splitlines()).strip(),
            "_contentSchema": {
                "properties": {
                    k: v
                    for k, v in content_schema.get("properties", {}).items()
                    if k not in schema_excludes
                },
                "required": [
                    k
                    for k in content_schema.get("required", [])
                    if k not in schema_excludes
                ],
            },
        }

    @classmethod
    async def export_tekst_jsonl(
        cls,
        *,
        resource: ResourceBaseDocument,
        content_ids: list[PydanticObjectId],
        file_path: Path,
    ) -> None:
        """
        Exports the given contents of the given resource as JSON lines,
        compatible for re-import in Tekst.
        """
        with open(file_path, "w") as fp:
            # write resource metadata to first line
            res_json = json.dumps(
                camelize(
                    resource.model_dump(
                        mode="json",
                        by_alias=True,
                        exclude_none=True,
                        exclude_unset=True,
                        exclude=RES_EXCLUDE_EXP_IMP,
                    )
                ),
                ensure_ascii=False,
                default=str,
                indent=None,
            )
            fp.write(f"{res_json}\n")
            # write contents to file, line by line
            for i, c_id in enumerate(content_ids):
                content = ensure(
                    await ContentBaseDocument.get(c_id, with_children=True)
                )
                c_json = json.dumps(
                    camelize(
                        content.model_dump(
                            mode="json",
                            by_alias=True,
                            exclude_unset=True,
                            exclude_none=True,
                            exclude=cls._EXCLUDE_FROM_CONTENT_EXPORT_DATA,
                        )
                    ),
                    ensure_ascii=False,
                    default=str,
                    indent=None,
                )
                fp.write(f"{c_json}{'\n' if i < len(content_ids) - 1 else ''}")
        del content_ids

    @classmethod
    async def export_universal_json(
        cls,
        *,
        resource: ResourceBaseDocument,
        content_ids: list[PydanticObjectId],
        file_path: Path,
    ) -> None:
        """
        Exports the given contents of the given resource as JSON, in a form that
        aims to be as comprehensive as possible.
        """
        # prepare (root) resource object
        text = ensure(await TextDocument.get(resource.text_id))
        res = camelize(
            resource.model_dump(
                mode="json",
                include={
                    "id",
                    "title",
                    "subtitle",
                    "level",
                    "citation",
                    "meta",
                    "description",
                },
                exclude_none=True,
                exclude_unset=True,
            )
        )
        res["title"] = {
            title_trans["locale"]: title_trans["translation"]
            for title_trans in res["title"]
        }
        res["subtitle"] = {
            sub_trans["locale"]: sub_trans["translation"]
            for sub_trans in res.get("subtitle", [])
        }
        res["level"] = {
            lvl_trans["locale"]: lvl_trans["translation"]
            for lvl_trans in text.levels[res["level"]]
        }
        res["description"] = {
            description["locale"]: description["translation"]
            for description in res.get("description", [])
        }
        res["meta"] = {meta["key"]: meta["value"] for meta in res["meta"]}

        # construct content objects
        contents: list[dict] = []
        for c_id in content_ids:
            content = ensure(await ContentBaseDocument.get(c_id, with_children=True))
            c_dict = camelize(
                content.model_dump(
                    mode="json",
                    by_alias=True,
                    exclude_unset=True,
                    exclude_none=True,
                    exclude=cls._EXCLUDE_FROM_CONTENT_EXPORT_DATA,
                )
            )
            contents.append(c_dict)
        del content_ids

        # construct labels of all locations on the resource's level
        full_loc_labels = await text.full_location_labels(resource.level)
        for content in contents:
            content["location"] = full_loc_labels.get(str(content["locationId"]))
            del content["locationId"]
        res["contents"] = contents

        with open(file_path, "w") as fp:
            json.dump(
                res,
                fp=fp,
                ensure_ascii=False,
                default=str,
            )

    @classmethod
    def resource_model[T: ResourceBase](cls) -> type[T]:
        """Returns the resource model for this type of resource"""
        raise NotImplementedError(
            "This method must be implemented by subclasses."
        )  # pragma: no cover

    @classmethod
    def content_model(cls) -> type[ContentBase]:
        """Returns the content model for contents of this type of resource"""
        raise NotImplementedError(
            "This method must be implemented by subclasses."
        )  # pragma: no cover

    @classmethod
    def _rtype_index_mappings(
        cls,
        lenient_analyzer: str,
        strict_analyzer: str,
    ) -> dict[str, Any] | None:
        """
        Returns the mappings properties for ES search index
        documents unique for this type of resource content, respecting any resource
        configuration relevant to the resource's index mappings
        """
        raise NotImplementedError(
            "This method must be implemented by subclasses."
        )  # pragma: no cover

    @classmethod
    def _rtype_index_doc(
        cls,
        content: ContentBase,
    ) -> dict[str, Any] | None:
        """
        Returns the content for the ES index document
        for this type of resource content that is unique to this resource type
        """
        raise NotImplementedError(
            "This method must be implemented by subclasses."
        )  # pragma: no cover

    @classmethod
    def rtype_es_queries(
        cls,
        *,
        query: "ResourceSearchQuery",
        strict: bool = False,
    ) -> list[dict[str, Any]] | None:
        """
        Constructs an Elasticsearch search query for each field
        in the given resource search query instance.
        Common content fields are not included in the returned queries.
        """
        raise NotImplementedError(
            "This method must be implemented by subclasses."
        )  # pragma: no cover

    @classmethod
    def highlights_generator(cls) -> Callable[[dict[str, Any]], list[str]] | None:
        """
        For resource types that need a custom highlights generator, this method can be
        overwritten to return a function that takes a list of search hits and returns
        custom highlights for them. If this function returns None (the default if not
        overwritten), the default highlighting will be used.
        """
        return None

    @classmethod
    async def export(
        cls,
        *,
        resource: ResourceBaseDocument,
        content_ids: list[PydanticObjectId],
        export_format: ResourceExportFormat,
        file_path: Path,
    ) -> None:
        """
        Writes export data to the given path.
        Raises ValueError if the export format is not supported by this resource type.
        """
        raise NotImplementedError(
            "This method must be implemented by subclasses."
        )  # pragma: no cover


class ResourceTypesManager:
    __resource_types: dict[str, ResourceTypeBase] = dict()

    def register(
        self,
        resource_type_class: type[ResourceTypeBase],
    ):
        # init resource/content type CRUD models
        resource_type_class.resource_model().create_model()
        resource_type_class.resource_model().read_model()
        resource_type_class.resource_model().update_model()
        resource_type_class.content_model().create_model()
        resource_type_class.content_model().read_model()
        resource_type_class.content_model().update_model()
        # create resource/content document models
        resource_type_class.resource_model().document_model()
        resource_type_class.content_model().document_model()
        # register instance
        self.__resource_types[resource_type_class.get_key()] = resource_type_class()

    def get(self, resource_type_name: str) -> ResourceTypeBase:
        return self.__resource_types[resource_type_name]

    def get_all(self) -> dict[str, ResourceTypeBase]:
        return self.__resource_types

    def list_names(self) -> list[str]:
        return list(self.__resource_types.keys())

    def is_initialized(self) -> bool:
        return len(self.__resource_types) > 0


# global variable to hold resource type manager instance
resource_types_mgr: ResourceTypesManager = ResourceTypesManager()


def init_resource_types_mgr() -> None:
    global resource_types_mgr
    if resource_types_mgr.is_initialized():  # pragma: no cover
        return
    log.info("Registering resource types...")
    # get internal resource type module names
    lt_modules = [mod.name for mod in pkgutil.iter_modules(resource_types.__path__)]
    for lt_module in lt_modules:
        module = importlib.import_module(f"{resource_types.__name__}.{lt_module}")
        res_types_from_module = inspect.getmembers(
            module, lambda o: inspect.isclass(o) and issubclass(o, ResourceTypeBase)
        )
        for res_type_impl in res_types_from_module:
            # exclude ResourceTypeBase class (which is weirdly picked up here)
            if res_type_impl[1] is not ResourceTypeBase:
                res_type_class = res_type_impl[1]
                # register resource type instance with resource type manager
                log.debug(f"Registering resource type: {res_type_class.get_name()}")
                resource_types_mgr.register(res_type_class)


init_resource_types_mgr()
