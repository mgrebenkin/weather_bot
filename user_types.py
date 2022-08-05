from typing import NamedTuple


class UserType(NamedTuple):
    id: int
    lat: float
    lon: float
    sending_time: str

    def __str__(self):
        return f"""(user: {self.id}, """ \
        f"""location: ({self.lat}, {self.lon}), """ \
        f"""sending time: {self.sending_time})""" 
