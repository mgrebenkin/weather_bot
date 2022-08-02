from typing import NamedTuple


class UserType(NamedTuple):
    id: int
    lat: float
    lon: float
    sending_time: str
