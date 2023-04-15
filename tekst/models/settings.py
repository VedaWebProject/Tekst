from pydantic import Field

from tekst.models.common import ModelBase, ModelFactory, PyObjectId


class PlatformSettings(ModelBase, ModelFactory):
    """Settings defining platform behavior configured by admins"""

    default_text_id: PyObjectId | None = Field(
        None, description="Default text to load in UI"
    )

    class Settings:
        name = "settings"


PlatformSettingsDocument = PlatformSettings.get_document_model()
PlatformSettingsCreate = PlatformSettings.get_create_model()
PlatformSettingsRead = PlatformSettings.get_read_model()
PlatformSettingsUpdate = PlatformSettings.get_update_model()
