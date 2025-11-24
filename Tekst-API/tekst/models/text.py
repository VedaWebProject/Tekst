import re

from typing import Annotated

from beanie import PydanticObjectId
from beanie.operators import Eq
from pydantic import (
    ConfigDict,
    Field,
    field_validator,
)
from pydantic_extra_types.color import Color
from typing_extensions import TypedDict

from tekst.i18n import TranslationBase, Translations
from tekst.models.common import (
    DocumentBase,
    ExcludeFromModelVariants,
    ModelBase,
    ModelFactoryMixin,
)
from tekst.models.location import LocationDocument
from tekst.types import ColorSerializer, ConStr, LocationLabel, LocationLevel


class TextSubtitleTranslation(TranslationBase):
    translation: Annotated[
        ConStr(
            max_length=128,
            cleanup="oneline",
        ),
        Field(
            description="Subtitle translation for a text",
        ),
    ]


class TextLevelTranslation(TranslationBase):
    translation: Annotated[
        ConStr(
            max_length=32,
            cleanup="oneline",
        ),
        Field(
            description="Translation of a text level label",
        ),
    ]


class ResourceCategoryTranslation(TranslationBase):
    translation: Annotated[
        ConStr(
            max_length=32,
            cleanup="oneline",
        ),
        Field(
            description="Translation of a resource category",
        ),
    ]


class ResourceCategory(TypedDict):
    key: Annotated[
        ConStr(
            max_length=16,
            cleanup="oneline",
        ),
        Field(
            description="Key identifying this resource category",
        ),
    ]
    translations: Translations[ResourceCategoryTranslation]


TextTitle = Annotated[
    ConStr(
        max_length=64,
        cleanup="oneline",
    ),
    Field(description="Title of this text"),
]

TextSlug = Annotated[
    ConStr(
        max_length=16,
        cleanup="oneline",
        pattern=r"^[a-z0-9]+$",
    ),
    Field(
        description="A short identifier for use in URLs and internal operations",
    ),
]


class Text(ModelBase, ModelFactoryMixin):
    """A text represented in Tekst"""

    title: TextTitle
    slug: TextSlug

    subtitle: Annotated[
        Translations[TextSubtitleTranslation],
        Field(
            description=(
                "Subtitle translations of this text "
                "(if set, it must contain at least one element)"
            ),
        ),
    ] = []

    levels: Annotated[
        list[Translations[TextLevelTranslation]],
        Field(
            description="Structure levels of this text and their label translations",
            min_length=1,
            max_length=32,
        ),
    ]

    default_level: Annotated[
        LocationLevel,
        Field(
            description=(
                "Default structure level for the client to use for browsing this text"
            ),
        ),
    ] = 0

    loc_delim: Annotated[
        ConStr(
            max_length=3,
            strip=False,
            pattern=r"[^\n\r]+",
        ),
        Field(
            description="Delimiter for displaying text locations",
        ),
    ] = ", "

    labeled_location: Annotated[
        bool,
        Field(
            description=(
                "Whether the UI should label the parts of "
                "the browse location with each levels' names"
            ),
        ),
    ] = True

    color: Annotated[
        Color,
        ColorSerializer,
        Field(
            description="Accent color used for this text in the client UI",
        ),
    ] = "#38714B"

    sort_order: Annotated[
        int,
        Field(
            description="Sort order for displaying this resource among others",
            ge=0,
            le=1000,
        ),
    ] = 10

    is_active: Annotated[
        bool,
        Field(
            description=(
                "Whether the text should be listed "
                "for non-admin users in the web client"
            ),
        ),
    ] = False

    resource_categories: Annotated[
        list[ResourceCategory],
        Field(
            description="Resource categories to categorize resources in",
            max_length=32,
        ),
    ] = []

    full_loc_label_as_hit_heading: Annotated[
        bool,
        Field(
            description=(
                "Whether to use the full location label as the hit heading "
                "in the search results"
            ),
        ),
    ] = False

    index_utd: Annotated[
        bool,
        Field(
            description="The search index for this text is up-to-date",
        ),
        ExcludeFromModelVariants(
            update=True,
            create=True,
        ),
    ] = False

    @field_validator("subtitle", mode="after")
    @classmethod
    def validate_subtitle(cls, v) -> Translations[TextSubtitleTranslation] | None:
        for subtitle in v:
            subtitle["translation"] = re.sub(
                r"[\s\n\r]+", " ", subtitle["translation"]
            ).strip()
        return v

    @field_validator("default_level", mode="after")
    @classmethod
    def validate_default_level(cls, v, info, **kwargs):
        # unfortunately we can only validate this if "levels" is present
        # ...and this might not be the case (e.g. for update models)
        if isinstance(info.data.get("levels"), list) and v >= len(
            info.data.get("levels")
        ):
            raise ValueError(
                f"Invalid default level value ({v}). "
                f"This text only has {len(info.data['levels'])} levels."
            )
        return v


class TextDocument(Text, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "texts"
        bson_encoders = {Color: lambda c: c.as_hex()}

    @classmethod
    async def get_active_texts_ids(cls):
        return [
            text.id
            for text in await TextDocument.find(
                Eq(TextDocument.is_active, True)
            ).to_list()
        ]

    async def full_location_labels(
        self,
        target_level: int,
    ) -> dict[str, str]:
        """
        Returns a dict mapping the location ID of each location on the given level to
        the full concatenated location labels for all locations on the
        given target level of this text. Location label parts are delimited
        by the text's location delimiter or ", " if no delimiter is set.
        """
        if target_level is None or target_level < 0 or target_level >= len(self.levels):
            raise ValueError(f"Invalid target level ({target_level}) for this text.")
        loc_delim = self.loc_delim or ", "
        location_labels = {}
        for level in range(target_level + 1):
            location_labels = {
                str(loc["_id"]): loc_delim.join(
                    [
                        lbl
                        for lbl in [
                            location_labels.get(str(loc.get("parent_id"))),
                            loc["label"],
                        ]
                        if lbl
                    ]
                )
                for loc in await LocationDocument.find(
                    LocationDocument.text_id == self.id,
                    LocationDocument.level == level,
                )
                .sort(+LocationDocument.position)
                .aggregate([{"$project": {"_id": 1, "parent_id": 1, "label": 1}}])
                .to_list()
            }
        return location_labels


TextCreate = Text.create_model()
TextRead = Text.read_model()
TextUpdate = Text.update_model()


class InsertLevelRequest(ModelBase):
    translations: Annotated[
        Translations[TextLevelTranslation],
        Field(
            description="Translation(s) for the label of the level to insert",
        ),
    ]


class MoveLocationRequestBody(ModelBase):
    position: int
    after: bool
    parent_id: Annotated[
        PydanticObjectId | None,
        Field(
            alias="parentId",
        ),
    ]


class LocationDefinition(ModelBase):
    label: LocationLabel
    locations: list["LocationDefinition"] | None = None
    aliases: list[str] | None = None


class TextStructureImportData(ModelBase):
    model_config = ConfigDict(extra="allow")
    locations: list[LocationDefinition] = []
