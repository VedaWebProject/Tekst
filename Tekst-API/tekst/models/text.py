import re

from datetime import datetime
from typing import Annotated

from beanie import PydanticObjectId
from pydantic import (
    ConfigDict,
    Field,
    PlainSerializer,
    StringConstraints,
    field_validator,
)
from pydantic_extra_types.color import Color
from typing_extensions import TypedDict

from tekst.models.common import (
    DocumentBase,
    ModelBase,
    ModelFactoryMixin,
    TranslationBase,
    Translations,
)
from tekst.models.location import LocationDocument


class TextSubtitleTranslation(TranslationBase):
    translation: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=128,
            strip_whitespace=True,
        ),
    ]


class TextLevelTranslation(TranslationBase):
    translation: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=32,
            strip_whitespace=True,
        ),
    ]


class ResourceCategoryTranslation(TranslationBase):
    translation: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=32,
            strip_whitespace=True,
        ),
    ]


class ResourceCategory(TypedDict):
    key: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=16,
            strip_whitespace=True,
        ),
    ]
    translations: Translations[ResourceCategoryTranslation]


class Text(ModelBase, ModelFactoryMixin):
    """A text represented in Tekst"""

    title: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=64,
            strip_whitespace=True,
        ),
        Field(description="Title of this text"),
    ]

    slug: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=16,
            strip_whitespace=True,
            pattern=r"^[a-z0-9]+$",
        ),
        Field(
            description="A short identifier for use in URLs and internal operations",
        ),
    ]

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
        int,
        Field(
            ge=0,
            description=(
                "Default structure level for the client "
                "to use for browsing this text"
            ),
        ),
    ] = 0

    loc_delim: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=3,
            strip_whitespace=False,
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

    accent_color: Annotated[
        Color,
        PlainSerializer(
            lambda c: c.as_hex() if isinstance(c, Color) else str(c),
            return_type=str,
            when_used="unless-none",
        ),
        Field(
            description="Accent color used for this text in the client UI",
        ),
    ] = "#305D97"

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

    contents_changed_at: Annotated[
        datetime | None,
        Field(
            description="The last time contents of any resource on this text changed",
        ),
    ] = None

    index_name: Annotated[
        str | None,
        Field(
            description="The name of the search index for this text",
        ),
    ] = None

    index_created_at: Annotated[
        datetime | None,
        Field(
            description="The time the search index for this text was created/updated",
        ),
    ] = None

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
                TextDocument.is_active == True  # noqa: E712
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
            raise AttributeError(
                f"Invalid target level ({target_level}) for this text."
            )
        loc_delim = self.loc_delim or ", "
        location_labels = {}
        for level in range(target_level + 1):
            location_labels = {
                str(loc.id): loc_delim.join(
                    [
                        lbl
                        for lbl in [location_labels.get(str(loc.parent_id)), loc.label]
                        if lbl
                    ]
                )
                for loc in await LocationDocument.find(
                    LocationDocument.text_id == self.id,
                    LocationDocument.level == level,
                )
                .sort(+LocationDocument.position)
                .to_list()
            }
        return location_labels

    async def contents_changed_hook(self):
        """Updates the last contents modification time"""
        self.contents_changed_at = datetime.utcnow()
        await self.replace()

    async def index_updated_hook(self, index_name: str):
        """Updates the last index update time"""
        self.index_name = index_name
        self.index_created_at = datetime.utcnow()
        await self.replace()


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
    label: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=256,
            strip_whitespace=True,
        ),
    ]
    locations: list["LocationDefinition"] | None = None
    aliases: list[str] | None = None


class TextStructureImportData(ModelBase):
    model_config = ConfigDict(extra="allow")
    locations: list[LocationDefinition] = []
