from typing import Annotated

from annotated_types import BaseMetadata
from pydantic import (
    BeforeValidator,
    Field,
    PlainSerializer,
    StringConstraints,
)
from pydantic.dataclasses import dataclass as pydantic_dataclass
from pydantic.functional_validators import AfterValidator
from typing_extensions import TypedDict

from tekst.utils.strings import cleanup_spaces_multiline, cleanup_spaces_oneline


### ANNOTATIONS
### (validators and other type annotations like field info etc.)

# These FieldInfo instances are to be used as type annotation metadata for fields
# that should be marked as optional in the JSON schema. By default, any field
# with a default value is "optional", but the generator we use to generate the
# TypeScript types for the client is configured to transform fields with default
# values as required to make working with response models easier. In turn, we have to
# explicitly mark optional fields (especially for request models) as optinal in some way
# for the generator to understand which fields to treat as optional/nullable.
SchemaOptionalNullable = Field(json_schema_extra={"optionalNullable": True})
SchemaOptionalNonNullable = Field(json_schema_extra={"optionalNullable": False})

# some extra string-manipulating validators

SingleLineString = AfterValidator(cleanup_spaces_oneline)
MultiLineString = AfterValidator(cleanup_spaces_multiline)
EmptyStrToNone = BeforeValidator(lambda v: v or None if isinstance(v, str) else v)

# serializers

ColorSerializer = PlainSerializer(
    lambda c: c.as_hex() if hasattr(c, "as_hex") else str(c),
    return_type=str,
    when_used="unless-none",
)

# manipulating model variants


@pydantic_dataclass(frozen=True)
class ExcludeFromModelVariants(BaseMetadata):
    """
    Metadata class to be used as type annotation for fields that
    should not be included in certain model types
    """

    create: bool = False
    update: bool = False


### TYPES

HttpUrl = Annotated[
    str,
    StringConstraints(min_length=1, max_length=2083),
    SingleLineString,
]


# location-specific property types

LocationLevel = Annotated[
    int,
    Field(
        ge=0,
        le=32,
        description="Structure level of a location",
    ),
]

LocationPosition = Annotated[
    int,
    Field(
        ge=0,
        description="Position of a location on its structure level",
    ),
]

LocationLabel = Annotated[
    str,
    StringConstraints(
        min_length=1,
        max_length=256,
        strip_whitespace=True,
    ),
    SingleLineString,
]

LocationAlias = Annotated[
    str,
    StringConstraints(
        min_length=1,
        max_length=512,
        strip_whitespace=True,
    ),
    SingleLineString,
]


# resource-specific property types

ResourceTypeName = Annotated[
    str,
    StringConstraints(
        min_length=1,
        max_length=32,
        strip_whitespace=True,
    ),
]


# type annotations for field that can be part of
# the general type-specific resource configuration

CollapsibleContentsConfigValue = Annotated[
    int | None,
    Field(
        description=(
            "Minimum height in pixels from which contents should be collapsible "
            "(unsetting this will disable collapsibility)"
        ),
        ge=100,
        le=800,
    ),
]

FontFamilyValue = Annotated[
    str,
    StringConstraints(
        min_length=1,
        max_length=32,
    ),
    SingleLineString,
    Field(description="Name of a font family"),
]


class ContentCssProperty(TypedDict):
    prop: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=256,
        ),
        SingleLineString,
        Field(description="A CSS property name"),
    ]
    value: Annotated[
        str,
        StringConstraints(min_length=1, max_length=256),
        SingleLineString,
        Field(description="A CSS property value"),
    ]


type ContentCssProperties = Annotated[
    list[ContentCssProperty],
    Field(
        description="List of CSS properties to apply to the contents of this resource",
        max_length=64,
    ),
]


class SearchReplacement(TypedDict):
    pattern: Annotated[
        str,
        StringConstraints(min_length=1, max_length=64),
        SingleLineString,
        Field(description="Regular expression to match (Java RegEx syntax)"),
    ]
    replacement: Annotated[
        str,
        StringConstraints(min_length=1, max_length=64),
        SingleLineString,
        Field(description="Replacement string"),
    ]


type SearchReplacements = Annotated[
    list[SearchReplacement],
    Field(
        description=(
            "List of regular expression replacements to apply to search index documents"
        ),
        max_length=16,
    ),
]
