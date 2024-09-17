from tekst.models.common import ModelBase
from tekst.models.location import LocationRead
from tekst.resources import AnyContentReadBody


class LocationData(ModelBase):
    location_path: list[LocationRead] = []
    contents: list[AnyContentReadBody] = []
