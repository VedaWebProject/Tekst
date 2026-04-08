from typing import Annotated

from fastapi import Body
from pydantic import Field

from tekst.models.content import (
    MissingContent,
)
from tekst.resources.api_call import (
    ApiCallContentCreate,
    ApiCallContentDocument,
    ApiCallContentRead,
    ApiCallContentUpdate,
    ApiCallResourceCreate,
    ApiCallResourceRead,
    ApiCallResourceUpdate,
)
from tekst.resources.audio import (
    AudioContentCreate,
    AudioContentDocument,
    AudioContentRead,
    AudioContentUpdate,
    AudioResourceCreate,
    AudioResourceRead,
    AudioResourceUpdate,
)
from tekst.resources.external_references import (
    ExternalReferencesContentCreate,
    ExternalReferencesContentDocument,
    ExternalReferencesContentRead,
    ExternalReferencesContentUpdate,
    ExternalReferencesResourceCreate,
    ExternalReferencesResourceRead,
    ExternalReferencesResourceUpdate,
)
from tekst.resources.images import (
    ImagesContentCreate,
    ImagesContentDocument,
    ImagesContentRead,
    ImagesContentUpdate,
    ImagesResourceCreate,
    ImagesResourceRead,
    ImagesResourceUpdate,
)
from tekst.resources.location_metadata import (
    LocationMetadataContentCreate,
    LocationMetadataContentDocument,
    LocationMetadataContentRead,
    LocationMetadataContentUpdate,
    LocationMetadataResourceCreate,
    LocationMetadataResourceRead,
    LocationMetadataResourceUpdate,
)
from tekst.resources.plain_text import (
    PlainTextContentCreate,
    PlainTextContentDocument,
    PlainTextContentRead,
    PlainTextContentUpdate,
    PlainTextResourceCreate,
    PlainTextResourceRead,
    PlainTextResourceUpdate,
)
from tekst.resources.rich_text import (
    RichTextContentCreate,
    RichTextContentDocument,
    RichTextContentRead,
    RichTextContentUpdate,
    RichTextResourceCreate,
    RichTextResourceRead,
    RichTextResourceUpdate,
)
from tekst.resources.text_annotation import (
    TextAnnotationContentCreate,
    TextAnnotationContentDocument,
    TextAnnotationContentRead,
    TextAnnotationContentUpdate,
    TextAnnotationResourceCreate,
    TextAnnotationResourceRead,
    TextAnnotationResourceUpdate,
)


# ### create union type aliases for models of any resource type model

AnyResourceCreate = Annotated[
    ApiCallResourceCreate
    | AudioResourceCreate
    | ExternalReferencesResourceCreate
    | ImagesResourceCreate
    | LocationMetadataResourceCreate
    | PlainTextResourceCreate
    | RichTextResourceCreate
    | TextAnnotationResourceCreate,
    Body(discriminator="resource_type"),
    Field(discriminator="resource_type"),
]

AnyResourceRead = Annotated[
    ApiCallResourceRead
    | AudioResourceRead
    | ExternalReferencesResourceRead
    | ImagesResourceRead
    | LocationMetadataResourceRead
    | PlainTextResourceRead
    | RichTextResourceRead
    | TextAnnotationResourceRead,
    Body(discriminator="resource_type"),
    Field(discriminator="resource_type"),
]

AnyResourceUpdate = Annotated[
    ApiCallResourceUpdate
    | AudioResourceUpdate
    | ExternalReferencesResourceUpdate
    | ImagesResourceUpdate
    | LocationMetadataResourceUpdate
    | PlainTextResourceUpdate
    | RichTextResourceUpdate
    | TextAnnotationResourceUpdate,
    Body(discriminator="resource_type"),
    Field(discriminator="resource_type"),
]


# ### CREATE UNION TYPE ALIASES FOR MODELS OF ANY CONTENT TYPE MODEL

AnyContentCreate = Annotated[
    ApiCallContentCreate
    | AudioContentCreate
    | ExternalReferencesContentCreate
    | ImagesContentCreate
    | LocationMetadataContentCreate
    | PlainTextContentCreate
    | RichTextContentCreate
    | TextAnnotationContentCreate,
    Body(discriminator="resource_type"),
    Field(discriminator="resource_type"),
]

AnyContentRead = Annotated[
    ApiCallContentRead
    | AudioContentRead
    | ExternalReferencesContentRead
    | ImagesContentRead
    | LocationMetadataContentRead
    | PlainTextContentRead
    | RichTextContentRead
    | TextAnnotationContentRead,
    Body(discriminator="resource_type"),
    Field(discriminator="resource_type"),
]

AnyContentReadOrMissing = Annotated[
    ApiCallContentRead
    | AudioContentRead
    | ExternalReferencesContentRead
    | ImagesContentRead
    | LocationMetadataContentRead
    | PlainTextContentRead
    | RichTextContentRead
    | TextAnnotationContentRead
    | MissingContent,
    Body(discriminator="resource_type"),
    Field(discriminator="resource_type"),
]

AnyContentUpdate = Annotated[
    ApiCallContentUpdate
    | AudioContentUpdate
    | ExternalReferencesContentUpdate
    | ImagesContentUpdate
    | LocationMetadataContentUpdate
    | PlainTextContentUpdate
    | RichTextContentUpdate
    | TextAnnotationContentUpdate,
    Body(discriminator="resource_type"),
    Field(discriminator="resource_type"),
]

AnyContentDocument = Annotated[
    ApiCallContentDocument
    | AudioContentDocument
    | ExternalReferencesContentDocument
    | ImagesContentDocument
    | LocationMetadataContentDocument
    | PlainTextContentDocument
    | RichTextContentDocument
    | TextAnnotationContentDocument,
    Body(discriminator="resource_type"),
    Field(discriminator="resource_type"),
]
