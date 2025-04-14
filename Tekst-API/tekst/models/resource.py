import re

from datetime import datetime
from typing import Annotated, Literal

from beanie import PydanticObjectId
from beanie.operators import And, Eq, In, Or
from pydantic import (
    Field,
    field_validator,
)
from typing_extensions import TypedDict

from tekst.i18n import TranslationBase, Translations
from tekst.logs import log, log_op_end, log_op_start
from tekst.models.common import (
    DocumentBase,
    ExcludeFromModelVariants,
    ModelBase,
    ModelFactoryMixin,
)
from tekst.models.location import LocationDocument
from tekst.models.precomputed import PrecomputedDataDocument
from tekst.models.resource_configs import ResourceConfigBase
from tekst.models.text import TextDocument
from tekst.models.user import UserRead, UserReadPublic
from tekst.types import ConStr, ConStrOrNone, ResourceTypeName
from tekst.utils.html import force_html, sanitize_html


# class for one arbitrary metadate
class MetadataEntry(TypedDict):
    key: Annotated[
        ConStr(
            max_length=16,
            cleanup="oneline",
        ),
        Field(
            description="Key identifying this metadata entry",
        ),
    ]
    value: Annotated[
        ConStr(
            max_length=128,
            cleanup="multiline",
        ),
        Field(
            description="Value of this metadata entry",
        ),
    ]


class ResourceTitleTranslation(TranslationBase):
    translation: Annotated[
        ConStr(
            max_length=64,
            cleanup="oneline",
        ),
        Field(
            description="Title translation for this resource",
        ),
    ]


class ResourceSubtitleTranslation(TranslationBase):
    translation: Annotated[
        ConStr(
            max_length=512,
            cleanup="oneline",
        ),
        Field(
            description="Subtitle translation for this resource",
        ),
    ]


class ResourceDescriptionTranslation(TranslationBase):
    translation: Annotated[
        ConStr(
            min_length=1,
            max_length=102400,
            cleanup="multiline",
        ),
        Field(
            description="Description translation HTML for this resource",
        ),
    ]


