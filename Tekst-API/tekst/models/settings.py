from beanie import PydanticObjectId
from pydantic import Field

from tekst.models.common import DocumentBase, ModelBase, ModelFactoryMixin


class PlatformSettings(ModelBase, ModelFactoryMixin):
    """Settings defining platform behavior configured by admins"""

    default_text_id: PydanticObjectId | None = Field(
        None, description="Default text to load in UI"
    )


class PlatformSettingsDocument(PlatformSettings, DocumentBase):
    class Settings:
        name = "settings"


PlatformSettingsCreate = PlatformSettings.get_create_model()
PlatformSettingsRead = PlatformSettings.get_read_model()
PlatformSettingsUpdate = PlatformSettings.get_update_model()
