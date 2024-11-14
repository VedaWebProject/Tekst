from tekst.models.common import ModelBase
from tekst.models.location import LocationRead
from tekst.resources import AnyContentRead


class LocationData(ModelBase):
    location_path: list[LocationRead] = []
    contents: list[AnyContentRead] = []