class ResourceBase(ModelBase, ModelFactoryMixin):
    """A resource describing a set of data on a text"""

    title: Annotated[
        Translations[ResourceTitleTranslation],
        Field(
            description="Title of this resource",
            min_length=1,
        ),
    ]

    subtitle: Annotated[
        Translations[ResourceSubtitleTranslation],
        Field(
            description="Short, concise subtitle of this resource",
        ),
    ] = []

    text_id: Annotated[
        PydanticObjectId,
        Field(
            description="ID of the text this resource belongs to",
        ),
        ExcludeFromModelVariants(
            update=True,
        ),
    ]

    level: Annotated[
        int,
        Field(
            ge=0,
            description="Text level this resource belongs to",
        ),
        ExcludeFromModelVariants(
            update=True,
        ),
    ]

    resource_type: Annotated[
        ResourceTypeName,
        Field(
            description="A string identifying one of the available resource types",
        ),
        ExcludeFromModelVariants(
            update=True,
        ),
    ]

    original_id: Annotated[
        PydanticObjectId | None,
        Field(
            description=(
                "If this is a version of another resource,"
                " this ID references the original"
            ),
        ),
    ] = None

    owner_id: Annotated[
        PydanticObjectId | None,
        Field(
            description="User owning this resource",
        ),
        ExcludeFromModelVariants(
            update=True,
            create=True,
        ),
    ] = None

    shared_read: Annotated[
        list[PydanticObjectId],
        Field(
            description="Users with shared read access to this resource",
            max_length=64,
        ),
        ExcludeFromModelVariants(
            create=True,
        ),
    ] = []

    shared_write: Annotated[
        list[PydanticObjectId],
        Field(
            description="Users with shared write access to this resource",
            max_length=64,
        ),
        ExcludeFromModelVariants(
            create=True,
        ),
    ] = []

    public: Annotated[
        bool,
        Field(
            description="Publication status of this resource",
        ),
        ExcludeFromModelVariants(
            update=True,
            create=True,
        ),
    ] = False

    proposed: Annotated[
        bool,
        Field(
            description="Whether this resource has been proposed for publication",
        ),
        ExcludeFromModelVariants(
            update=True,
            create=True,
        ),
    ] = False

    citation: Annotated[
        ConStrOrNone(
            max_length=4096,
            cleanup="oneline",
        ),
        Field(
            description="Citation details for this resource",
        ),
    ] = None

    meta: Annotated[
        list[MetadataEntry],
        Field(
            description="Arbitrary metadata",
            min_length=0,
            max_length=64,
        ),
    ] = []

    description: Annotated[
        Translations[ResourceDescriptionTranslation],
        Field(
            description=(
                "Plain text, potentially multiline description on this resource"
            ),
        ),
    ] = []

    config: ResourceConfigBase = ResourceConfigBase()

    contents_changed_at: Annotated[
        datetime,
        Field(
            description="The last time contents of this resource changed",
        ),
        ExcludeFromModelVariants(
            update=True,
            create=True,
        ),
    ] = datetime.utcfromtimestamp(86400)

    @field_validator("subtitle", mode="after")
    @classmethod
    def handle_whitespaces_in_subtitle(cls, v):
        for desc_trans in v:
            desc_trans["translation"] = re.sub(
                r"[\s\n\r]+", " ", desc_trans["translation"]
            ).strip()
        return v

    @field_validator(
        "resource_type",
        mode="after",
        check_fields=False,
    )
    @classmethod
    def validate_resource_type_name(cls, v):
        from tekst.resources import resource_types_mgr

        resource_type_names = resource_types_mgr.list_names()
        if v not in resource_type_names:
            raise ValueError(
                f"Given resource type ({v}) is not a valid "
                f"resource type name (one of {resource_type_names})."
            )
        return v

    @field_validator("description", mode="after")
    @classmethod
    def sanitize_description(cls, v):
        for translation in v:
            translation["translation"] = sanitize_html(
                force_html(translation["translation"])
            )
        return v

    def restricted_fields(self, user: UserRead | None = None) -> set[str] | None:
        restrict_shares_info = user is None or (
            user.id != self.owner_id and not user.is_superuser
        )
        restrictions: dict[str, bool] = {
            "shared_read": restrict_shares_info,
            "shared_write": restrict_shares_info,
        }
        return {k for k, v in restrictions.items() if v}

    @classmethod
    def quick_search_fields(cls) -> list[str]:
        """
        Should return a list of search index fields that can be searched via
        quick search. By default, it returns an empty list. This is supposed to be
        overridden by concrete resource implementations.
        """
        return []  # pragma: no cover

    async def contents_changed_hook(self) -> None:
        """
        Will be called whenever contents of a given resource are changed.
        This may be overridden by concrete resource implementations to do whatever
        is necessary to react to content changes. Overriding implementations MUST
        call `await super().contents_changed_hook()`!
        """
        self.contents_changed_at = datetime.utcnow()
        await self.replace()

    async def resource_precompute_hook(self) -> None:
        """
        Will be called whenever the central resource precompute procedures are run.
        This may be overridden by concrete resource implementations to run arbitrary
        data precomputation procedures. Overriding implementations MUST
        call `await super().resource_precompute_hook()`!
        """
        op_id = log_op_start(f"Precompute coverage data for resource {self.id}")
        try:
            await self.__precompute_coverage_data()
        except Exception as e:  # pragma: no cover
            log_op_end(op_id, failed=True)
            raise e
        log_op_end(op_id)

    async def __precompute_coverage_data(self) -> None:
        # get precomputed resource coverage data
        precomp_doc = await PrecomputedDataDocument.find_one(
            PrecomputedDataDocument.ref_id == self.id,
            PrecomputedDataDocument.precomputed_type == "coverage",
        )
        if precomp_doc:
            if precomp_doc.created_at > self.contents_changed_at:
                log.debug(
                    f"Coverage data for resource {str(self.id)} up-to-date. Skipping."
                )
                return
        else:
            # create new coverage data document
            precomp_doc = PrecomputedDataDocument(
                ref_id=self.id,
                precomputed_type="coverage",
            )

        data: list[dict] = (
            await LocationDocument.find(
                LocationDocument.text_id == self.text_id,
                LocationDocument.level == self.level,
            )
            .sort(+LocationDocument.position)
            .aggregate(
                [
                    {
                        "$lookup": {
                            "from": "contents",
                            "localField": "_id",
                            "foreignField": "location_id",
                            "let": {"location_id": "$_id", "resource_id": self.id},
                            "pipeline": [
                                {
                                    "$match": {
                                        "$expr": {
                                            "$and": [
                                                {
                                                    "$eq": [
                                                        "$location_id",
                                                        "$$location_id",
                                                    ]
                                                },
                                                {
                                                    "$eq": [
                                                        "$resource_id",
                                                        "$$resource_id",
                                                    ]
                                                },
                                            ]
                                        }
                                    }
                                },
                                {"$project": {"_id": 1}},
                            ],
                            "as": "contents",
                        }
                    },
                    {
                        "$project": {
                            "id": "$_id",
                            "label": 1,
                            "position": 1,
                            "parent_id": 1,
                            "covered": {"$gt": [{"$size": "$contents"}, 0]},
                        }
                    },
                ],
            )
            .to_list()
        )

        text_doc: TextDocument = await TextDocument.get(self.text_id)
        # get all resource level location labels
        location_labels = await text_doc.full_location_labels(self.level)
        # get all parent level location labels
        parent_location_labels = await text_doc.full_location_labels(
            max(self.level - 1, 0)
        )

        # generate coverage details data
        coverage_per_parent = {}
        covered_locations_count = 0
        for location in data:
            loc_id = str(location["id"])
            parent_id = str(location["parent_id"])
            if parent_id not in coverage_per_parent:
                coverage_per_parent[parent_id] = []
            coverage_per_parent[parent_id].append(
                {
                    "loc_id": loc_id,
                    "label": location_labels[loc_id],
                    "covered": location["covered"],
                }
            )
            covered_locations_count += 1 if location["covered"] else 0
        details = [
            {"label": parent_location_labels.get(p_id), "locations": loc_cov}
            for p_id, loc_cov in coverage_per_parent.items()
        ]

        # generate coverage ranges data
        ranges = []
        curr_range: dict[str, str | bool] | None = None
        for location in data:
            if curr_range and curr_range.get("covered") != location["covered"]:
                # there is a range, but it's complete, so we add it to the ranges
                ranges.append(curr_range)
                curr_range = None
            if curr_range is None:
                # no current range, start a new one
                curr_range = {
                    "start": location_labels[str(location["id"])],
                    "end": location_labels[str(location["id"])],
                    "covered": location["covered"],
                }
            else:
                # there is a current range, coverage matches, so we extend it
                curr_range["end"] = location_labels[str(location["id"])]
        if curr_range:
            # append the last remaining coverage range
            ranges.append(curr_range)
        covered_count = len([r for r in ranges if r.get("covered")])
        missing_count = len(ranges) - covered_count
        use_covered_ranges = (
            covered_count == len(ranges) or covered_count <= missing_count
        )
        ranges = [
            [r.get("start"), r.get("end")]
            for r in ranges
            if r.get("covered") == use_covered_ranges
        ]

        precomp_doc.data = ResourceCoverage(
            covered=covered_locations_count,
            total=len(data),
            ranges=ranges,
            ranges_covered=use_covered_ranges,
            details=details,
        ).model_dump()

        precomp_doc.created_at = datetime.utcnow()
        await precomp_doc.save()


