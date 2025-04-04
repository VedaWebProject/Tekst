from re import Pattern
from typing import Annotated, Literal, TypeAlias

from pydantic import BeforeValidator, Field, StringConstraints, conint, constr
from pydantic.functional_validators import AfterValidator
from typing_extensions import TypeAliasType, TypedDict

from tekst.utils.strings import cleanup_spaces_multiline, cleanup_spaces_oneline


# These FieldInfo instances are to be used as type annotation metadata for fields
# that should be marked as optional in the JSON schema. By default, any field
# with a default value is "optional", but the generator we use to generate the
# TypeScript types for the client is configured to transform fields with default
# values as required to make working with response models easier. In turn, we have to
# explicitly mark optional fields (especially for request models) as optinal in some way
# for the generator to understand which fields to treat as optional/nullable.
SchemaOptionalNullable = Field(json_schema_extra={"optionalNullable": True})
SchemaOptionalNonNullable = Field(json_schema_extra={"optionalNullable": False})


# validators for internal use

_CleanupOneline = AfterValidator(cleanup_spaces_oneline)
_CleanupMultiline = AfterValidator(cleanup_spaces_multiline)


# GENERAL TYPES


def _empty_str_to_none(v: str | None) -> None:
    if v is None:
        return None
    if isinstance(v, str) and v.strip() == "":
        return None
    raise ValueError("Value is not an empty string nor None")


_EmptyStrToNone: TypeAlias = Annotated[None, BeforeValidator(_empty_str_to_none)]


def ConStr(  # noqa: N802
    min_length: int = 1,
    max_length: int | None = None,
    strip: bool = True,
    cleanup: Literal["oneline", "multiline"] | None = None,
    pattern: str | Pattern[str] | None = None,
) -> TypeAlias:
    annotations = (
        str,
        StringConstraints(
            min_length=min_length,
            max_length=max_length,
            strip_whitespace=strip,
            pattern=pattern,
        ),
        _CleanupOneline if cleanup == "oneline" else None,
        _CleanupMultiline if cleanup == "multiline" else None,
    )
    annotations = tuple([a for a in annotations if a is not None])
    return Annotated[annotations]


def ConStrOrNone(  # noqa: N802
    min_length: int = 1,
    max_length: int | None = None,
    strip: bool = True,
    cleanup: Literal["oneline", "multiline"] | None = None,
    pattern: str | Pattern[str] | None = None,
) -> TypeAlias:
    return _EmptyStrToNone | ConStr(
        min_length=min_length,
        max_length=max_length,
        strip=strip,
        cleanup=cleanup,
        pattern=pattern,
    )


HttpUrl = ConStr(
    min_length=1,
    max_length=2083,
    cleanup="oneline",
)
HttpUrlOrNone = _EmptyStrToNone | HttpUrl


# LOCATION-SPECIFIC PROPERTY TYPES

LocationLevel = conint(
    ge=0,
    le=32,
)

LocationPosition = conint(
    ge=0,
)

LocationLabel = ConStr(
    max_length=256,
    cleanup="oneline",
)

LocationAlias = constr(
    min_length=1,
    max_length=32,
    strip_whitespace=True,
)


# RESOURCE-SPECIFIC PROPERTY TYPES

ResourceTypeName = constr(
    min_length=1,
    max_length=32,
    strip_whitespace=True,
)


# TYPE ANNOTATIONS FOR FIELD THAT CAN BE PART OF
# THE GENERAL TYPE-SPECIFIC RESOURCE CONFIGURATION

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
    ConStr(
        max_length=32,
        cleanup="oneline",
    ),
    Field(
        description="Name of a font family",
    ),
]

FontFamilyValueOrNone = Annotated[
    ConStrOrNone(
        max_length=32,
        cleanup="oneline",
    ),
    Field(
        description="Name of a font family",
    ),
]


class ContentCssProperty(TypedDict):
    prop: Annotated[
        ConStr(
            max_length=256,
            cleanup="oneline",
        ),
        Field(
            description="A CSS property name",
        ),
    ]
    value: Annotated[
        ConStr(
            max_length=256,
            cleanup="oneline",
        ),
        Field(
            description="A CSS property value",
        ),
    ]


ContentCssProperties = TypeAliasType(
    "ContentCssProperties",
    Annotated[
        list[ContentCssProperty],
        Field(
            description=(
                "List of CSS properties to apply to the contents of this resource"
            ),
            min_length=0,
            max_length=64,
        ),
    ],
)


class SearchReplacement(TypedDict):
    pattern: Annotated[
        ConStr(
            max_length=64,
            cleanup="oneline",
        ),
        Field(
            description="Regular expression to match (Java RegEx syntax)",
        ),
    ]
    replacement: Annotated[
        ConStr(
            min_length=0,
            max_length=64,
            cleanup="oneline",
        ),
        Field(
            description="Replacement string",
        ),
    ]


SearchReplacements = TypeAliasType(
    "SearchReplacements",
    Annotated[
        list[SearchReplacement],
        Field(
            description=(
                "List of regular expression replacements "
                "to apply to search index documents"
            ),
            min_length=0,
            max_length=16,
        ),
    ],
)


# ANNOTATIONS FOR MODIFYING MODEL VARIANTS


class ExcludeFromModelVariants:
    """
    Class to be used as type annotation metadata for fields that
    should not be included in certain model types
    """

    def __init__(
        self,
        *,
        create: bool = False,
        update: bool = False,
    ):
        self.create = create
        self.update = update
