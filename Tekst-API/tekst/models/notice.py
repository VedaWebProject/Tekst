from typing import Annotated

from pydantic import AwareDatetime, Field, StringConstraints

from tekst.i18n import TranslationBase, Translations
from tekst.models.common import (
    CreateBase,
    DocumentBase,
    ModelBase,
    ReadBase,
)
from tekst.types import MultiLineString


class NoticeTranslation(TranslationBase):
    translation: Annotated[
        str, StringConstraints(min_length=1, max_length=100000), MultiLineString
    ]


class Notice(ModelBase):
    html: Annotated[
        Translations[NoticeTranslation],
        Field(
            description="HTML content of this notice, possibly translated",
            min_length=1,
        ),
    ]
    ends_at: Annotated[
        AwareDatetime,
        Field(description="The time this notice will be invalidated at"),
    ]


class NoticeDocument(Notice, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "notices"
        indexes = [["ends_at"]]


class NoticeCreate(Notice, CreateBase):
    pass


class NoticeRead(Notice, ReadBase):
    pass