# generate document and update models for this base model,
# as those have to be used as bases for inheriting model's document/update models


class ResourceBaseDocument(ResourceBase, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "resources"
        is_root = True
        indexes = [
            "text_id",
            "level",
            "resource_type",
            "owner_id",
        ]

    @classmethod
    async def access_conditions_read(cls, user: UserRead | None) -> dict:
        active_texts_ids = await TextDocument.get_active_texts_ids()
        # compose access condition for different user types
        if not user:
            # not logged in, no user
            return And(
                ResourceBaseDocument.public == True,  # noqa: E712
                In(ResourceBaseDocument.text_id, active_texts_ids),
            )
        elif user.is_superuser:
            # superusers can read all resources
            return {}
        else:
            # logged in as regular user
            return And(
                In(ResourceBaseDocument.text_id, active_texts_ids),
                Or(
                    ResourceBaseDocument.owner_id == user.id,
                    Or(
                        ResourceBaseDocument.public == True,  # noqa: E712
                        ResourceBaseDocument.proposed == True,  # noqa: E712
                        ResourceBaseDocument.shared_read == user.id,
                        ResourceBaseDocument.shared_write == user.id,
                    ),
                ),
            )

    @classmethod
    async def access_conditions_write(cls, user: UserRead | None) -> dict:
        if not user:  # pragma: no cover (as this should never happen anyway)
            # not logged in, no user (don't match anything!)
            return Eq(ResourceBaseDocument.public, "THIS_WONT_MATCH")

        if user.is_superuser:
            # superusers can write all resources
            return {}

        active_texts_ids = await TextDocument.get_active_texts_ids()

        # compose conditions for logged in, regular users
        return And(
            In(ResourceBaseDocument.text_id, active_texts_ids),
            ResourceBaseDocument.public == False,  # noqa: E712
            ResourceBaseDocument.proposed == False,  # noqa: E712
            Or(
                ResourceBaseDocument.owner_id == user.id,
                ResourceBaseDocument.shared_write == user.id,
            ),
        )

    @classmethod
    async def user_resource_count(cls, user_id: PydanticObjectId | None) -> int:
        if not user_id:
            return 0  # pragma: no cover
        return await ResourceBaseDocument.find(
            ResourceBaseDocument.owner_id == user_id,
            with_children=True,
        ).count()


class ResourceReadExtras(ModelBase):
    writable: Annotated[
        bool | None,
        Field(
            description="Whether this resource is writable for the requesting user",
        ),
    ] = None
    owner: Annotated[
        UserReadPublic | None,
        Field(
            description="Public user data for user owning this resource",
        ),
    ] = None
    shared_read_users: Annotated[
        list[UserReadPublic] | None,
        Field(
            description="Public user data for users allowed to read this resource",
        ),
    ] = None
    shared_write_users: Annotated[
        list[UserReadPublic] | None,
        Field(
            description="Public user data for users allowed to write this resource",
        ),
    ] = None


ResourceBaseUpdate = ResourceBase.update_model()


class LocationCoverage(ModelBase):
    loc_id: str
    label: str
    covered: bool = False


class ParentCoverage(ModelBase):
    label: str | None
    locations: list[LocationCoverage]


class ResourceCoverage(ModelBase):
    covered: int
    total: int
    ranges: list[list[str]]
    ranges_covered: bool
    details: list[ParentCoverage]


ResourceExportFormat = Literal["json", "tekst-json", "csv"]

res_exp_fmt_info = {
    "json": {
        "extension": "json",
        "mimetype": "application/json",
    },
    "tekst-json": {
        "extension": "json",
        "mimetype": "application/json",
    },
    "csv": {
        "extension": "csv",
        "mimetype": "text/csv",
    },
    "txt": {
        "extension": "txt",
        "mimetype": "text/plain",
    },
    "html": {
        "extension": "html",
        "mimetype": "text/html",
    },
}
