from tekst.models.common import ModelBase


class IndexInfoResponse(ModelBase):
    documents: int
    size: str
    searches: int
